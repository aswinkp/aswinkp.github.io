#!/usr/bin/env python3
"""
Generate V203 B mouth/smile correction candidates.

Problem being fixed: current V203 B has good forehead/eyebrows/hair/site fit,
but lips/smile do not feel like Aswin. This pass constrains the mouth/lips/smile
much more strongly using real photo references only for identity.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
REFS = [
    ROOT / "static/assets/generated-ai-portraits/references/aswin-github-avatar.jpg",
    ROOT / "static/assets/generated-ai-portraits/references/aswin-semi-professional.jpeg",
    ROOT / "static/assets/generated-ai-portraits/references/aswin-professional-dp.jpeg",
]
STYLE_REFS = [
    ROOT / "static/assets/generated-ai-portraits/v202-v203/v203-b-founder-operator-warm.png",
    ROOT / "static/assets/generated-ai-portraits/gpt-portrait-v2-03.png",
]
OUT = ROOT / "static/assets/generated-ai-portraits/v203b-mouth-fix"
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob("*.png"):
    old.unlink()

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("OPENAI_API_KEY is not set")
missing = [p for p in [*REFS, *STYLE_REFS] if not p.exists()]
if missing:
    raise SystemExit("Missing files: " + ", ".join(map(str, missing)))

IDENTITY = """
Use the FIRST THREE attached photos as the only identity references for Aswin Kumar.
Generate a new original portrait of the same person. People who know him, especially family, should recognize him immediately.

Highest priority correction: preserve his real mouth, lips, smile shape, and lower-face identity.
The generated smile must look like the real reference photos, especially the natural slight smile in the semi-professional and professional DP references.
Do not invent a new mouth. Do not make the lips fuller, thinner, wider, sharper, too symmetrical, glossy, westernized, or model-like.
Keep the natural relationship between mustache, upper lip, lower lip, teeth visibility, cheeks, and beard. If teeth are visible, keep them very subtle and natural; closed-mouth or barely-open smile is safer.
Avoid the fake AI-smile look. Avoid smirk, grin, pursed lips, duck lips, overly polished lips, or unnaturally stretched corners.

Also preserve: youthful South Asian/Indian face, oval-to-slightly-rounded face, thick dark swept-back hair, prominent dark eyebrows, dark almond-shaped eyes, medium-width straight nose with softly rounded tip, warm medium-brown skin tone, well-groomed full beard connected to mustache, natural hairline, and real facial proportions.
Do not westernize, slim, age, beautify, or change his face.
One person only. One coherent face only. No duplicate features. No hands.
""".strip()

STYLE = """
Use the LAST TWO attached images as STYLE REFERENCES ONLY. Do not use their faces as identity.
Keep only the V203 B direction: founder/operator editorial, warm but authoritative, dark seamless #070707-style background, dark clothing blending into the site, face as focal point, clean homepage-ready crop.
No new style directions. No props. No busy office scene. No text/logos/watermark.
""".strip()

VARIANTS = [
    ("v203b-mouthfix-01-closed-natural.png", "closed-mouth natural slight smile, very close to real mouth/lip shape, warm approachable authority"),
    ("v203b-mouthfix-02-barely-open.png", "barely-open natural smile with minimal teeth if any, preserve real lip proportions, not a grin"),
    ("v203b-mouthfix-03-neutral-warm.png", "neutral-warm expression with only a tiny smile at the corners, safest identity-preserving mouth"),
    ("v203b-mouthfix-04-reference-smile.png", "natural professional-DP-like smile but toned down for dark founder portrait, preserve mustache/lip/beard relationship"),
]

url = "https://api.openai.com/v1/images/edits"
headers = {"Authorization": f"Bearer {API_KEY}"}

for i, (filename, mouth_direction) in enumerate(VARIANTS, 1):
    prompt = f"{IDENTITY}\n\n{STYLE}\n\nMouth/smile variant: {mouth_direction}.\n\nGenerate one realistic vertical editorial portrait, 1024x1536. Highest priority: the mouth/lips/smile must feel natural and recognizably Aswin."
    print(f"Generating {i}/{len(VARIANTS)}: {filename}", flush=True)
    handles = []
    try:
        files = []
        for p in REFS:
            f = p.open("rb"); handles.append(f)
            files.append(("image[]", (p.name, f, "image/jpeg")))
        for p in STYLE_REFS:
            f = p.open("rb"); handles.append(f)
            files.append(("image[]", (p.name, f, "image/png")))
        data = {"model": "gpt-image-1", "prompt": prompt, "size": "1024x1536", "quality": "high", "n": "1"}
        response = requests.post(url, headers=headers, data=data, files=files, timeout=600)
    finally:
        for f in handles:
            f.close()
    if response.status_code >= 400:
        print(response.text)
        response.raise_for_status()
    image_b64 = response.json()["data"][0]["b64_json"]
    out_path = OUT / filename
    out_path.write_bytes(base64.b64decode(image_b64))
    print(f"Saved {out_path}", flush=True)
print("Done.")
