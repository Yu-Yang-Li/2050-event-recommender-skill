# Follow And OCR Workflow

Use this when the user asks to follow 2050 public-account updates, ingest new articles, or refresh the recommendation base.

## Source Path

1. Start from the current article CSV if available.
2. Check the public 2050 WeChat account or a provided article list for new links.
3. For each new link, capture a full-page screenshot before OCR.
4. OCR only after confirming images lazy-loaded correctly.
5. Store source metadata with title, URL, publish time, capture time, and extraction method.

## Screenshot Method

The reference method from `TashanGKD/2050KnowledgeBase`:

- Use Playwright + Chromium.
- Desktop viewport: 1920 x 1080.
- `deviceScaleFactor`: 2.
- Full-page screenshot, no trimming.
- Scroll through the full page to trigger lazy loading.
- Force `img[data-src]` and `img[data-srcset]` into `src` / `srcset`.
- Wait again before screenshot.

The bundled `scripts/capture-wechat.mjs` preserves that approach. Patch paths before running in a new workspace.

## OCR Method

Preferred:

- Use an OCR engine already installed in the environment.
- Keep raw OCR text and a cleaned markdown summary separately.
- Preserve headings, schedule blocks, organizer names, and registration instructions.

Fallback:

- If OCR is unavailable, use screenshot evidence plus manual title-level indexing.
- Say that details beyond the title need article-body extraction.

## Refresh Checklist

- Are there new article titles after 2026-04-21?
- Did any article update pass, traffic, dining, camping, venue, or deadline details?
- Are there new AI-related sessions from WaytoAGI, DeskClaw, Agent, digital twin, AI education, or creator-tool tracks?
- Are there new TopicLab / Tashan activities that should appear in the reserved Tashan section?
- Does a recommendation depend on exact time/location? If yes, verify live before finalizing.
