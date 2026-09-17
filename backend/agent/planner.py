"""
Deck Planner Module: Synthesizes user requirements into a structured narrative arc
with insight-driven headlines, diverse layout allocations, and audience-first story beats.
"""
from typing import List, Dict, Any, Optional


NARRATIVE_BEAT_PATTERNS = {
    3: [
        {"role": "Core Thesis & Problem", "layout": "hero_title"},
        {"role": "Breakthrough Solution & Evidence", "layout": "comparison"},
        {"role": "Strategic Impact & Action", "layout": "key_takeaways"},
    ],
    4: [
        {"role": "Executive Briefing", "layout": "hero_title"},
        {"role": "Structural Bottleneck", "layout": "standard"},
        {"role": "Next-Gen Architecture & Evidence", "layout": "chart"},
        {"role": "Strategic Roadmap", "layout": "key_takeaways"},
    ],
    5: [
        {"role": "Opening Executive Thesis", "layout": "hero_title"},
        {"role": "The Friction in Legacy Models", "layout": "standard"},
        {"role": "Paradigm Shift & Mechanism", "layout": "comparison"},
        {"role": "Empirical Performance Gains", "layout": "chart"},
        {"role": "Strategic Takeaways & Next Steps", "layout": "key_takeaways"},
    ],
    6: [
        {"role": "Executive Opener", "layout": "hero_title"},
        {"role": "Macro Problem & Why Current Tools Fail", "layout": "standard"},
        {"role": "Core Solution Architecture", "layout": "comparison"},
        {"role": "Data-Driven Validation & ROI", "layout": "chart"},
        {"role": "Implementation Roadmap & Milestones", "layout": "process_flow"},
        {"role": "Enterprise Synthesis & Next Steps", "layout": "key_takeaways"},
    ],
    7: [
        {"role": "Executive Opener", "layout": "hero_title"},
        {"role": "Macro Problem & Urgency", "layout": "standard"},
        {"role": "Core Solution Architecture", "layout": "comparison"},
        {"role": "Empirical Market / Performance Data", "layout": "chart"},
        {"role": "Deployment Workflow & Phases", "layout": "process_flow"},
        {"role": "Enterprise Case Study & Proof Point", "layout": "case_study"},
        {"role": "Strategic Recommendations", "layout": "key_takeaways"},
    ],
    8: [
        {"role": "Executive Opener", "layout": "hero_title"},
        {"role": "Industry Landscape & Bottlenecks", "layout": "standard"},
        {"role": "The Core Turning Point", "layout": "big_statistic"},
        {"role": "Technical Architecture & Capabilities", "layout": "comparison"},
        {"role": "Empirical Gains & Benchmarks", "layout": "chart"},
        {"role": "Sequential Rollout Roadmap", "layout": "process_flow"},
        {"role": "Real-World Enterprise Case Study", "layout": "case_study"},
        {"role": "Strategic Takeaways & Action Plan", "layout": "key_takeaways"},
    ],
    9: [
        {"role": "Executive Opener", "layout": "hero_title"},
        {"role": "Macro Status Quo & Challenges", "layout": "standard"},
        {"role": "The Breakthrough Catalyst", "layout": "big_statistic"},
        {"role": "Solution Framework & Architecture", "layout": "comparison"},
        {"role": "Empirical Data & Performance Trends", "layout": "chart"},
        {"role": "Phased Implementation Timeline", "layout": "process_flow"},
        {"role": "Enterprise Spotlight / Case Study", "layout": "case_study"},
        {"role": "Strategic Impact & Synthesis", "layout": "key_takeaways"},
        {"role": "Evidence Base & Citations", "layout": "references"},
    ],
    10: [
        {"role": "Executive Opener", "layout": "hero_title"},
        {"role": "Macro Status Quo & Challenges", "layout": "standard"},
        {"role": "The Core Paradigm Shift", "layout": "big_statistic"},
        {"role": "Solution Architecture & Capabilities", "layout": "comparison"},
        {"role": "Empirical Data & Performance Trends", "layout": "chart"},
        {"role": "Phased Implementation Roadmap", "layout": "process_flow"},
        {"role": "Enterprise Spotlight / Case Study", "layout": "case_study"},
        {"role": "Expert Perspective & Core Tenet", "layout": "quote"},
        {"role": "Executive Summary & Next Steps", "layout": "key_takeaways"},
        {"role": "Sources & Methodology", "layout": "references"},
    ],
}


def build_planner_prompt(
    topic: str,
    number_of_slides: int,
    description: Optional[str] = None,
) -> str:
    """
    Generates a planning prompt asking the LLM to structure a narrative storyline
    with insight-driven headlines, clear audience takeaways, and layout archetypes.
    """
    desc_context = f"\nUser Context / Goals: {description.strip()}" if description else ""
    default_beats = NARRATIVE_BEAT_PATTERNS.get(number_of_slides, NARRATIVE_BEAT_PATTERNS[6])

    beats_guide = "\n".join(
        f"Slide {i+1}: Role: {b['role']} | Recommended Layout: {b['layout']}"
        for i, b in enumerate(default_beats)
    )

    return f"""
# ROLE
You are an Executive Presentation Strategist. Before slide writing begins, your job is to craft a cohesive, high-impact narrative arc for a presentation deck.

# TOPIC
"{topic}"{desc_context}

# TARGET SLIDES: {number_of_slides}

# NARRATIVE ARC FRAMEWORK
A great presentation is a story that moves the audience forward:
Problem / Context → Insight → Solution → Evidence → Comparison → Implementation → Impact → Conclusion

Recommended Beat Structure:
{beats_guide}

# CRITICAL REQUIREMENTS
1. **INSIGHT-DRIVEN HEADLINES (MANDATORY)**:
   - Every headline must express a full takeaway or conclusion.
   - BANNED: Passive generic labels like "Impact Metrics", "Success Stories", "Current Bottlenecks", "Overview", "Background".
   - REQUIRED: Active statements like "Legacy Workflows Are Optimized for Batch Processing, Not Real-Time Decisions".

2. **LAYOUT VARIETY**:
   - Assign varied layouts so no two consecutive slides share the same layout.
   - Available layouts: "hero_title", "standard", "comparison", "chart", "process_flow", "case_study", "big_statistic", "quote", "key_takeaways", "references".

3. **AUDIENCE TAKEAWAY**:
   - For every slide, state what the audience actually learns or decides from this slide.

# OUTPUT JSON FORMAT
Enclose your response strictly in ```json ... ``` code fences:
```json
{{
  "deck_thesis": "One-sentence overarching takeaway of the entire presentation",
  "slides": [
    {{
      "slide_number": 1,
      "narrative_role": "Executive Opener",
      "insight_headline": "Active declarative headline",
      "layout": "hero_title",
      "audience_takeaway": "What the audience understands after this slide",
      "has_data_visual": false,
      "chart_type": null
    }}
  ]
}}
```
Generate the complete {number_of_slides}-slide narrative plan now.
""".strip()
