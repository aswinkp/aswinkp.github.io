---
layout:     post
title:      Benchmarking Browser Automation Tools for AI Agents
date:       2026-03-06 17:30:00
summary:    I tested three browser automation tools — agent-browser, Playwright MCP, and Claude in Chrome — to find which is fastest, cheapest on tokens, and most reliable for AI-driven visual debugging.
categories: ai tooling
---

When building [Squad of Agents](https://squadofagents.com), I use Claude Code as my primary development tool. Part of my workflow involves visual debugging — loading pages in a browser, taking screenshots, reading console logs, and inspecting network requests — all driven by the AI agent.

There are three browser automation tools available to Claude Code today:

1. **agent-browser** — a headless CLI tool optimized for AI agents
2. **Playwright MCP** — Playwright wrapped as an MCP server
3. **Claude in Chrome** — a Chrome extension that lets Claude control your real browser

I wanted to know: which is fastest? Which uses the fewest tokens? Which captures the most useful data? So I ran the same task on all three and measured everything.

## The test

The task was simple but representative of real visual debugging:

1. Navigate to `squadofagents.com`
2. Authenticate (set a Django session cookie)
3. Load the `codevantage-bot` team dashboard
4. Take a full-page screenshot
5. Read console logs
6. Read network requests
7. Get an accessibility snapshot of the page

## Results

| Metric | agent-browser | Playwright MCP | Claude in Chrome |
|---|---|---|---|
| **Wall time** | **~9.7s** | ~29.7s | ~40.2s |
| **Tool calls** | **1** | 8 | 8 |
| **Screenshot** | 57KB PNG (file) | 57KB PNG (file + inline) | JPEG (inline only) |
| **Console logs** | Empty | Empty | Empty |
| **Network requests** | Empty | **16 requests captured** | Empty |
| **Accessibility snapshot** | 2KB clean YAML | ~4KB verbose YAML | ~3KB flat list |
| **Token cost (estimate)** | **~50 tokens** | ~3-5K tokens | ~2K tokens |

## Analysis

### Speed: agent-browser wins by 3-4x

agent-browser completes the entire workflow in a single Bash command — no round-trips between the AI model and the tool server. The CLI launches a headless browser, executes all commands sequentially, and returns. Total wall time: **9.7 seconds**.

Playwright MCP and Claude in Chrome both require multiple tool calls, each of which is a round-trip: Claude generates the tool call, the MCP server executes it, the result comes back, Claude processes it and generates the next call. This serialization adds up fast.

### Token efficiency: agent-browser wins dramatically

This is the most important difference for daily use. Every tool call result gets injected into Claude's context window. Playwright MCP returns the **full page accessibility snapshot with every single response** — navigate returns a snapshot, click returns a snapshot, even taking a screenshot returns a snapshot. Each one is 3-5K tokens of YAML.

agent-browser writes everything to files. The only thing that enters the context is a one-line confirmation like `✓ Screenshot saved to /tmp/screenshot.png`. When I need to inspect the output, I read the file — but often I don't need to, because I just wanted the screenshot saved for comparison.

Over a debugging session with 10-20 browser interactions, this difference compounds to **tens of thousands of tokens saved**.

### Data capture: Playwright wins on network requests

All three tools failed to capture console logs retroactively — they all require being set up before the page loads. This is a fundamental limitation.

However, Playwright MCP was the only tool that successfully captured network requests (16 requests including static assets, API calls, and Cloudflare analytics). Both agent-browser and Claude in Chrome returned empty results.

### Auth: Claude in Chrome wins on convenience

Claude in Chrome uses your real Chrome session — if you're already logged in, the agent can just navigate and everything works. No cookie injection needed.

The other two tools run headless browsers with no existing session, so you need to explicitly create and inject a session cookie. For production debugging, this means an extra step to generate a Django session via SSH.

### Reliability

- **agent-browser**: Most reliable. Single command, predictable behavior, no extension dependencies.
- **Playwright MCP**: Reliable but verbose. Works consistently, but the token cost per interaction is high.
- **Claude in Chrome**: Least reliable. Requires the Chrome extension to be connected. In my first attempt during this session, it returned "Browser extension is not connected" — it only worked on the second try, 40 minutes later.

## When to use each

| Scenario | Best tool |
|---|---|
| Quick visual check after a code change | agent-browser |
| Debugging HTMX/API interactions (need network logs) | Playwright MCP |
| Debugging in your real browser with real auth state | Claude in Chrome |
| CI/automated testing | agent-browser or Playwright |
| Long debugging sessions (token budget matters) | agent-browser |

## The takeaway

**agent-browser should be the default for AI-driven visual debugging.** It's 3-4x faster, uses 50-100x fewer tokens, and is the most reliable. Use Playwright MCP when you specifically need network request data, and Claude in Chrome when you need to interact with your real browser session.

The token efficiency difference is the real story here. In a world where context windows are finite and every token counts, a tool that writes results to files instead of injecting them into the conversation is a significant advantage. It's the difference between a debugging session that stays focused and one that runs out of context halfway through.
