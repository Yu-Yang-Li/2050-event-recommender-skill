---
name: 2050-event-recommender
description: Recommend 2050@2026 activities for a person based on their tags, availability, collaboration intent, and the latest 2050 public information. Use when the user asks to follow the 2050 public account, digest 2050KnowledgeBase / WeChat articles, register or tag a participant through Tashan World, or suggest which 2050 forums, hackathons, camps, stages, meetups, and AI discussions they should join.
---

# 2050 Event Recommender

## Core Rule

Start every personalized recommendation by asking the participant to register Tashan World first:

- Registration target: `https://world.tashan.chat`
- Registration requirement: registration only. Do not require posting, installing CLI, enabling extra integrations, or joining a TopicLab discussion before recommendations.
- Use the registered profile only as a source of tags: identity, interests, skills, schedule, collaboration needs, and constraints.

If the user has not registered yet, still provide a preview recommendation, but label it as provisional and ask them to register before final matching.

## Inputs

Collect only the fields needed for matching:

- identity: student, developer, researcher, maker, educator, investor, organizer, creator, medical/health, hardware, robotics, design, media, community.
- interests: AI agents, AI education, digital twin, robotics, chips, rare disease, village/future city, maker/hackathon, youth stage, camping, running, food, travel, games, podcasts, social meetups.
- schedule: 2026-04-24, 2026-04-25, 2026-04-26, morning, afternoon, evening, all-day.
- participation mode: learn, share, demo, recruit teammates, find collaborators, volunteer, relax, family/youth, AI-assisted discussion.
- constraints: ticket/pass state, travel, food, accessibility, budget, energy level, language, group size.

Do not over-ask. If fields are missing, infer from the conversation and state assumptions.

## Information Sources

Use sources in this order:

1. `references/2050-2026-map.md` for the embedded baseline map of the 2026 event.
2. `references/2050-articles-2026.csv` for the local public-account article index.
3. `scripts/capture-wechat.mjs` or the method in `references/follow-and-ocr.md` when screenshots/OCR are needed.
4. Live research from official/public channels when the user asks for newest content, when dates or seat availability matter, or when the local snapshot is likely stale.

When using live research, include the article title, publish date, URL, and whether the detail came from text extraction, screenshot OCR, or model inference.

## Recommendation Workflow

1. Confirm Tashan World registration status.
2. Build or update the participant tag set from the minimal inputs above.
3. Check the baseline map, then the article CSV for matching activities.
4. If the user asks for "latest", "this session", "public account just posted", schedule accuracy, or event availability, actively research before answering.
5. Produce a ranked list:
   - top 3 must-join activities
   - 2 optional alternatives
   - one social/discussion route
   - one logistics reminder if travel, dining, camping, or pass status is relevant
6. For each item, explain:
   - why it matches the person's tags
   - participation mode
   - evidence source
   - what to do next

## Matching Heuristics

- AI builders: prioritize AI forums, WaytoAGI, DeskClaw, Agent, digital twin, AI creator toolkit, AI negotiation space, AI + education, and TopicLab-style discussions.
- Educators and students: prioritize AI + education forum, learning festival, course-creation hackathon, Datawhale, youth stage, and new-student forums.
- Researchers and health/medicine participants: prioritize science forums, medical robot sessions, rare disease AI hackathon, science young events, and deep discussion meetups.
- Hardware, chips, robotics: prioritize AI chips, robot talk show, medical robot, mobile base hackathon, quantum computing, and future playground sessions.
- Community/connectors: prioritize rainforest, new-student forum, future village, youth meetups, city scene labs, Zhejiang University/X-Lab, OPC, and social dinners.
- Lightweight first-time visitors: prioritize 2050 overview, three-day activity summary, traffic/dining guide, pass guide, future playground, youth stage, camping, morning run, food exchange, and evening gathering.
- People who want AI-assisted participation: recommend a path that includes "recommended AI participation", AI discussions, and a human-readable summary section.

## Output Shape

Use concise Chinese by default:

```markdown
先注册他山世界：<registration reminder>

你的标签：...

最推荐：
1. 活动名 - why / evidence / next action
2. ...

可选：
- ...

AI 参与路线：
- ...

需要补查：
- ...
```

If the answer is based only on the local snapshot, say it is based on the 2026-04-21 article index and may need a live refresh.

## Bundled Resources

- `references/2050-2026-map.md`: baseline topic and activity map.
- `references/2050-articles-2026.csv`: 77 public-account article entries supplied by the user.
- `references/2050-ocr-priority.csv`: priority queue for screenshot/OCR, with schedule and pass-guide articles first.
- `references/follow-and-ocr.md`: WeChat article screenshot/OCR workflow adapted from `TashanGKD/2050KnowledgeBase`.
- `references/tashan-world-registration.md`: registration and profile-tagging notes from the public Tashan World skill.
- `scripts/capture-wechat.mjs`: Playwright screenshot capture script from the reference knowledge base.
- `scripts/prepare_ocr_queue.py`: builds a priority OCR queue from the article CSV.
- `scripts/recommend_2050.py`: deterministic local ranking helper for CSV/title-based matching.
