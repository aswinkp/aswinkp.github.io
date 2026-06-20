#!/usr/bin/env python3
"""
Generate focused V202/V203 portrait candidates only.

Identity references: ONLY
- static/assets/generated-ai-portraits/references/aswin-github-avatar.jpg
- static/assets/generated-ai-portraits/references/aswin-semi-professional.jpeg
- static/assets/generated-ai-portraits/references/aswin-professional-dp.jpeg

The existing V2 02 / V2 03 images are NOT sent as image references because they
changed identity too much. They are sent only as style references, with explicit
instructions not to use their faces as identity:
- V202: public thinker / editorial profile
- V203: founder/operator office editorial
"""
from __future__ import annotations

import base64
import os
from pathlib import Path
import shutil
import requests

ROOT = Path(__file__).resolve().parents[1]
REF_1 = ROOT / "static/assets/generated-ai-portraits/references/aswin-github-avatar.jpg"
REF_2 = ROOT / "static/assets/generated-ai-portraits/references/aswin-semi-professional.jpeg"
REF_3 = ROOT / "static/assets/generated-ai-portraits/references/aswin-professional-dp.jpeg"
STYLE_1 = ROOT / "static/assets/generated-ai-portraits/final-candidates/v202-01-public-thinker-soft-smile.png"
STYLE_2 = ROOT / "static/assets/generated-ai-portraits/gpt-portrait-v2-02.png"
STYLE_3 = ROOT / "static/assets/generated-ai-portraits/gpt-portrait-v2-03.png"
OUT = ROOT / "static/assets/generated-ai-portraits/v202-v203"
OUT.mkdir(parents=True, exist_ok=True)

# Clear only this focused candidate directory so the review page has no old drift.
for old in OUT.glob("*.png"):
    old.unlink()

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("OPENAI_API_KEY is not set. Export it and rerun this script.")

missing = [p for p in (REF_1, REF_2, REF_3, STYLE_1, STYLE_2, STYLE_3) if not p.exists()]
if missing:
    raise SystemExit("Missing references: " + ", ".join(str(p) for p in missing))

IDENTITY = """
Use ONLY the three attached photos as identity references for Aswin Kumar.
Generate a new original portrait of the SAME person, not a transformation of the source photos.
Preserve identity very closely: youthful South Asian/Indian face, oval-to-slightly-rounded face, thick dark swept-back hair, prominent dark eyebrows, dark almond-shaped eyes, medium-width straight nose with softly rounded tip, warm medium-brown skin tone, well-groomed full beard connected to mustache, natural hairline, and the same overall facial proportions.
People who know him should recognize him immediately. Do not westernize, slim, age, beautify, or significantly change his face. Do not change the nose, eyes, eyebrows, beard shape, hairline, or jaw.
Expression: slight confident smile, pleasant and approachable, calm authority. Not a broad grin.
One person only. One coherent face only. No duplicate eyes, no blended second face, no warped face, no malformed hands, no visible hands.
No text, watermark, logos, props, or busy scene.
""".strip()

STYLE_RULE = """
The last three attached images are STYLE REFERENCES ONLY. Do not use their faces or identity.
Borrow only their mood, composition, monochrome editorial lighting, dark seamless background, thoughtful founder energy, and V202/V203 character direction.
The final face must come from the first three real identity photos only.
""".strip()

SITE_FIT = """
Portfolio fit: minimal dark founder portfolio website with background color #11100e.
The portrait should blend into the dark website: seamless black/charcoal/near-#11100e background or no visible environmental background. Face is the focal point. Clothing can be dark charcoal / black / near #11100e, but exact match is not mandatory.
Editorial, real, high-trust, not glossy SaaS stock photography. Vertical portrait, head-and-shoulders or upper torso, clean crop.
""".strip()

VARIANTS = [
    (
        "v202-a-public-thinker-direct-smile.png",
        "V202 direction only: public thinker / editorial profile. Direct-to-camera black-and-white portrait, head and shoulders, dark seamless charcoal background, subtle confident closed-mouth smile, calm authoritative founder presence.",
    ),
    (
        "v202-b-public-thinker-three-quarter.png",
        "V202 direction only: public thinker / editorial profile. Three-quarter angle, looking slightly off camera but face still clear, slight pleasant smile, dark crewneck or minimal shirt, monochrome charcoal-on-charcoal, intellectual magazine profile energy.",
    ),
    (
        "v202-c-public-thinker-soft-authority.png",
        "V202 direction only: public thinker / editorial profile. Soft low-key lighting, direct gaze, approachable authoritative smile, close crop, minimal dark background that disappears into #11100e, realistic facial identity above all.",
    ),
    (
        "v203-a-founder-operator-direct.png",
        "V203 direction only: founder/operator editorial. Upper-torso portrait, direct eye contact, slight confident smile, dark overshirt or shirt, no visible office details except barely perceptible dark tonal depth, background nearly invisible and blending into #11100e.",
    ),
    (
        "v203-b-founder-operator-warm.png",
        "V203 direction only: founder/operator editorial. Warm human founder energy, calm smile, head-and-shoulders crop, dark minimal clothing, subtle low-key light, barely-there background, practical builder/operator character without props.",
    ),
    (
        "v203-c-founder-operator-cover.png",
        "V203 direction only: founder/operator editorial. Clean cover-style portrait with slight negative space, subject slightly off-center, approachable authoritative smile, dark shirt/jacket, seamless deep charcoal background, homepage-ready.",
    ),
]

url = "https://api.openai.com/v1/images/edits"
headers = {"Authorization": f"Bearer {API_KEY}"}

for i, (filename, direction) in enumerate(VARIANTS, 1):
    prompt = f"{IDENTITY}\n\n{STYLE_RULE}\n\n{SITE_FIT}\n\n{direction}\n\nGenerate one realistic editorial portrait. Highest priority: identity preservation and coherent face."
    print(f"Generating {i}/{len(VARIANTS)}: {filename}", flush=True)
    with REF_1.open("rb") as f1, REF_2.open("rb") as f2, REF_3.open("rb") as f3, STYLE_1.open("rb") as s1, STYLE_2.open("rb") as s2, STYLE_3.open("rb") as s3:
        files = [
            ("image[]", (REF_1.name, f1, "image/jpeg")),
            ("image[]", (REF_2.name, f2, "image/jpeg")),
            ("image[]", (REF_3.name, f3, "image/jpeg")),
            ("image[]", (STYLE_1.name, s1, "image/png")),
            ("image[]", (STYLE_2.name, s2, "image/png")),
            ("image[]", (STYLE_3.name, s3, "image/png")),
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
    print(f"Saved {path}", flush=True)

print("Done.")
