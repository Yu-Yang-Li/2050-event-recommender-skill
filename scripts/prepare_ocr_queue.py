#!/usr/bin/env python3
"""Prepare a priority queue for 2050 WeChat screenshot/OCR extraction."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


CATEGORY_RULES = [
    ("schedule", 100, ["三日", "攻略", "交通", "餐饮", "PASS", "通行证", "指南", "召集流程", "倒计时"]),
    ("ai-agent", 82, ["AI", "Agent", "模型", "数字分身", "人机", "DeskClaw", "灵感", "WaytoAGI"]),
    ("hackathon", 74, ["黑客松", "hackathon", "工具包", "竞速", "共创", "小龙虾", "移动底座"]),
    ("research-tech", 68, ["科学", "医疗", "罕见病", "机器人", "芯片", "量子", "产业"]),
    ("community-life", 56, ["热带雨林", "露营", "晨跑", "百城", "青春舞台", "咖啡", "剧本杀", "旅行", "火车", "团聚"]),
]


def classify(title: str) -> tuple[str, int]:
    best_category = "general"
    best_score = 30
    for category, score, keywords in CATEGORY_RULES:
        hits = sum(1 for keyword in keywords if keyword.lower() in title.lower())
        if hits and score + hits > best_score:
            best_category = category
            best_score = score + hits
    return best_category, best_score


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--out-csv", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    args = parser.parse_args()

    with args.csv.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    enriched = []
    for index, row in enumerate(rows, start=1):
        category, priority = classify(row.get("标题", ""))
        enriched.append(
            {
                "priority": priority,
                "category": category,
                "source_order": index,
                "title": row.get("标题", ""),
                "url": row.get("链接", ""),
                "published_at": row.get("发布时间", ""),
                "capture_status": "pending",
                "ocr_status": "pending",
            }
        )

    enriched.sort(key=lambda item: (-item["priority"], item["source_order"]))
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)

    with args.out_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(enriched[0].keys()))
        writer.writeheader()
        writer.writerows(enriched)

    args.out_json.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"count": len(enriched), "top": enriched[:10]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
