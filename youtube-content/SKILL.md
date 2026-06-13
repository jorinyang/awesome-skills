---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

```bash
pip install youtube-transcript-api
```

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Check cache** (optional, recommended for repeated access): if a `youtube-cache/{video_id}/` directory exists from a prior fetch, read `transcript.json` and `metadata.json` directly — skip to Step 4 (transform). This avoids repeated API calls.
2. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
3. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
4. **Cache** the raw data for future re-formatting:
   ```bash
   mkdir -p youtube-cache/{video_id}
   # Save transcript JSON
   python3 SKILL_DIR/scripts/fetch_transcript.py "URL" > youtube-cache/{video_id}/transcript.json
   # Save metadata (title, duration, channel, etc.)
   ```
   Cached data enables fast re-formatting without repeated API calls — useful when the user requests the same video in different formats (summary → blog → thread).
5. **Download cover image** (optional, when user wants thumbnail/cover):
   ```bash
   curl -sSL "https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" -o youtube-cache/{video_id}/cover.jpg
   # Fallback qualities: sddefault, hqdefault, mqdefault, default
   ```
6. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
7. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
8. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Cache Directory Structure

```
youtube-cache/{video_id}/
├── transcript.json    # Raw transcript (JSON with timestamps)
├── metadata.json      # Video metadata (title, duration, channel, description)
└── cover.jpg          # Video thumbnail/cover image (maxresdefault)
```

**Cache benefits:**
- Subsequent requests for the same video avoid API calls entirely
- Switching output formats (summary → blog → thread) is instant
- Preserves data for offline reference
- The `--refresh` flag forces re-fetch ignoring cache

## Error Handling

- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run `pip install youtube-transcript-api` and retry.
