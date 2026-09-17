from typing import Dict, Any, Optional, List
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
    narrative_plan: Optional[List[Dict[str, Any]]] = None,
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
    logo_val = "Top-right corner on header" if logo else "None"
    image_example_val = '"High-impact visual concept description"' if images else "null"
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

    narrative_section = ""
    if narrative_plan:
        plan_lines = ["\n# PRE-APPROVED NARRATIVE ARC (FOLLOW THESE EXACT BEATS & LAYOUTS):"]
        for s in narrative_plan:
            num = s.get("slide_number", "?")
            role = s.get("narrative_role", "Section")
            head = s.get("insight_headline", "")
            lay = s.get("layout", "standard")
            plan_lines.append(f"- Slide {num} [{role}]: Layout '{lay}' — Headline: \"{head}\"")
        narrative_section = "\n".join(plan_lines) + "\n"

    theme_spec_block = _get_theme_spec(theme_selection)

    return f"""
# ROLE & IDENTITY
You are "DeckArchitect AI", a world-class Executive Presentation Designer, Information Architect, and Subject Matter Expert.
Your mission is to produce a COMPLETE, HIGH-IMPACT, slide-by-slide presentation on the given topic — with real facts, insights, empirical trends, and rich visual variety — ready for programmatic rendering into PowerPoint (.pptx).
{narrative_section}
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

For every slide, produce:
1. **Insight-Driven Takeaway Headline**: Formulate a complete, declarative thesis (e.g., "AI Is Shifting Clinical Care Toward Earlier, Personalized Detection" — NEVER a passive label like "Overview", "Impact Metrics", or "Success Stories").
2. **Contextual Subheadline**: 1 concise sentence framing the key insight, mechanism, or market dynamic for the slide.
3. **Appropriate Structured Content for the Slide's Layout Archetype** (detailed below).

---

# SLIDE LAYOUT ARCHETYPES (CHOOSE PURPOSEFULLY & VARY ACROSS DECK)
Every slide MUST use the layout designated in the narrative plan, or select the best fit from these archetypes:

1. **`hero_title` (Presentation Opener)**:
   - Commanding active headline, scoping subheadline, 2–3 brief orientation bullets.

2. **`standard` (Concept / Capabilities Stack)**:
   - 3–4 cards with `title` (short bold heading) and `description` (1–2 concise explanatory sentences with evidence/mechanisms).

3. **`chart` (Quantitative Evidence & Trends)**:
   - When meaningful numerical data or progression exists, provide structured `chart_data`:
     - `chart_type`: `"column"`, `"line"`, or `"donut"`
     - `title`: Chart title
     - `categories`: Array of 3–5 string labels (e.g. `["2023", "2024", "2025 [Est]", "2026 [Est]"]`)
     - `series_name`: Metric description (e.g. `"Market Size ($B)"` or `"Accuracy (%)"`)
     - `values`: Array of 3–5 numeric floats/ints (e.g. `[14.2, 28.5, 62.0, 110.4]`)
     - `key_takeaway`: 1–2 sentence analytical summary explaining what the numbers prove.

4. **`comparison` (Before vs After / Legacy vs Next-Gen)**:
   - Provides structured side-by-side contrast:
     - `left_title`: Legacy / Traditional approach
     - `left_status`: e.g. `"Legacy Bottleneck"`
     - `left_points`: 2–3 bullet points explaining friction
     - `right_title`: Modern / AI-Augmented approach
     - `right_status`: e.g. `"Modern Paradigm"`
     - `right_points`: 2–3 bullet points explaining advantages
     - `takeaway`: Core strategic differentiator sentence

5. **`process_flow` (Roadmap / Architecture Journey)**:
   - Sequential progression of 3–4 chronological phases or milestones:
     - `steps`: Array of 3–4 items with `step_number`, `title` (phase name), `description` (core action), and `deliverable` (concrete outcome/milestone).

6. **`case_study` (Enterprise Proof Point / Real-World Validation)**:
   - Spotlights a concrete application or enterprise example:
     - `organization`: Entity or domain spotlighted
     - `highlight_metric`: Large bold result (e.g. `"+65% Faster"`, `"$4.2M Saved"`)
     - `metric_label`: Metric context
     - `challenge`: 1 sentence explaining the initial problem
     - `solution`: 1 sentence explaining the deployed mechanism
     - `impact`: 1 sentence explaining measurable business outcome
     - `takeaway`: 1 sentence strategic lesson for leadership

7. **`big_statistic` (Quantitative Anchor)**:
   - For an extraordinary data point:
     - `value`: Massive number (e.g. `"$1.4T"`, `"84%"`, `"3.5x"`)
     - `label`: What the metric represents
     - `context`: Benchmark or historical baseline
     - `implication`: Strategic consequence

8. **`key_takeaways` (Executive Synthesis)**:
   - 3–4 high-level strategic takeaways summarizing the entire presentation with clear immediate next steps.

9. **`quote` (Strategic Tenet / Expert Insight)**:
   - `quote_text`: High-impact principle or insight
   - `attribution`: Speaker / Source and role

10. **`references` (Evidence Base & Sources)**:
    - 3–4 external benchmarks or methodology disclosures:
      - `sources`: Array of items with `source_title`, `citation`, and `is_estimated` boolean.

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
      "logo_specification": "{logo_val}"
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
        "image_prompt": {image_example_val},
        "recommended_aspect_ratio": "16:9",
        "icon_keyword": "compass"
      }},
      "speaker_notes": "Welcome executive leadership. Today we examine the strategic impact and roadmap for {topic}."
    }},
    {{
      "slide_number": 2,
      "layout": "chart",
      "headline": "Exponential Compute Efficiency Accelerating Enterprise Adoption",
      "subheadline": "Inference optimization has reduced marginal processing costs by over 70% in 24 months",
      "chart_data": {{
        "chart_type": "column",
        "title": "Normalized Compute Cost per Million Tokens ($)",
        "categories": ["2022", "2023", "2024", "2025 [Est]"],
        "series_name": "Cost ($)",
        "values": [20.0, 6.5, 1.8, 0.45],
        "key_takeaway": "Sub-dollar token economics make real-time multi-agent orchestration viable at enterprise scale."
      }},
      "visual_assets": {{
        "image_prompt": {image_example_val},
        "recommended_aspect_ratio": "16:9",
        "icon_keyword": "bar-chart-2"
      }},
      "speaker_notes": "Slide 2 demonstrates the collapsing cost curve that enables high-frequency autonomous workflows."
    }},
    {{
      "slide_number": 3,
      "layout": "comparison",
      "headline": "Autonomous Agents Shift Workflows from Sequential Batching to Continuous Agency",
      "subheadline": "Comparing operational throughput, human oversight load, and feedback response latency",
      "comparison": {{
        "left_title": "Traditional Workflow Automation",
        "left_status": "Legacy Friction",
        "left_points": [
          "Rigid if-then rule scripts break on ambiguous edge cases",
          "Manual human triaging required for exception handling",
          "Latency measured in hours or days between batch runs"
        ],
        "right_title": "Agentic Reasoning Pipeline",
        "right_status": "Autonomous Advantage",
        "right_points": [
          "Self-correcting feedback loops recover from transient errors",
          "Dynamic tool selection adapts to heterogeneous schema inputs",
          "Sub-second execution with automated audit telemetry"
        ],
        "takeaway": "Autonomy eliminates human bottlenecking on repetitive analytical tasks."
      }},
      "visual_assets": {{
        "image_prompt": {image_example_val},
        "recommended_aspect_ratio": "16:9",
        "icon_keyword": "git-compare"
      }},
      "speaker_notes": "Notice the fundamental shift from brittle hardcoded rules to goal-oriented adaptive execution."
    }}
  ]
}}
```

Now generate the COMPLETE {number_of_slides}-slide presentation on "{topic}" adhering strictly to the planned narrative arc, insight-driven headlines, and rich visual layout requirements.
""".strip()


def prompt_node(state: PresentationState) -> Dict[str, Any]:
    """
    LangGraph Node: Synthesizes user specifications and narrative plan into the structured prompt.
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
        narrative_plan=state.get("narrative_plan"),
    )
    return {"prompt": prompt}

