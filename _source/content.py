"""Read and validate the editable portfolio content."""
from json import loads
from pathlib import Path

CONTENT = Path(__file__).with_name("content.json")
STAGES = ("基础", "系统", "应用", "实验")
CATEGORIES = ("项目", "论文笔记")


def plain(value, label, limit, required=False):
    if not isinstance(value, str) or len(value) > limit or (required and not value.strip()):
        raise ValueError(f"{label}请填写有效文本，最多 {limit} 个字。")
    return value.strip()


def validate(data, course_ids):
    if not isinstance(data, dict):
        raise ValueError("内容必须是一个对象。")
    courses, plan, entries = (data.get(key) for key in ("courses", "plan", "entries"))
    if not isinstance(courses, dict) or not isinstance(plan, dict) or not isinstance(entries, list):
        raise ValueError("课程、课程规划或补充内容的格式无效。")
    clean = {
        "cover_title": plain(data.get("cover_title"), "封面标题", 48, True),
        "signature": plain(data.get("signature"), "封面签名", 140, True),
        "courses": {},
        "plan": {},
        "entries": [],
    }
    for slug, record in courses.items():
        if slug not in course_ids or not isinstance(record, dict):
            raise ValueError("课程编号无效。")
        clean["courses"][slug] = {
            "intro": plain(record.get("intro", ""), "课程简介", 300),
            "task": plain(record.get("task", ""), "自测任务", 300),
            "note": plain(record.get("note", ""), "课程补充笔记", 4000),
        }
    for stage, description in plan.items():
        if stage not in STAGES:
            raise ValueError("课程规划阶段无效。")
        description = plain(description, "阶段目标", 450)
        if description:
            clean["plan"][stage] = description

    if len(entries) > 30:
        raise ValueError("项目和论文笔记最多可添加 30 条。")
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("category") not in CATEGORIES:
            raise ValueError("补充内容的分类无效。")
        clean["entries"].append({
            "category": entry["category"],
            "title": plain(entry.get("title"), "标题", 100, True),
            "body": plain(entry.get("body"), "正文", 5000, True),
        })
    return clean


def read_content(course_ids):
    return validate(loads(CONTENT.read_text(encoding="utf-8")), course_ids)
