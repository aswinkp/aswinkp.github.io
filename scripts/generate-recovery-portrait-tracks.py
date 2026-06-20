#!/usr/bin/env python3
"""
Two-track portrait recovery:
1) Exact-face-preserving photo edits: use the semi-professional real photo as base,
   protect face/hair/ears via mask, edit only background/clothing/lighting around it.
2) Stylized illustrated founder portraits: intentionally not photoreal, so identity drift is less uncanny.

Avoids exact Studio Ghibli naming; uses warm hand-painted animation/editorial language.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path
import subprocess
import requests

ROOT = Path(__file__).resolve().parents[1]
REF_DIR = ROOT / "static/assets/generated-ai-portraits/references"
SEMI = REF_DIR / "aswin-semi-professional.jpeg"
GITHUB = REF_DIR / "aswin-github-avatar.jpg"
PRO_DP = REF_DIR / "aswin-professional-dp.jpeg"
STYLE_V203B = ROOT / "static/assets/generated-ai-portraits/v202-v203/v203-b-founder-operator-warm.png"

OUT_EXACT = ROOT / "static/assets/generated-ai-portraits/exact-face-edits"
OUT_STYLIZED = ROOT / "static/assets/generated-ai-portraits/stylized-founder"
WORK = ROOT / "static/assets/generated-ai-portraits/work"
for d in (OUT_EXACT, OUT_STYLIZED, WORK):
    d.mkdir(parents=True, exist_ok=True)
for d in (OUT_EXACT, OUT_STYLIZED):
    for old in d.glob("*.png"):
        old.unlink()

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("OPENAI_API_KEY is not set")
for p in [SEMI, GITHUB, PRO_DP, STYLE_V203B]:
    if not p.exists():
        raise SystemExit(f"Missing {p}")

# Prepare a standard vertical image and a mask.
# Mask semantics for OpenAI edit: transparent = editable, opaque = preserve.
# We preserve a generous face/hair/ears ellipse from the semi-professional photo.
BASE = WORK / "semi-base-1024x1536.png"
MASK = WORK / "semi-face-preserve-mask-1024x1536.png"
subprocess.run([
    "magick", str(SEMI),
    "-auto-orient",
    "-resize", "1024x1536^",
    "-gravity", "center",
    "-extent", "1024x1536",
    str(BASE),
], check=True)
# Transparent canvas, draw white opaque ellipse over face/hair/ears region to preserve.
# Coordinates tuned for the normalized semi-professional portrait.
subprocess.run([
    "magick", "-size", "1024x1536", "xc:none",
    "-fill", "white",
    "-draw", "ellipse 512,415 245,335 0,360",
    str(MASK),
], check=True)

URL = "https://api.openai.com/v1/images/edits"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def post_edit(files, prompt, out_path, masked=False):
    data = {"model": "gpt-image-1", "prompt": prompt, "size": "1024x1536", "quality": "high", "n": "1"}
    handles = []
    try:
        upload = []
        for field, path, mime in files:
            f = Path(path).open("rb"); handles.append(f)
            upload.append((field, (Path(path).name, f, mime)))
        print(f"Generating {out_path.name}", flush=True)
        r = requests.post(URL, headers=HEADERS, data=data, files=upload, timeout=600)
    finally:
        for f in handles:
            f.close()
    if r.status_code >= 400:
        print(r.text)
        r.raise_for_status()
    out_path.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"Saved {out_path}", flush=True)

EXACT_PROMPT_BASE = """
Edit the image while preserving the protected face/hair/ears region EXACTLY.
Do not alter the face, lips, smile, mouth, eyebrows, forehead, eyes, nose, beard, mustache, skin tone, face shape, hairline, or ears inside the protected area.
The person must remain exactly the same as the source photo in the preserved face region.
Only change the editable surrounding areas: background, clothing, lighting atmosphere, crop feel, and overall mood.
Goal: make the real photo feel like it belongs on a dark #070707 minimal founder portfolio website.
No text, logo, props, busy scene, hands, or new person.
""".strip()

exact_variants = [
    ("exact-face-01-dark-founder.png", "Seamless near-black #070707 background. Dark charcoal/black simple founder shirt or overshirt. Subtle editorial rim light around shoulders only. Face remains untouched."),
    ("exact-face-02-warm-authoritative.png", "Dark warm charcoal background with very soft studio falloff. Replace clothing with minimal dark crewneck/overshirt. Calm approachable founder tone. Face remains untouched."),
    ("exact-face-03-public-thinker.png", "Minimal black editorial background, slightly more intellectual public-thinker mood, dark jacket/shirt, low-key lighting around body only. Face remains untouched."),
]

for name, variant in exact_variants:
    prompt = EXACT_PROMPT_BASE + "\n\nVariant: " + variant
    post_edit([
        ("image", BASE, "image/png"),
        ("mask", MASK, "image/png"),
    ], prompt, OUT_EXACT / name, masked=True)

STYLIZED_PROMPT_BASE = """
Use the first three attached real photos as identity references for Aswin Kumar.
Use the last attached image only as a mood/composition reference for the dark founder/operator direction, not identity.
Create a stylized illustrated founder portrait, NOT photorealistic.
Since exact photoreal identity has been failing, make this intentionally hand-painted and animated/editorial so it avoids the uncanny realistic almost-face problem.

Preserve recognizable identity anchors: thick swept dark hair, prominent dark eyebrows, dark eyes, youthful South Asian/Indian face, medium-brown skin tone, beard connected to mustache, real face proportions, natural mouth/lips/smile relationship from the real photos.
Especially avoid inventing a new smile or lips. Keep the mouth simple, natural, and restrained.

Style: warm hand-painted cinematic animation-inspired editorial portrait, approachable authoritative founder, dark minimal #070707 background, dark clothing, face as focal point, premium but human.
Do not imitate any specific named studio, film, or living artist. No text/logos/watermark. One person only.
""".strip()

stylized_variants = [
    ("stylized-01-warm-founder.png", "Subtle closed-mouth smile, warm eyes, dark founder portrait, soft painterly lighting."),
    ("stylized-02-public-thinker.png", "Public thinker feel, three-quarter but recognizable, restrained natural smile, editorial shadow."),
    ("stylized-03-approachable-authority.png", "Approachable authoritative founder, slightly more pleasant expression, clean animation-poster finish."),
    ("stylized-04-notebook-operator.png", "Founder/operator energy, calm confidence, dark minimal background, natural mouth and beard shape."),
]

for name, variant in stylized_variants:
    prompt = STYLIZED_PROMPT_BASE + "\n\nVariant: " + variant
    post_edit([
        ("image[]", SEMI, "image/jpeg"),
        ("image[]", GITHUB, "image/jpeg"),
        ("image[]", PRO_DP, "image/jpeg"),
        ("image[]", STYLE_V203B, "image/png"),
    ], prompt, OUT_STYLIZED / name)

print("Done.")
print(f"Exact-face outputs: {OUT_EXACT}")
print(f"Stylized outputs: {OUT_STYLIZED}")
