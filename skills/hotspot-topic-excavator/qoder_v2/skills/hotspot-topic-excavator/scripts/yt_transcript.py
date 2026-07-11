#!/usr/bin/env python3
"""
降级路径·YouTube Transcript 获取脚本（Qoder 适配版）

当需要获取播客/视频的逐字稿时，使用本脚本通过 youtube-transcript-api 获取。

用法:
    python3 scripts/yt_transcript.py <video_id_or_url> [--language en] [--format text|json]

示例:
    python3 scripts/yt_transcript.py 6m-ZZBCiiEE
    python3 scripts/yt_transcript.py https://www.youtube.com/watch?v=6m-ZZBCiiEE

输出:
    打印逐字稿到 stdout
    返回码: 0=成功, 1=参数错误, 2=transcript不可用, 3=依赖缺失
"""

import argparse
import re
import sys

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print("ERROR: 缺少 youtube-transcript-api。请执行: pip3 install --user youtube-transcript-api", file=sys.stderr)
    sys.exit(3)


def extract_video_id(input_str):
    """从 URL 或纯 ID 中提取 YouTube video ID"""
    # 纯 video ID (11字符)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', input_str):
        return input_str

    # 标准 YouTube URL
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, input_str)
        if match:
            return match.group(1)

    return None


def fetch_transcript(video_id, language='en', output_format='text'):
    """获取 YouTube 视频的逐字稿"""
    print(f"[YT] Video ID: {video_id}", file=sys.stderr)

    try:
        # 尝试新版 API
        transcript_list = YouTubeTranscriptApi.list(video_id)

        # 查找指定语言的 transcript
        transcript = None
        try:
            transcript = transcript_list.find_transcript([language])
        except Exception:
            # 尝试其他语言
            try:
                transcript = transcript_list.find_generated_transcript([language])
            except Exception:
                # 尝试任意可用语言
                available = list(transcript_list)
                if available:
                    transcript = available[0]
                    print(f"[YT] 未找到 {language} 字幕，使用: {transcript.language}", file=sys.stderr)

        if not transcript:
            print(f"ERROR: 无可用 transcript (语言: {language})", file=sys.stderr)
            sys.exit(2)

        fetched = transcript.fetch()

        print(f"[YT] Transcript 语言: {transcript.language}, 片段数: {len(fetched.snippets)}", file=sys.stderr)

        if output_format == 'json':
            import json
            data = [{
                'text': s.text,
                'start': s.start,
                'duration': s.duration
            } for s in fetched.snippets]
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            # 文本格式：带时间戳
            lines = []
            for snippet in fetched.snippets:
                minutes = int(snippet.start // 60)
                seconds = int(snippet.start % 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                lines.append(f"[{timestamp}] {snippet.text}")
            print('\n'.join(lines))

        print(f"[YT] 完成，总时长约 {int(fetched.snippets[-1].start // 60) if fetched.snippets else 0} 分钟", file=sys.stderr)

    except AttributeError:
        # 旧版 API 兼容
        print("[YT] 使用旧版 API 接口...", file=sys.stderr)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            for entry in transcript:
                minutes = int(entry['start'] // 60)
                seconds = int(entry['start'] % 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                print(f"[{timestamp}] {entry['text']}")
            print(f"[YT] 完成，片段数: {len(transcript)}", file=sys.stderr)
        except Exception as e:
            print(f"ERROR: 旧版 API 也失败 - {e}", file=sys.stderr)
            sys.exit(2)

    except Exception as e:
        print(f"ERROR: 获取 transcript 失败 - {e}", file=sys.stderr)
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(description='YouTube Transcript 获取')
    parser.add_argument('input', help='YouTube video ID 或 URL')
    parser.add_argument('--language', '-l', default='en',
                        help='字幕语言 (默认: en)')
    parser.add_argument('--format', '-f', choices=['text', 'json'], default='text',
                        help='输出格式 (默认: text)')

    args = parser.parse_args()

    video_id = extract_video_id(args.input)
    if not video_id:
        print(f"ERROR: 无法从 '{args.input}' 中提取 video ID", file=sys.stderr)
        sys.exit(1)

    fetch_transcript(video_id, args.language, args.format)


if __name__ == '__main__':
    main()
