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

# CONTENT & NARRATIVE ARCHITECTURE (CRITICAL — READ CAREFULLY)
You are an executive presentation strategist. Your presentations must be information-dense yet visually scannable. Do not write bare keywords, superficial bullet fragments, or generic filler. Instead, explain the subject thoroughly with substantive insights.

For every content slide, produce:
1. **Active Takeaway Headline**: Formulate a complete, declarative thesis (e.g., "AI Is Shifting Clinical Care Toward Earlier, Personalized Detection" — never a vague label like "Overview" or "Technology").
2. **Contextual Subheadline**: 1 concise sentence framing the key insight or market dynamic for the slide.
3. **3–5 Structured Content Elements**:
   - **`title`**: A sharp, descriptive section heading (2 to 5 words, e.g., "Earlier Diagnostic Screening", "Targeted Therapeutics").
   - **`description`**: 1–2 concise explanatory sentences (typically 20–40 words) that unpack the "why" and "how". Include supporting evidence: statistics, concrete examples, mechanisms, business implications, or practical takeaways.
   - **`type`**: Assign appropriate types: `"bullet"` for concept cards, `"metric"` for KPI callouts, `"step"` for chronological stages, `"takeaway"` for summary conclusions.

---

# SLIDE-TYPE-SPECIFIC CONTENT GUIDELINES
Adapt content depth and structure to the specific slide archetype:

1. **Hero Title (`hero_title`)**:
   - Keep text minimal and commanding.
   - `headline`: The bold, overarching thesis or presentation title.
   - `subheadline`: Contextual framing sentence explaining the scope.
   - `content_elements`: 2–3 brief briefing points (e.g. Scope, Prepared By, Executive Takeaway).

2. **Introduction & Context Slide**:
   - Frame the macro landscape, current status quo, and why this topic matters right now.
   - Each point must explain a distinct dimension of the background.

3. **Problem & Friction Slide**:
   - Clearly articulate: (1) what the core bottleneck or problem is, (2) why legacy approaches fail, (3) who or what is affected, and (4) quantifiable costs or operational friction.

4. **Solution & Capability Slide**:
   - Detail: (1) core architecture or methodology, (2) operational mechanics (how it works), (3) primary tangible benefits, and (4) implementation prerequisites.

5. **Comparison & Contrast Slide (`split_screen`)**:
   - Structure distinct, direct contrasts across meaningful dimensions (e.g., "Traditional Approach" vs. "Next-Gen Model", or "Before" vs. "After").
   - Avoid trivial labels—compare specific capabilities, latency, cost, or reliability.

6. **Process & Roadmap Slide (`process_timeline`)**:
   - 3–4 sequential steps or milestones.
   - Each element `title` must identify the phase/milestone (e.g., "Phase 1: Diagnostic Ingestion").
   - Each `description` must explain the core action, key deliverable, and success criteria for that step.

7. **Metrics & KPI Slide (`metrics_callout`)**:
   - 3–4 quantitative anchors.
   - Put the metric value in `title` (e.g., "78%", "$1.4T", "3.2x", "45ms").
   - In `description`, provide the benchmark label, context, and practical interpretation.

8. **Conclusion & Strategic Takeaways Slide**:
   - 3–5 high-level synthesis points: key findings, executive recommendations, and immediate next steps.

---

# ADAPTING CONTENT TO SLIDE SPACE
Avoid walls of text or uneven distribution:
- **Hero slide**: Minimal text, maximum impact.
- **Split-screen (2 columns)**: 2–4 balanced points with moderate descriptions.
- **Standard vertical stack (3–4 cards)**: Rich, structured 1–2 sentence explanations.
- **2x2 Feature Grid**: 4 punchy, equal-weight sections.
- **Metrics layout**: Bold numbers + concise contextual interpretation.

---

# ACCURACY & SAFE ESTIMATION RULES
- **No Hallucinations**: Do not invent false companies, fake study authors, or fabricated citations.
- **Mark Uncertain Estimates**: When exact empirical figures are modeled, projected, or unavailable, explicitly denote them as `[Estimated]` or `[Data unavailable]` (e.g., "Market size projected at $45B by 2028 [Estimated]").
- **No Generic Placeholders**: Never write "[Placeholder]", "Add details here", "Lorem Ipsum", or empty filler.

---

# STRICT GUARDRAILS
1. **EXACT SLIDE COUNT**: Produce EXACTLY {number_of_slides} slides. No more, no less.
2. **OUTPUT FORMAT**: Respond ONLY with a valid JSON object enclosed in ```json ... ``` code fences. No preamble, no outro text.
3. **NO GENERIC FILLER**: Every point must be informative, fact-based, and tailored to "{topic}".{desc_requirement}

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
        "background": "#HEX",
        "surface": "#HEX",
        "surface_border": "#HEX",
        "primary_accent": "#HEX",
        "secondary_accent": "#HEX",
        "heading": "#HEX",
        "body": "#HEX",
        "muted": "#HEX"
      }},
      "typography": {{
        "header_font": "Clean font respecting '{font_style}'",
        "body_font": "Clean font respecting '{font_style}'"
      }},
      "logo_specification": "Top-right | None"
    }}
  }},
  "slides": [
    {{
      "slide_number": 1,
      "layout": "hero_title",
      "headline": "Transformative Paradigm in {topic}",
      "subheadline": "An executive analysis of core drivers, market implications, and strategic adoption",
      "content_elements": [
        {{
          "type": "bullet",
          "title": "Core Objective",
          "description": "Establish a unified framework for integrating high-velocity insights into daily operational decision-making."
        }},
        {{
          "type": "bullet",
          "title": "Strategic Focus",
          "description": "Evaluating technical feasibility, economic return, and organizational change requirements across all operational units."
        }}
      ],
      "visual_assets": {{
        "image_prompt": null,
        "recommended_aspect_ratio": "16:9",
        "icon_keyword": "compass"
      }},
      "speaker_notes": "Welcome executive leadership. Today we examine the strategic impact and roadmap for {topic}."
    }},
    {{
      "slide_number": 2,
      "layout": "standard",
      "headline": "Core Drivers Reshaping the Modern Landscape",
      "subheadline": "Three fundamental structural shifts accelerating sector-wide transformation",
      "content_elements": [
        {{
          "type": "bullet",
          "title": "Algorithmic Precision at Scale",
          "description": "Modern architectures process multi-modal signals simultaneously, reducing manual synthesis latency from days to sub-second responses."
        }},
        {{
          "type": "bullet",
          "title": "Accelerating Unit Economics",
          "description": "Inference optimization and dedicated hardware pipelines have compressed compute costs by over 60% [Estimated] year-over-year."
        }},
        {{
          "type": "bullet",
          "title": "Regulatory & Safety Mandates",
          "description": "Emerging compliance standards require auditable governance pipelines, transforming security from a compliance checkpoint into a moat."
        }}
      ],
      "visual_assets": {{
        "image_prompt": null,
        "recommended_aspect_ratio": "16:9",
        "icon_keyword": "trending-up"
      }},
      "speaker_notes": "Slide 2 highlights the three macro forces propelling change. Note the compounding effect of compute efficiency."
    }}
  ]
}}
```

Now generate the COMPLETE {number_of_slides}-slide presentation on "{topic}" adhering strictly to these rich content requirements.
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
