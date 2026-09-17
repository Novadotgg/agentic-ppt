from typing import Dict, Any, Optional
from backend.agent.state import PresentationState


# ──────────────────────────────────────────────────────────────────────────────
# PREMIUM THEME DEFINITIONS
# Each entry defines a complete visual system that is serialised into the prompt
# so the AI produces theme-faithful HEX palettes, fonts, and slide treatments.
# ──────────────────────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────
# PREMIUM THEME DEFINITIONS
# Each entry defines a complete visual system that is serialised into the prompt
# so the AI produces theme-faithful HEX palettes, fonts, and slide treatments.
# ──────────────────────────────────────────────────────────────────────────────
THEME_SPECS: dict[str, dict] = {
    "Obsidian Emerald": {
        "summary": "Premium AI / Technology — black, charcoal, emerald, white",
        "background": "#080e1a",
        "surface": "#0c1422",
        "surface_border": "#132f2b",
        "primary_accent": "#10b981",
        "secondary_accent": "#34d399",
        "heading_color": "#f1f5f9",
        "body_text": "#94a3b8",
        "muted_text": "#64748b",
        "chart_colors": "#10b981, #34d399, #059669, #6ee7b7, #064e3b",
        "title_slide": "Full-bleed dark with crisp white headline, emerald accent kicker/badge, and minimal layout",
        "content_slide": "Dark navy surface card (#0c1422) on dark background (#080e1a), subtle emerald border (#132f2b), white heading",
        "metrics_style": "Large emerald numbers (#10b981) on dark surface cards, white labels, muted descriptions",
        "table_style": "Dark rows, emerald header row, subtle emerald dividers",
        "highlight": "#064e3b background with #10b981 text",
        "image_treatment": "Dark-tinted with emerald color overlay or emerald border frame",
        "typography_mood": "Minimalist, high-tech geometric sans (e.g. Inter, Aptos, Segoe UI)",
    },
    "Midnight Executive": {
        "summary": "Corporate / Finance / Strategy — deep navy, antique gold, crisp silver-white",
        "background": "#0d1b2a",
        "surface": "#132238",
        "surface_border": "#1f3554",
        "primary_accent": "#d4a017",
        "secondary_accent": "#f0c040",
        "heading_color": "#f8fafc",
        "body_text": "#94a3b8",
        "muted_text": "#64748b",
        "chart_colors": "#d4a017, #f0c040, #b8860b, #ffd966, #8b6914",
        "title_slide": "Full navy background with gold accent rule and crisp white headline",
        "content_slide": "Navy surface card (#132238), thin navy border (#1f3554), gold accent highlights, white headings",
        "metrics_style": "Gold numbers (#d4a017) on navy surface cards, white label, muted text",
        "table_style": "Navy alternating rows, gold bold header row, white text",
        "highlight": "#132238 background with #d4a017 bold text",
        "image_treatment": "Navy tint overlay with subtle gold vignette edges",
        "typography_mood": "Authoritative corporate typography — crisp sans if Sans requested, serif only if Classic Serif requested",
    },
    "Ivory Linen": {
        "summary": "Editorial / Elegant / Warm — warm ivory, bronze-gold, near-black warm charcoal",
        "background": "#faf8f5",
        "surface": "#ffffff",
        "surface_border": "#e7e0d6",
        "primary_accent": "#b8860b",
        "secondary_accent": "#8b6508",
        "heading_color": "#1c1917",
        "body_text": "#44403c",
        "muted_text": "#78716c",
        "chart_colors": "#b8860b, #8b6508, #d4b896, #6b4e30, #e8d5b8",
        "title_slide": "Warm ivory full-bleed, deep charcoal headline, warm bronze accent line",
        "content_slide": "Crisp white cards (#ffffff) on ivory background (#faf8f5), warm neutral border (#e7e0d6), charcoal headings",
        "metrics_style": "Deep bronze numbers (#b8860b) on white cards, charcoal labels",
        "table_style": "Alternating ivory/white rows, warm-gold header, dark charcoal text",
        "highlight": "#f5efe6 background with #8b6508 bold text",
        "image_treatment": "Warm sepia tint, soft vignette edges, vintage feel",
        "typography_mood": "Refined editorial typography — clean humanist sans if Sans requested, serif only if Classic Serif requested",
    },
    "Arctic Blueprint": {
        "summary": "SaaS / Product / Clean Tech — icy off-white, electric blue, dark slate",
        "background": "#f1f5f9",
        "surface": "#ffffff",
        "surface_border": "#cbd5e1",
        "primary_accent": "#2563eb",
        "secondary_accent": "#0284c7",
        "heading_color": "#0f172a",
        "body_text": "#334155",
        "muted_text": "#64748b",
        "chart_colors": "#2563eb, #0284c7, #60a5fa, #93c5fd, #1d4ed8",
        "title_slide": "Clean icy background, bold dark-slate headline, electric-blue geometric accent line",
        "content_slide": "Pure white card (#ffffff) with slate border (#cbd5e1), dark-slate heading, electric-blue accent line",
        "metrics_style": "Electric-blue numbers (#2563eb) on white cards, dark-slate labels",
        "table_style": "White rows with blue header row, light blue alternating rows",
        "highlight": "#dbeafe background with #1d4ed8 text",
        "image_treatment": "Clean no-filter — or subtle blue tint overlay on photography",
        "typography_mood": "Geometric sans-serif — Inter, Aptos, Segoe UI — highly legible, modern SaaS pitch deck",
    },
    "Crimson Authority": {
        "summary": "Leadership / Bold / High Impact — pure black, crimson red, pure white",
        "background": "#09090b",
        "surface": "#141417",
        "surface_border": "#27272a",
        "primary_accent": "#ef4444",
        "secondary_accent": "#f87171",
        "heading_color": "#fafafa",
        "body_text": "#d4d4d8",
        "muted_text": "#71717a",
        "chart_colors": "#ef4444, #f87171, #b91c1c, #fca5a5, #7f1d1d",
        "title_slide": "Pure dark full-bleed with crimson accent line, dramatic white headline",
        "content_slide": "Dark surface card (#141417) on dark background (#09090b), subtle zinc border (#27272a), crimson accent, pure-white heading",
        "metrics_style": "Crimson numbers (#ef4444) on dark surface cards, pure-white labels",
        "table_style": "Very dark alternating rows, crimson bold header row, white text",
        "highlight": "#271717 background with #f87171 text",
        "image_treatment": "High contrast — desaturated black-and-white with red color grade or red border frame",
        "typography_mood": "Commanding, high-impact sans — Inter, Segoe UI, Aptos, Montserrat",
    },
}


def _get_theme_spec(theme_selection: str) -> str:
    """Serialise the full theme visual system into a prompt-friendly string."""
    spec = THEME_SPECS.get(theme_selection)
    if not spec:
        return (
            f"Theme: {theme_selection}. "
            "Derive a cohesive, professional color palette appropriate to this theme name."
        )
    lines = [f"**{theme_selection}** — {spec['summary']}"]
    for key, val in spec.items():
        if key == "summary":
            continue
        label = key.replace("_", " ").title()
        lines.append(f"  - {label}: {val}")
    return "\n".join(lines)


def build_system_prompt(
    topic: str,
    number_of_slides: int,
    font_style: str,
    theme_selection: str,
    images: bool,
    logo: bool,
    notes: bool,
    description: Optional[str] = None,
) -> str:
    """
    Constructs a production-grade, guardrailed system prompt for an agentic presentation generator.
    """
    image_instruction = (
        "Generate detailed image generation prompts and icon keywords for every slide."
        if images
        else "Images are disabled. Set visual_assets image_prompt to null and provide only an icon_keyword."
    )
    logo_instruction = (
        "Include branding specification ('Top-right corner on header')."
        if logo
        else "Logo is disabled. Set logo_specification to 'None'."
    )
    notes_instruction = (
        "Generate comprehensive, conversational speaker notes with talking points for each slide."
        if notes
        else "Speaker notes are disabled. Set speaker_notes to '' for each slide."
    )

    clean_desc = description.strip() if description else ""
    desc_section = (
        f"- **Additional Topic Context / User Description**:\n  {clean_desc}\n"
        if clean_desc
        else ""
    )

    desc_requirement = (
        f'\n6. **Incorporate User Context**: The user has specified: "{clean_desc}". You MUST reflect these specific points, focus areas, and context across the presentation.'
        if clean_desc
        else ""
    )

    theme_spec_block = _get_theme_spec(theme_selection)

    return f"""
# ROLE & IDENTITY
You are "DeckArchitect AI", a world-class Executive Presentation Designer, Information Architect, and Subject Matter Expert.
Your mission is to produce a COMPLETE, CONTENT-RICH, slide-by-slide presentation on the given topic — with real facts, insights, trends, and data — ready for programmatic rendering into PowerPoint (.pptx).

---

# USER SPECIFICATIONS
- **Topic / Core Subject**: {topic}
{desc_section}- **Target Slide Count**: {number_of_slides}
- **Font Direction**: {font_style}
- **Image Guidelines**: {image_instruction}
- **Branding / Logo**: {logo_instruction}
- **Speaker Notes**: {notes_instruction}

---

# THEME & VISUAL SYSTEM (CRITICAL — MUST FOLLOW EXACTLY)
The selected presentation theme is: **{theme_selection}**

Full visual system specification:
{theme_spec_block}

You MUST use this exact color system when filling the `color_palette` JSON fields. Do NOT invent different colors. The palette must faithfully match the theme spec above.

---

# CONTENT REQUIREMENTS (CRITICAL — READ CAREFULLY)
Every slide MUST contain real, substantive content about "{topic}". This is non-negotiable:

1. **Write actual content** — NOT placeholders, NOT "[Placeholder]", NOT "[Estimated]", NOT generic filler like "Description here" or "Add content".
2. **Every bullet must be a real insight** — Include specific facts, statistics, trends, policy implications, historical context, or forward-looking projections that are genuinely relevant to "{topic}".
3. **Each `description` field must be a full, meaningful sentence or data point** — minimum 8 words, maximum 20 words.
4. **Headlines must name the specific takeaway** — e.g., "India's Digital Economy to Reach $1T by 2030" not "Economic Growth".
5. **3–5 content_elements per slide** — Never leave a slide with 0 or 1 bullet. Minimum 3.{desc_requirement}

---

# CORE DESIGN & NARRATIVE PRINCIPLES
1. **The Rule of One Idea**: Each slide conveys exactly ONE core message.
2. **Action-Driven Headlines**: Titles must be active takeaways, not passive labels.
3. **Visual Hierarchy & Layout Archetypes**: Assign every slide a deliberate layout:
   - `hero_title`: Opener / closing slide
   - `split_screen`: 2 columns (e.g., Problem vs Solution, Before vs After)
   - `metrics_callout`: 3-4 key numbers/KPIs with brief descriptors
   - `process_timeline`: Sequential steps or milestones
   - `feature_grid`: 3-4 card highlights
   - `quote_focus`: Impactful statement or testimonial
4. **Aesthetic Consistency**:
   - Use the exact color palette from the theme spec above.
   - Choose fonts harmonizing with "{font_style}" and the theme's typography mood.

---

# STRICT GUARDRAILS
1. **EXACT SLIDE COUNT**: Produce EXACTLY {number_of_slides} slides. No more, no less.
2. **OUTPUT FORMAT**: Respond ONLY with a valid JSON object enclosed in ```json ... ``` code fences. No preamble, no outro text.
3. **NO PLACEHOLDERS**: Do NOT write "[Placeholder]", "[Estimated]", "[Add content]", or any filler text anywhere in content_elements.
4. **CONTENT SAFETY**: Refuse hate speech, harassment, or disinformation.

---

# OUTPUT JSON SCHEMA
```json
{{
  "metadata": {{
    "topic": "{topic}",
    "total_slides": {number_of_slides},
    "theme": {{
      "name": "{theme_selection}",
      "color_palette": {{
        "background": "#HEX (slide background from theme spec)",
        "surface": "#HEX (card container background from theme spec)",
        "surface_border": "#HEX (card border from theme spec)",
        "primary_accent": "#HEX (primary brand accent from theme spec)",
        "secondary_accent": "#HEX (secondary accent from theme spec)",
        "heading": "#HEX (heading text color from theme spec)",
        "body": "#HEX (body text color from theme spec)",
        "muted": "#HEX (muted text color from theme spec)"
      }},
      "typography": {{
        "header_font": "Clean font name respecting '{font_style}' (e.g. Inter/Segoe UI/Aptos if Sans-Serif, Georgia if Serif)",
        "body_font": "Clean readable font name respecting '{font_style}' (e.g. Inter/Segoe UI/Calibri if Sans-Serif)"
      }},
      "logo_specification": "Top-right | None"
    }}
  }},
  "slides": [
    {{
      "slide_number": 1,
      "layout": "hero_title",
      "headline": "Specific, active takeaway title about {topic}",
      "subheadline": "One sentence contextual subtitle",
      "content_elements": [
        {{
          "type": "bullet",
          "title": "Specific aspect of {topic}",
          "description": "Real, specific fact or insight about this aspect — 8 to 20 words"
        }},
        {{
          "type": "bullet",
          "title": "Another specific aspect",
          "description": "Another real insight, statistic, or trend — 8 to 20 words"
        }},
        {{
          "type": "metric",
          "title": "Key metric label",
          "description": "Specific number or percentage with context"
        }}
      ],
      "visual_assets": {{
        "image_prompt": null,
        "recommended_aspect_ratio": "16:9",
        "icon_keyword": "chart-line"
      }},
      "speaker_notes": "Conversational talking points for this slide"
    }}
  ]
}}
```

Now generate the COMPLETE {number_of_slides}-slide presentation on "{topic}" with REAL, SUBSTANTIVE content in every bullet. Do not use any placeholders.
""".strip()


def prompt_node(state: PresentationState) -> Dict[str, Any]:
    """
    LangGraph Node 1: Synthesizes user specifications into the structured prompt.
    """
    prompt = build_system_prompt(
        topic=state.get("topic", "Presentation Topic"),
        description=state.get("description"),
        number_of_slides=state.get("number_of_slides", 6),
        font_style=state.get("font_style", "Modern Sans-Serif"),
        theme_selection=state.get("theme_selection", "Obsidian Emerald"),
        images=state.get("images", False),
        logo=state.get("logo", False),
        notes=state.get("notes", True),
    )
    return {"prompt": prompt}
