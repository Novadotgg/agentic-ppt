from langgraph.graph import StateGraph, START, END

from backend.agent.state import PresentationState
from backend.agent.prompt import prompt_node
from backend.agent.groq_node import generate_presentation_node


def build_presentation_graph():
    """
    Assembles and compiles the presentation generation LangGraph workflow:
    START -> generate_prompt -> generate_presentation -> END
    """
    workflow = StateGraph(PresentationState)

    workflow.add_node("generate_prompt", prompt_node)
    workflow.add_node("generate_presentation", generate_presentation_node)

    workflow.add_edge(START, "generate_prompt")
    workflow.add_edge("generate_prompt", "generate_presentation")
    workflow.add_edge("generate_presentation", END)

    return workflow.compile()


presentation_graph = build_presentation_graph()
