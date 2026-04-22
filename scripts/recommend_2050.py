#!/usr/bin/env python3
"""Rank 2050@2026 article-title matches for a lightweight profile."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


TAG_KEYWORDS = {
    "ai": ["AI", "Agent", "模型", "数字分身", "DeskClaw", "灵感交易所", "人机", "智能体"],
    "education": ["教育", "学习节", "课创", "Datawhale", "在家学习", "新生论坛"],
    "research": ["科学", "量子", "芯片", "医疗", "罕见病", "机器人", "科研"],
    "maker": ["黑客松", "hackathon", "小龙虾", "工具包", "竞速", "移动底座"],
    "community": ["热带雨林", "团聚", "邻居", "OPC", "706", "少数派", "浙大", "咖啡"],
    "logistics": ["交通", "餐饮", "PASS", "攻略", "指南", "三日活动", "通行证"],
    "lifestyle": ["露营", "晨跑", "百城味道", "旅行", "火车", "剧本杀", "播客", "青春舞台"],
}


def load_profile(path: Path | None, tags: list[str]) -> dict:
    profile: dict = {"tags": tags}
    if path:
        profile.update(json.loads(path.read_text(encoding="utf-8")))
    normalized = []
    for item in profile.get("tags", []):
        normalized.extend(str(item).lower().replace("，", ",").split(","))
    profile["tags"] = [tag.strip() for tag in normalized if tag.strip()]
    return profile


def score_title(title: str, tags: list[str]) -> tuple[int, list[str]]:
    matched: list[str] = []
    score = 0
    for tag in tags:
        keywords = TAG_KEYWORDS.get(tag, [tag])
        for keyword in keywords:
            if keyword.lower() in title.lower():
                score += 3 if tag in TAG_KEYWORDS else 2
                matched.append(tag)
                break
    if "2050" in title:
        score += 1
    return score, sorted(set(matched))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()

    profile = load_profile(args.profile, args.tag)
    tags = profile.get("tags", [])
    rows = []
    with args.csv.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            title = row.get("标题", "")
            score, matched = score_title(title, tags)
            if score > 0:
                rows.append(
                    {
                        "score": score,
                        "matched_tags": matched,
                        "title": title,
                        "url": row.get("链接", ""),
                        "published_at": row.get("发布时间", ""),
                    }
                )

    rows.sort(key=lambda item: (-item["score"], item["published_at"], item["title"]))
    print(json.dumps(rows[: args.limit], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
