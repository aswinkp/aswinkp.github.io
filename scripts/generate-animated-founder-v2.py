#!/usr/bin/env python3
"""
Generate animated/stylized founder portrait variations only.

Track A realistic face preservation is intentionally abandoned because it failed.
This batch is not trying to produce a photoreal same-face result. It creates illustrated/animated founder portraits using real photos as loose identity anchors.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
REF_DIR = ROOT / "static/assets/generated-ai-portraits/references"
IDENTITY_REFS = [
    REF_DIR / "aswin-semi-professional.jpeg",
    REF_DIR / "aswin-github-avatar.jpg",
    REF_DIR / "aswin-professional-dp.jpeg",
]
STYLE_REFS = [
    ROOT / "static/assets/generated-ai-portraits/v202-v203/v203-b-founder-operator-warm.png",
    ROOT / "static/assets/generated-ai-portraits/stylized-founder/stylized-01-warm-founder.png",
]
OUT = ROOT / "static/assets/generated-ai-portraits/animated-founder-v2"
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob("*.png"):
    old.unlink()

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("OPENAI_API_KEY is not set")
missing = [p for p in [*IDENTITY_REFS, *STYLE_REFS] if not p.exists()]
if missing:
    raise SystemExit("Missing files: " + ", ".join(map(str, missing)))

BASE_PROMPT = """
Use the first three attached real photos as loose identity anchors for Aswin Kumar.
Use the last two attached images only as mood/composition/style references, not identity.

Create a stylized animated/editorial founder portrait, not a photorealistic generated photo.
The goal is to avoid the uncanny realistic almost-face problem. It should be clearly illustrated/animated while still feeling inspired by Aswin's real identity.

Important identity anchors to keep recognizable in simplified illustrated form:
- youthful South Asian/Indian founder
- thick dark swept hair with similar hairline direction
- prominent dark eyebrows and expressive dark eyes
- medium-brown skin tone
- beard connected to mustache, close to his natural beard outline
- oval/slightly rounded face shape
- natural restrained mouth and smile; do not invent a fake glossy AI smile
- calm approachable expression with authority

Do NOT attempt a hyperrealistic face. Do NOT make lips/mouth over-detailed or unnatural. Do NOT westernize, age up, make model-like, or turn into a generic handsome avatar.
No text, logos, watermark, props, hands, or busy scene.

Website fit:
- dark #070707 / near-black seamless background
- dark clothing that can blend into the page
- vertical 3:4 homepage portrait composition
- face as focal point
- authoritative but approachable founder/public thinker
- premium minimal personal portfolio mood
Do not imitate any specific named studio, film, or living artist.
""".strip()

VARIANTS = [
    ("animated-v2-01-soft-founder.png", "Soft hand-painted animation style, direct gaze, tiny closed-mouth smile, warm but restrained."),
    ("animated-v2-02-public-thinker.png", "Public thinker/editorial animation style, slightly serious, subtle warmth in eyes, minimal smile."),
    ("animated-v2-03-approachable-authority.png", "Most approachable version, gentle natural smile, still founder-authoritative, not cute or childish."),
    ("animated-v2-04-dark-operator.png", "Darker operator mood, confident and calm, face lit softly from front, mouth neutral-warm."),
    ("animated-v2-05-ink-and-paint.png", "Refined ink-and-paint editorial illustration, clean facial simplification, natural beard/mustache shape."),
    ("animated-v2-06-cinematic-warm.png", "Cinematic warm animated portrait, slightly amber face lighting, dark seamless site background."),
    ("animated-v2-07-minimal-avatar.png", "Minimal founder avatar style, less detail, strongest avoidance of uncanny realism, authoritative calm."),
    ("animated-v2-08-premium-editorial.png", "Premium editorial illustration, confident slight smile, polished but human, homepage-ready."),
]

url = "https://api.openai.com/v1/images/edits"
headers = {"Authorization": f"Bearer {API_KEY}"}

for i, (filename, variant) in enumerate(VARIANTS, 1):
    prompt = BASE_PROMPT + "\n\nVariant: " + variant
    files = []
    handles = []
    try:
        for p in IDENTITY_REFS:
            f = p.open("rb"); handles.append(f)
            files.append(("image[]", (p.name, f, "image/jpeg")))
        for p in STYLE_REFS:
            f = p.open("rb"); handles.append(f)
            files.append(("image[]", (p.name, f, "image/png")))
        data = {"model": "gpt-image-1", "prompt": prompt, "size": "1024x1536", "quality": "high", "n": "1"}
        print(f"Generating {i}/{len(VARIANTS)}: {filename}", flush=True)
        r = requests.post(url, headers=headers, data=data, files=files, timeout=600)
    finally:
        for f in handles:
            f.close()
    if r.status_code >= 400:
        print(r.text)
        r.raise_for_status()
    out_path = OUT / filename
    out_path.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"Saved {out_path}", flush=True)

print("Done.")
print(OUT)
