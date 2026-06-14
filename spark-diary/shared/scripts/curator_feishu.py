#!/usr/bin/env python3
"""Spark Diary Curator - Feishu integration for daily curation"""
import sys, json
sys.path.insert(0, '/Users/lizhenjiang/hermes_workspace/spark-diary/shared/scripts')
from feishu_client import FeishuAPI

BASE_TOKEN = "AtInb8idNaYujwsdXZBcoDCyn6g"
TABLE_IDEAS = "tblBtNgaweUh1aZL"
TABLE_MATERIALS = "tblBtmKRLwZm2yzf"
TODAY = "2026-06-13"
RECORD_ID = "recTEST001"

MATERIAL_PATH = "/Users/lizhenjiang/hermes_workspace/spark-diary/03_materials/2026-06-13_material.md"
VOICE_PATH = "/Users/lizhenjiang/hermes_workspace/spark-diary/03_materials/2026-06-13_voice.md"

BLOCK_TEXT = 2
BLOCK_H1 = 3
BLOCK_H2 = 4
BLOCK_H3 = 5
BLOCK_BULLET = 12
BLOCK_QUOTE = 15
BLOCK_DIVIDER = 22

BLOCK_TYPE_FIELD = {
    2: "text",
    3: "heading1",
    4: "heading2",
    5: "heading3",
    12: "bullet",
    15: "quote",
    22: "divider",
}

def make_children_blocks(filepath):
    """Convert markdown file to Feishu docx children blocks."""
    with open(filepath) as f:
        content = f.read()
    children = []
    for para in content.split('\n\n'):
        para = para.strip()
        if not para:
            continue
        if para.startswith('# '):
            bt, txt = BLOCK_H1, para[2:]
        elif para.startswith('## '):
            bt, txt = BLOCK_H2, para[3:]
        elif para.startswith('### '):
            bt, txt = BLOCK_H3, para[4:]
        elif para.startswith('> '):
            bt, txt = BLOCK_QUOTE, para[2:]
        elif para.startswith('- '):
            bt, txt = BLOCK_BULLET, para[2:]
        elif para.startswith('---'):
            bt, txt = BLOCK_DIVIDER, ''
        else:
            bt, txt = BLOCK_TEXT, para

        field_name = BLOCK_TYPE_FIELD.get(bt, "text")
        if bt == BLOCK_DIVIDER:
            children.append({"block_type": bt, field_name: {}})
        else:
            children.append({
                "block_type": bt,
                field_name: {
                    "elements": [{"text_run": {"content": txt, "text_element_style": {}}}],
                    "style": {}
                }
            })
    return children

def main():
    api = FeishuAPI()
    report = {}

    # Create documents
    d5 = api.create_document("D5 Fusion " + TODAY)
    d5_doc_id = d5.get("document", {}).get("document_id", "")
    d5_url = "https://bytedance.feishu.cn/docx/" + d5_doc_id
    report["d5_doc_id"] = d5_doc_id

    d6 = api.create_document("D6 Voice " + TODAY)
    d6_doc_id = d6.get("document", {}).get("document_id", "")
    d6_url = "https://bytedance.feishu.cn/docx/" + d6_doc_id
    report["d6_doc_id"] = d6_doc_id

    # Append blocks
    if d5_doc_id:
        d5_children = make_children_blocks(MATERIAL_PATH)
        api.create_children_blocks(d5_doc_id, d5_doc_id, d5_children)
        report["d5_blocks"] = len(d5_children)

    if d6_doc_id:
        d6_children = make_children_blocks(VOICE_PATH)
        api.create_children_blocks(d6_doc_id, d6_doc_id, d6_children)
        report["d6_blocks"] = len(d6_children)

    # Update T1
    core_expr = (
        "Inspiration push can use Readwise-style half-life algorithm: "
        "items not reviewed for longer get higher priority."
    )
    ai_summary = (
        "User proposed half-life decay algorithm for inspiration recall priority. "
        "AI extended: connects to Ebbinghaus forgetting curve, formalizes P=f(delta_t,H). "
        "Open questions: half-life parameter tuning, gem vs fragment weighting, "
        "decay curve differentiation by inspiration type."
    )
    t1_fields = {
        "Status": "S3_CURATED",
        "Core_Expression": core_expr,
        "AI_Summary": ai_summary,
    }
    if d5_doc_id:
        t1_fields["Material_Doc"] = {"link": d5_url, "text": "Fusion " + TODAY}
    try:
        api.update_record(BASE_TOKEN, TABLE_IDEAS, RECORD_ID, t1_fields)
        report["t1_updated"] = True
    except Exception as e:
        report["t1_error"] = str(e)

    # Write T3
    t3_fields = {
        "Date": TODAY,
        "Idea_Count": 1,
        "Theme_Distribution": "Product x1: half-life recall weight",
        "Mood": "Exploratory",
    }
    if d5_doc_id:
        t3_fields["Material_Doc"] = {"link": d5_url, "text": "Fusion " + TODAY}
    if d6_doc_id:
        t3_fields["Voice_Doc"] = {"link": d6_url, "text": "Voice " + TODAY}
    try:
        api.create_record(BASE_TOKEN, TABLE_MATERIALS, t3_fields)
        report["t3_written"] = True
    except Exception as e:
        report["t3_error"] = str(e)

    report["d5_url"] = d5_url
    report["d6_url"] = d6_url
    return report

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))
