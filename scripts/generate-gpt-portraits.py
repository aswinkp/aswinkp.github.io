#!/usr/bin/env python3
"""
Generate AI-created founder portrait variants using OpenAI GPT image generation.

Usage:
  export OPENAI_API_KEY='...'
  python3 scripts/generate-gpt-portraits.py

Inputs:
  static/assets/authoritative-portraits/source-linkedin.jpg
  static/assets/authoritative-portraits/source-slack.jpg

Outputs:
  static/assets/generated-ai-portraits/gpt-portrait-01.png ... gpt-portrait-05.png
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SRC_1 = ROOT / "static/assets/authoritative-portraits/source-linkedin.jpg"
SRC_2 = ROOT / "static/assets/authoritative-portraits/source-slack.jpg"
OUT = ROOT / "static/assets/generated-ai-portraits"
OUT.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("OPENAI_API_KEY is not set. Export it and rerun this script.")

SYSTEM_DIRECTION = """
Use the two attached real reference photos only as identity references for Aswin Kumar.
Do not copy the exact photo, pose, outfit, background, crop, or lighting.
Generate a new original portrait of the same person for a minimal dark personal portfolio website.
The image should make him feel like a credible founder, operator, and thought leader.
Avoid startup/SaaS marketing stock-photo vibes. Avoid fake CEO glamour. Avoid over-retouching.
Keep the person recognizably Indian/South Asian, with natural face structure, beard, hair, and calm presence.
Editorial, high-trust, founder-authority, serious but human.
""".strip()

VARIANTS = [
    (
        "gpt-portrait-01.png",
        "Executive editorial charcoal",
        "Black-and-white editorial portrait, dark charcoal background, black structured blazer over simple open-collar shirt, calm direct eye contact, slight confident smile, waist-up crop, soft directional studio light, minimal founder-authority tone, suitable for a homepage hero on a dark website."
    ),
    (
        "gpt-portrait-02.png",
        "Writer founder at desk",
        "Black-and-white environmental portrait of the same founder seated at a simple wooden desk, laptop and notebook barely visible, dark quiet office/study background, thoughtful half-smile, rolled-up sleeves with refined casual blazer, cinematic but restrained, intellectual operator energy."
    ),
    (
        "gpt-portrait-03.png",
        "Public thinker profile",
        "High-contrast monochrome three-quarter profile portrait, same face, looking slightly off-camera as if thinking before speaking, dark turtleneck or minimal black shirt, plain textured gray backdrop, magazine profile style, authoritative thought leader, not corporate."
    ),
    (
        "gpt-portrait-04.png",
        "Founder in motion",
        "Black-and-white candid editorial portrait of the same founder walking through a minimal workspace corridor, subtle motion, confident posture, neutral dark jacket, natural expression, documentary founder energy, background softly blurred, website cover-image ready."
    ),
    (
        "gpt-portrait-05.png",
        "Approachable authority",
        "Warm black-and-white portrait of the same founder, clean light-gray studio background, simple dark overshirt over white tee, relaxed shoulders, approachable smile but still serious and credible, modern personal-brand portrait, not glossy."
    ),
]

url = "https://api.openai.com/v1/images/edits"
headers = {"Authorization": f"Bearer {API_KEY}"}

for idx, (filename, name, variant_prompt) in enumerate(VARIANTS, start=1):
    prompt = f"{SYSTEM_DIRECTION}\n\nVariant {idx}: {name}.\n{variant_prompt}\n\nOutput: vertical portrait, 1024x1536 composition if possible, website-ready, no text, no watermark."
    print(f"Generating {filename}: {name}")

    with SRC_1.open("rb") as f1, SRC_2.open("rb") as f2:
        files = [
            ("image[]", (SRC_1.name, f1, "image/jpeg")),
            ("image[]", (SRC_2.name, f2, "image/jpeg")),
        ]
        data = {
            "model": "gpt-image-1",
            "prompt": prompt,
            "size": "1024x1536",
            "quality": "high",
            "n": "1",
        }
        response = requests.post(url, headers=headers, data=data, files=files, timeout=600)

    if response.status_code >= 400:
        print(response.text)
        response.raise_for_status()

    payload = response.json()
    image_b64 = payload["data"][0].get("b64_json")
    if not image_b64:
        print(json.dumps(payload, indent=2)[:2000])
        raise RuntimeError(f"No b64_json returned for {filename}")

    output_path = OUT / filename
    output_path.write_bytes(base64.b64decode(image_b64))
    print(f"Saved {output_path}")

print("Done.")
