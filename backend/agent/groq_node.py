import json
import os
import re
from typing import Dict, Any, Optional, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_groq import ChatGroq

from backend.agent.state import PresentationState
from backend.agent.planner import build_planner_prompt, NARRATIVE_BEAT_PATTERNS
from backend.agent.prompt import build_system_prompt
from backend.ppt.generator import create_presentation_file


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts and parses JSON from the LLM response.
    Handles: bare JSON, markdown fences (```json...```), prose before/after JSON.
    """
    cleaned = text.strip()

    # 1. Strip markdown code fences (```json ... ``` or ``` ... ```)
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if fence:
        candidate = fence.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 2. Try the full text as-is
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. Find the outermost { ... } block
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            pass

    return None


def get_llm_instance(config: Optional[RunnableConfig] = None) -> Optional[ChatGroq]:
    """Helper to retrieve the request-scoped LLM from config or fallback to env."""
    configurable = config.get("configurable", {}) if config else {}
    llm = configurable.get("llm")
    if llm:
        return llm

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    DEFAULT_MODEL = "openai/gpt-oss-20b"
    raw_env_model = (os.getenv("GROQ_MODEL") or "").strip().strip("'\"")
    model_name = raw_env_model or DEFAULT_MODEL
    return ChatGroq(
        model=model_name,
        temperature=0.3,
        max_tokens=8192,
        groq_api_key=api_key,
        max_retries=2,
    )


# ──────────────────────────────────────────────────────────────────────────────
# STAGE 1: INPUT VALIDATION NODE
# ──────────────────────────────────────────────────────────────────────────────
def input_validation_node(state: PresentationState) -> Dict[str, Any]:
    """
    Node 1: Validates and sanitizes presentation input parameters.
    """
    topic = str(state.get("topic") or "").strip()
    if not topic:
        return {"error": "Topic cannot be empty."}

    num_slides = int(state.get("number_of_slides") or 6)
    num_slides = max(3, min(10, num_slides))

    theme = state.get("theme_selection") or "Obsidian Emerald"
    font = state.get("font_style") or "Modern Sans-Serif"

    return {
        "topic": topic,
        "number_of_slides": num_slides,
        "theme_selection": theme,
        "font_style": font,
        "validation_result": {"status": "valid", "sanitized_topic": topic},
    }


# ──────────────────────────────────────────────────────────────────────────────
# STAGE 2: DECK PLANNER NODE (NARRATIVE STORY ARC)
# ──────────────────────────────────────────────────────────────────────────────
def deck_planner_node(
    state: PresentationState,
    config: Optional[RunnableConfig] = None,
) -> Dict[str, Any]:
    """
    Node 2: Generates an executive narrative storyline before slide drafting,
    establishing an intentional progression and insight-driven headlines.
    """
    if state.get("error"):
        return {}

    llm = get_llm_instance(config)
    num_slides = state.get("number_of_slides", 6)
    topic = state.get("topic", "Presentation")
    desc = state.get("description")

    # Fallback pattern if LLM fails or is unavailable
    fallback_pattern = NARRATIVE_BEAT_PATTERNS.get(num_slides, NARRATIVE_BEAT_PATTERNS[6])
    fallback_plan = [
        {
            "slide_number": i + 1,
            "narrative_role": b["role"],
            "insight_headline": f"{b['role']} in {topic}",
            "layout": b["layout"],
            "audience_takeaway": f"Understand the strategic significance of {b['role'].lower()}",
            "has_data_visual": b["layout"] == "chart",
            "chart_type": "column" if b["layout"] == "chart" else None,
        }
        for i, b in enumerate(fallback_pattern)
    ]

    if not llm:
        return {"narrative_plan": fallback_plan}

    prompt = build_planner_prompt(
        topic=topic,
        number_of_slides=num_slides,
        description=desc,
    )

    try:
        response = llm.invoke([
            SystemMessage(content="You are an Executive Presentation Strategist. Respond ONLY with valid JSON in ```json ... ``` code fences."),
            HumanMessage(content=prompt),
        ])
        raw_text = response.content if hasattr(response, "content") else str(response)
        parsed = extract_json(raw_text)

        if parsed and isinstance(parsed.get("slides"), list) and len(parsed["slides"]) == num_slides:
            return {"narrative_plan": parsed["slides"]}
    except Exception as e:
        print(f"[DeckPlanner Warning] Planning failed: {e}. Falling back to default pattern.")

    return {"narrative_plan": fallback_plan}


# ──────────────────────────────────────────────────────────────────────────────
# STAGE 3: CONTENT GENERATOR NODE
# ──────────────────────────────────────────────────────────────────────────────
def content_generator_node(
    state: PresentationState,
    config: Optional[RunnableConfig] = None,
) -> Dict[str, Any]:
    """
    Node 3: Generates full structured slide content adhering to the narrative arc.
    """
    if state.get("error"):
        return {}

    llm = get_llm_instance(config)
    if not llm:
        return {"error": "Groq API key is missing or invalid."}

    prompt = build_system_prompt(
        topic=state.get("topic", "Presentation"),
        number_of_slides=state.get("number_of_slides", 6),
        font_style=state.get("font_style", "Modern Sans-Serif"),
        theme_selection=state.get("theme_selection", "Obsidian Emerald"),
        images=state.get("images", False),
        logo=state.get("logo", False),
        notes=state.get("notes", True),
        description=state.get("description"),
        narrative_plan=state.get("narrative_plan"),
    )

    try:
        response = llm.invoke([
            SystemMessage(content=(
                "You are an expert presentation designer. "
                "Respond ONLY with a single valid JSON object, no prose, no markdown explanation. "
                "Wrap your JSON in ```json ... ``` code fences."
            )),
            HumanMessage(content=prompt),
        ])

        raw_text = response.content if hasattr(response, "content") else str(response)
        parsed_json = extract_json(raw_text)

        if not parsed_json:
            print("\n[DEBUG] Raw LLM response (JSON parse failed):\n", raw_text[:2000], "\n")
            return {
                "error": "Failed to parse presentation JSON from LLM response.",
                "raw_response": raw_text,
                "structured_output": None,
            }

        return {
            "error": None,
            "raw_response": raw_text,
            "structured_output": parsed_json,
            "prompt": prompt,
        }

    except Exception as e:
        err_str = str(e).lower()
        if "401" in err_str or "unauthorized" in err_str or "invalid_api_key" in err_str:
            return {"error": "Groq API key is invalid or unauthorized."}
        return {"error": f"Groq error: {str(e)[:400]}"}


# ──────────────────────────────────────────────────────────────────────────────
# STAGE 4: VISUAL & LAYOUT PLANNER NODE
# ──────────────────────────────────────────────────────────────────────────────
def visual_layout_planner_node(state: PresentationState) -> Dict[str, Any]:
    """
    Node 4: Inspects generated slide content and ensures layout archetypes
    are appropriately assigned and varied to prevent visual monotony.
    """
    structured = state.get("structured_output")
    if not structured or not isinstance(structured.get("slides"), list):
        return {}

    slides = structured["slides"]
    prev_layout = None

    for i, slide in enumerate(slides):
        current_layout = (slide.get("layout") or "standard").lower()

        # 1. Content-based archetype detection
        if slide.get("chart_data") and isinstance(slide["chart_data"], dict):
            cd = slide["chart_data"]
            if cd.get("categories") and cd.get("values"):
                slide["layout"] = "chart"
                current_layout = "chart"

        elif slide.get("comparison") and isinstance(slide["comparison"], dict):
            slide["layout"] = "comparison"
            current_layout = "comparison"

        elif slide.get("process_flow") or (isinstance(slide.get("steps"), list) and len(slide["steps"]) >= 2):
            slide["layout"] = "process_flow"
            current_layout = "process_flow"

        elif slide.get("case_study") and isinstance(slide["case_study"], dict):
            slide["layout"] = "case_study"
            current_layout = "case_study"

        elif slide.get("big_statistic") and isinstance(slide["big_statistic"], dict):
            slide["layout"] = "big_statistic"
            current_layout = "big_statistic"

        elif slide.get("takeaways") and isinstance(slide["takeaways"], list):
            slide["layout"] = "key_takeaways"
            current_layout = "key_takeaways"

        elif slide.get("sources") and isinstance(slide["sources"], list):
            slide["layout"] = "references"
            current_layout = "references"

        elif i == 0:
            slide["layout"] = "hero_title"
            current_layout = "hero_title"

        # 2. Prevent consecutive identical card layouts (except hero opener)
        if i > 0 and current_layout == prev_layout and current_layout == "standard":
            # If standard cards follow standard cards, alternate to 2x2 grid
            elements = slide.get("content_elements", [])
            if len(elements) == 4:
                slide["layout"] = "feature_grid"
            elif len(elements) == 3:
                slide["layout"] = "three_column"

        prev_layout = slide.get("layout")

    return {"structured_output": structured}


# ──────────────────────────────────────────────────────────────────────────────
# STAGE 5: QUALITY REVIEWER & REFINEMENT NODE
# ──────────────────────────────────────────────────────────────────────────────
BANNED_PASSIVE_TITLES = [
    "impact metrics",
    "success stories",
    "current bottlenecks",
    "overview",
    "background",
    "introduction",
    "key takeaways",
    "challenges",
    "next steps",
    "conclusion",
]


def quality_reviewer_node(state: PresentationState) -> Dict[str, Any]:
    """
    Node 5: Validates deck quality, upgrades passive/generic headlines,
    enforces slide count, and checks data visualization integrity.
    """
    structured = state.get("structured_output")
    if not structured or not isinstance(structured.get("slides"), list):
        return {}

    slides = structured["slides"]
    target_count = state.get("number_of_slides", len(slides))
    review_notes: List[str] = []

    # 1. Verify Slide Count
    if len(slides) > target_count:
        review_notes.append(f"Trimmed extra slides from {len(slides)} to {target_count}")
        slides = slides[:target_count]
        structured["slides"] = slides

    # 2. Review and Upgrade Passive Headlines
    for i, slide in enumerate(slides):
        headline = str(slide.get("headline") or "").strip()
        lower_head = headline.lower().strip(".:- ")

        if any(banned == lower_head or lower_head.startswith(banned + ":") for banned in BANNED_PASSIVE_TITLES):
            # Attempt to derive an insight headline from subheadline or first point
            sub = str(slide.get("subheadline") or "").strip()
            elements = slide.get("content_elements", [])
            first_title = elements[0].get("title") if elements and isinstance(elements, list) else None

            new_headline = ""
            if sub and len(sub) > 15:
                new_headline = sub.rstrip(".")
            elif first_title and len(first_title) > 8:
                new_headline = f"Strategic Imperative: {first_title}"
            else:
                new_headline = f"{headline}: Drivers and Strategic Implications"

            review_notes.append(f"Upgraded passive headline on Slide {i+1} from '{headline}' to '{new_headline}'")
            slide["headline"] = new_headline

    # 3. Review Chart Data Integrity
    for i, slide in enumerate(slides):
        if slide.get("layout") == "chart" and slide.get("chart_data"):
            cd = slide["chart_data"]
            cats = cd.get("categories", [])
            vals = cd.get("values", [])
            # Align categories and values length
            if len(cats) != len(vals):
                min_len = min(len(cats), len(vals))
                if min_len >= 2:
                    cd["categories"] = cats[:min_len]
                    cd["values"] = vals[:min_len]
                    review_notes.append(f"Aligned chart series length on Slide {i+1} to {min_len} items")
                else:
                    # Fallback to standard cards if chart data is malformed
                    slide["layout"] = "standard"
                    review_notes.append(f"Converted malformed chart on Slide {i+1} to standard layout")

    return {
        "structured_output": structured,
        "review_notes": review_notes,
    }


# ──────────────────────────────────────────────────────────────────────────────
# STAGE 6: PPT GENERATOR NODE
# ──────────────────────────────────────────────────────────────────────────────
def ppt_generator_node(state: PresentationState) -> Dict[str, Any]:
    """
    Node 6: Compiles the reviewed structured JSON into a presentation file (.pptx).
    """
    structured = state.get("structured_output")
    if not structured or state.get("error"):
        return {}

    try:
        temp_path = create_presentation_file(
            presentation_data=structured,
            default_topic=state.get("topic", "Presentation"),
            default_font=state.get("font_style", "Modern Sans-Serif"),
            default_theme=state.get("theme_selection", "Obsidian Emerald"),
            has_logo=state.get("logo", False),
            has_images=state.get("images", False),
        )
        return {"ppt_file_path": temp_path}
    except Exception as e:
        return {"error": f"Failed to compile PowerPoint file: {str(e)[:300]}"}
