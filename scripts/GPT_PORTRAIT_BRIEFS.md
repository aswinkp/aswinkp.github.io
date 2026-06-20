# GPT portrait generation briefs

The previous black-and-white images were local transformations. That is not enough for the direction Aswin asked for.

The actual desired direction is: use both real photos as identity references and generate new original portraits that give the portfolio its character.

Reference photos:
- `static/assets/authoritative-portraits/source-linkedin.jpg`
- `static/assets/authoritative-portraits/source-slack.jpg`

Generated output target:
- `static/assets/generated-ai-portraits/`

Run after setting an OpenAI image API key:

```bash
cd /Users/aswin/projects/personal-branding/aswinkp.github.io/hugo-site
export OPENAI_API_KEY="..."
python3 scripts/generate-gpt-portraits.py
```

Five intended variants:

1. Executive editorial charcoal
   - homepage default candidate
   - black-and-white, dark charcoal background, blazer/open-collar shirt
   - serious, calm, direct, authoritative

2. Writer founder at desk
   - intellectual/operator tone
   - desk, notebook/laptop, quiet office/study
   - thoughtful and founder-authored

3. Public thinker profile
   - magazine/profile energy
   - three-quarter profile, dark turtleneck/minimal black shirt
   - more thought-leader than CEO headshot

4. Founder in motion
   - documentary/candid founder feel
   - walking through a minimal workspace corridor
   - energetic but still restrained

5. Approachable authority
   - warmer and more human
   - light-gray studio background, dark overshirt/white tee
   - credible but not severe

Important guardrails:
- Do not copy exact source pose/outfit/background.
- Keep identity recognizable from the two real photos.
- Avoid SaaS/startup stock photo vibes.
- Avoid fake CEO glamour.
- Avoid over-retouched skin.
- No text or watermark in the image.
