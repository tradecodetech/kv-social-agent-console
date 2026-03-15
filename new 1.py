def build_lawn_visual_prompt(pillar: str) -> str:
    return f"""
Create a clean, professional lawn care tip graphic.

Style:
- Minimal
- Green and natural tones
- No people
- No logos
- High contrast text

Text on image:
"Lawn Tip"
"{pillar}"

Layout:
- Square (1:1)
- Social media friendly
- Clear hierarchy
"""
