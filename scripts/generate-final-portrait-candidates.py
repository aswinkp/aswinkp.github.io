#!/usr/bin/env python3
"""
Generate focused follow-up portraits from the two approved directions:
- V202 = V2 02 public thinker profile
- V203 = V2 03 founder office/editorial

Uses ONLY these two identity references:
- GitHub avatar
- ~/Downloads/aswin-semi-professional.jpeg copied into references
"""
from __future__ import annotations

import base64
import os
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
REF_1 = ROOT / "static/assets/generated-ai-portraits/references/aswin-github-avatar.jpg"
REF_2 = ROOT / "static/assets/generated-ai-portraits/references/aswin-semi-professional.jpeg"
OUT = ROOT / "static/assets/generated-ai-portraits/final-candidates"
OUT.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("OPENAI_API_KEY is not set. Export it and rerun this script.")

IDENTITY = """
Use ONLY the two attached images as identity references for Aswin Kumar.
Generate a new original portrait of the SAME person. Preserve facial identity closely.
Do not copy exact pose, crop, shirt, lighting, or background. But do preserve: oval-to-slightly-rounded face, thick dark swept-back hair, prominent dark eyebrows, dark almond-shaped eyes, medium-width straight nose with softly rounded tip, warm medium-brown skin tone, well-groomed full beard and connected mustache, and natural confident closed-mouth/semi-open smile.
Important: people who know him should recognize him. Do not westernize the face. Do not make him older, thinner, heavier, or change his jaw, nose, eyes, eyebrows, beard, or hairline.
One person only. One coherent face only. No duplicated eyes. No blended/morphed second face. No malformed hands. No surreal artifacts.
Expression: approachable, authoritative founder; calm confidence; slight pleasant smile, not a broad grin.
Website context: minimal dark founder portfolio, thought leader, high-trust, real and editorial, not glossy SaaS stock photo.
No text, no watermark, no logos.
""".strip()

VARIANTS = [
    ("v202-01-public-thinker-soft-smile.png", "V202 public thinker profile: black-and-white three-quarter magazine profile, looking slightly off camera, subtle confident smile, dark crewneck or turtleneck, textured charcoal background, close head-and-shoulders crop, intellectual and calm."),
    ("v202-02-public-thinker-direct.png", "V202 public thinker profile: black-and-white direct-to-camera editorial portrait, slight pleasant smile, dark minimal overshirt, soft directional studio light, charcoal background, authoritative but approachable."),
    ("v202-03-public-thinker-warmer.png", "V202 public thinker profile: warm monochrome editorial portrait, head slightly turned, eyes toward camera, small confident smile, refined casual dark blazer over plain shirt, muted gray-brown background, founder thought-leader energy."),
    ("v202-04-public-thinker-cover.png", "V202 public thinker profile: black-and-white cover portrait with negative space, subject on right third, slight smile, dark jacket, clean charcoal background, suitable for homepage hero layout."),
    ("v203-01-office-editorial-desk.png", "V203 founder office editorial: monochrome upper-torso portrait in a quiet minimal office, blurred desk/bookshelf background, seated, no visible hands, dark overshirt, slight confident smile, builder/operator energy."),
    ("v203-02-office-editorial-window.png", "V203 founder office editorial: black-and-white portrait near a window in a minimal workspace, soft natural side light, relaxed shoulders, direct eye contact, slight smile, authoritative but human."),
    ("v203-03-office-editorial-notebook.png", "V203 founder office editorial: editorial portrait at a simple desk with notebook/laptop blurred in foreground, only upper torso visible, dark blazer or overshirt, approachable confident smile, documentary founder style."),
    ("v203-04-office-editorial-clean.png", "V203 founder office editorial: clean minimal studio-office background, head-and-shoulders crop, direct gaze, slightly smiling, white or dark collared shirt under dark jacket, polished but not corporate."),
]

url = "https://api.openai.com/v1/images/edits"
headers = {"Authorization": f"Bearer {API_KEY}"}

for idx, (filename, direction) in enumerate(VARIANTS, 1):
    prompt = f"{IDENTITY}\n\nDirection: {direction}\n\nGenerate a realistic vertical portrait, 1024x1536, editorial quality, no artifacts."
    print(f"Generating {filename}")
    with REF_1.open("rb") as f1, REF_2.open("rb") as f2:
        files = [
            ("image[]", (REF_1.name, f1, "image/jpeg")),
            ("image[]", (REF_2.name, f2, "image/jpeg")),
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
    b64 = response.json()["data"][0]["b64_json"]
    path = OUT / filename
    path.write_bytes(base64.b64decode(b64))
    print(f"Saved {path}")
print("Done.")
