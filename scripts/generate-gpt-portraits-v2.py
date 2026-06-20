#!/usr/bin/env python3
"""
Regenerate cleaner AI-created founder portrait variants using OpenAI GPT image generation.
This v2 set is stricter: one person only, simple compositions, no hands/body complexity.
"""
from __future__ import annotations

import base64
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

BASE = """
The two attached photos are identity references of the same real person: Aswin Kumar.
Generate ONE new original portrait of this same person. Do not copy either exact source photo.
Do not blend two faces. Do not show duplicated facial features. Do not show multiple people.
One face only, centered, coherent anatomy, natural eyes, natural mouth, realistic beard and hair.
Keep him recognizably South Asian/Indian and recognizably the same person from the references.
This portrait is for a minimal dark founder portfolio website. He should read as a credible founder,
operator, and public thought leader: calm, high-trust, authoritative, serious but human.
No text, no watermark, no logos, no extra faces, no malformed hands, no surreal artifacts.
Prefer simple head-and-shoulders or upper-torso composition.
""".strip()

VARIANTS = [
    ("gpt-portrait-v2-01.png", "black-and-white executive editorial, dark charcoal seamless background, black blazer, open collar black shirt, direct eye contact, very slight confident smile, head and shoulders, refined studio lighting, realistic skin texture"),
    ("gpt-portrait-v2-02.png", "black-and-white magazine profile, three-quarter angle, looking just off camera, dark crewneck or turtleneck, textured gray background, thoughtful public intellectual mood, close crop, calm expression"),
    ("gpt-portrait-v2-03.png", "monochrome founder portrait in a quiet minimal office, blurred bookshelf or desk background, seated but only upper torso visible, dark overshirt, thoughtful approachable expression, editorial documentary style"),
    ("gpt-portrait-v2-04.png", "high-contrast black-and-white cover portrait, asymmetrical negative space on the left for website layout, subject on right third, dark jacket, direct gaze, serious founder-authority look, clean background"),
    ("gpt-portrait-v2-05.png", "soft black-and-white approachable authority portrait, light gray background, simple dark overshirt over plain tee, natural relaxed smile, upper torso, modern personal brand but not corporate stock photo"),
]

url = "https://api.openai.com/v1/images/edits"
headers = {"Authorization": f"Bearer {API_KEY}"}

for idx, (filename, direction) in enumerate(VARIANTS, start=1):
    prompt = f"{BASE}\n\nVariant {idx}: {direction}\n\nGenerate a realistic editorial portrait, vertical composition, website hero-ready."
    print(f"Generating {filename}")
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
        r = requests.post(url, headers=headers, data=data, files=files, timeout=600)
    if r.status_code >= 400:
        print(r.text)
        r.raise_for_status()
    b64 = r.json()["data"][0]["b64_json"]
    path = OUT / filename
    path.write_bytes(base64.b64decode(b64))
    print(f"Saved {path}")
print("Done.")
