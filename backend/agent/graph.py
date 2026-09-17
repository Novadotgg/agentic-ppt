from langgraph.graph import StateGraph, START, END

from backend.agent.state import PresentationState
from backend.agent.groq_node import (
    input_validation_node,
    deck_planner_node,
    content_generator_node,
    visual_layout_planner_node,
    quality_reviewer_node,
    ppt_generator_node,
)


def build_presentation_graph():
    """
    Assembles and compiles the 6-stage presentation generation LangGraph workflow:
    START
      ↓
    input_validation
      ↓
    deck_planner (Narrative Story Arc)
      ↓
    content_generator (Insight-Driven Slide Content)
      ↓
    visual_layout_planner (Archetype & Variety Allocation)
      ↓
    quality_reviewer (Quality Review & Refinement)
      ↓
    ppt_generator (PowerPoint Compilation)
      ↓
    END
    """
    workflow = StateGraph(PresentationState)

    workflow.add_node("input_validation", input_validation_node)
    workflow.add_node("deck_planner", deck_planner_node)
    workflow.add_node("content_generator", content_generator_node)
    workflow.add_node("visual_layout_planner", visual_layout_planner_node)
    workflow.add_node("quality_reviewer", quality_reviewer_node)
    workflow.add_node("ppt_generator", ppt_generator_node)

    workflow.add_edge(START, "input_validation")
    workflow.add_edge("input_validation", "deck_planner")
    workflow.add_edge("deck_planner", "content_generator")
    workflow.add_edge("content_generator", "visual_layout_planner")
    workflow.add_edge("visual_layout_planner", "quality_reviewer")
    workflow.add_edge("quality_reviewer", "ppt_generator")
    workflow.add_edge("ppt_generator", END)

    return workflow.compile()


presentation_graph = build_presentation_graph()
