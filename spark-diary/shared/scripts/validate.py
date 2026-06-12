#!/usr/bin/env python3
"""
spark-diary 通用文件契约校验器 (validate.py)
============================================

读取 shared/schemas/ 下的 JSON Schema 文件，对 YAML/JSON/MD+frontmatter 文件
做 schema 校验。

用法:
    python validate.py <contract_id> <file_path>

契约映射:
    D1  -> shared/schemas/d1_diary.schema.json   (diary.yaml)
    D2  -> shared/schemas/d2_inbox.schema.json   (00_inbox/*.json)
    D3  -> shared/schemas/d3_idea.schema.json    (01_ideas/*.md)
    D7  -> shared/schemas/d7_sprout.schema.json  (04_sprouts/*.md)
    D8  -> shared/schemas/d8_ledger.schema.json  (ledger.yaml)
    D10 -> shared/schemas/d10_tags.schema.json   (shared/tags.yaml)

依赖:
    pip install jsonschema pyyaml

Python 3.9 兼容.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# ── 项目根目录推导 ─────────────────────────────────────────────
# 当前脚本位于 shared/scripts/validate.py，项目根目录 = ../../

def _find_project_root() -> Path:
    """向上查找包含 diary.yaml 的目录作为项目根目录。"""
    script_dir = Path(__file__).resolve().parent
    for parent in [script_dir.parent.parent, script_dir.parent.parent.parent]:
        if (parent / "diary.yaml").exists():
            return parent
    # 回退：假设标准布局 shared/scripts/ -> root 上两级
    return script_dir.parent.parent


PROJECT_ROOT = _find_project_root()
SCHEMAS_DIR = PROJECT_ROOT / "shared" / "schemas"


# ── 契约 ID → schema 文件映射 ──────────────────────────────────

CONTRACT_SCHEMA_MAP: Dict[str, str] = {
    "D1":  "d1_diary.schema.json",
    "D2":  "d2_inbox.schema.json",
    "D3":  "d3_idea.schema.json",
    "D7":  "d7_sprout.schema.json",
    "D8":  "d8_ledger.schema.json",
    "D10": "d10_tags.schema.json",
}


# ── 文件格式检测 ───────────────────────────────────────────────

def _detect_format(file_path: Path) -> str:
    """检测文件格式: 'yaml', 'json', 'md_frontmatter'."""
    suffix = file_path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        return "yaml"
    if suffix == ".json":
        return "json"
    if suffix == ".md":
        return "md_frontmatter"
    raise ValueError(f"不支持的文件格式: {suffix}")


# ── 解析器 ─────────────────────────────────────────────────────

def _parse_yaml(file_path: Path) -> Dict[str, Any]:
    """解析 YAML 文件，返回 dict。"""
    try:
        import yaml
    except ImportError:
        print("错误: 需要安装 pyyaml 库。请执行: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        raise ValueError(f"YAML 文件为空或格式错误: {file_path}")
    if not isinstance(data, dict):
        raise ValueError(f"YAML 顶层必须是 object/dict，实际为: {type(data).__name__}")
    return data


def _parse_json(file_path: Path) -> Dict[str, Any]:
    """解析 JSON 文件，返回 dict。"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON 顶层必须是 object，实际为: {type(data).__name__}")
    return data


# 提取 Markdown frontmatter 的正则
_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
)


def _parse_md_frontmatter(file_path: Path) -> Dict[str, Any]:
    """从 Markdown 文件中提取 YAML frontmatter，返回 dict。"""
    try:
        import yaml
    except ImportError:
        print("错误: 需要安装 pyyaml 库。请执行: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = _FRONTMATTER_RE.match(content)
    if not match:
        raise ValueError(f"文件缺少 YAML frontmatter (必须以 '---' 开头): {file_path}")

    frontmatter_str = match.group(1)
    data = yaml.safe_load(frontmatter_str)
    if data is None:
        raise ValueError(f"Frontmatter 为空: {file_path}")
    if not isinstance(data, dict):
        raise ValueError(
            f"Frontmatter 顶层必须是 object/dict，实际为: {type(data).__name__}"
        )
    return data


def load_file(file_path: Path) -> Dict[str, Any]:
    """根据文件扩展名选择解析器，返回解析后的 dict。"""
    fmt = _detect_format(file_path)
    if fmt == "yaml":
        return _parse_yaml(file_path)
    elif fmt == "json":
        return _parse_json(file_path)
    elif fmt == "md_frontmatter":
        return _parse_md_frontmatter(file_path)
    else:
        raise ValueError(f"未知格式: {fmt}")


# ── Schema 校验器 ──────────────────────────────────────────────

def load_schema(contract_id: str) -> Dict[str, Any]:
    """根据契约 ID 加载对应的 JSON Schema 文件。"""
    if contract_id.upper() not in CONTRACT_SCHEMA_MAP:
        available = ", ".join(sorted(CONTRACT_SCHEMA_MAP.keys()))
        raise ValueError(
            f"未知的契约 ID: {contract_id}。可用: {available}"
        )

    schema_filename = CONTRACT_SCHEMA_MAP[contract_id.upper()]
    schema_path = SCHEMAS_DIR / schema_filename
    if not schema_path.exists():
        raise FileNotFoundError(
            f"Schema 文件不存在: {schema_path}"
        )

    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_against_schema(
    data: Dict[str, Any], schema: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """使用 jsonschema 库校验数据。

    Returns:
        (is_valid, error_message) — is_valid 为 True 时 error_message 为 None.
    """
    try:
        import jsonschema
    except ImportError:
        print(
            "错误: 需要安装 jsonschema 库。请执行: pip install jsonschema",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e)
    except jsonschema.SchemaError as e:
        return False, f"Schema 自身错误: {e}"


# ── 便利函数：一步校验 ─────────────────────────────────────────

def validate_file(contract_id: str, file_path: Path) -> Tuple[bool, Optional[str]]:
    """一步完成：加载 schema → 解析文件 → 校验。

    Args:
        contract_id: 契约 ID，如 'D1', 'D3'。
        file_path: 待校验文件路径。

    Returns:
        (is_valid, error_message)
    """
    schema = load_schema(contract_id)
    data = load_file(file_path)
    return validate_against_schema(data, schema)


# ── CLI 入口 ────────────────────────────────────────────────────

def main() -> None:
    """命令行入口。"""
    if len(sys.argv) != 3:
        print(
            "用法: python validate.py <contract_id> <file_path>\n"
            "示例: python validate.py D3 01_ideas/IDEA-20260613-01.md\n\n"
            f"可用契约: {', '.join(sorted(CONTRACT_SCHEMA_MAP.keys()))}",
            file=sys.stderr,
        )
        sys.exit(1)

    contract_id = sys.argv[1].upper()
    file_path_str = sys.argv[2]
    file_path = Path(file_path_str)

    if not file_path.exists():
        print(f"错误: 文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        is_valid, error_msg = validate_file(contract_id, file_path)
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"解析错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        sys.exit(1)

    if is_valid:
        print(f"✅ 校验通过: {file_path} 符合 {contract_id} 契约")
        sys.exit(0)
    else:
        print(f"❌ 校验失败: {file_path} 不符合 {contract_id} 契约", file=sys.stderr)
        print(f"   原因: {error_msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
