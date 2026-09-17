from typing import TypedDict, Optional, Dict, Any


class PresentationState(TypedDict, total=False):
    """
    LangGraph state schema for presentation generation.
    NOTE: Never store API keys or secrets in this state.
    """
    topic: str
    description: Optional[str]
    number_of_slides: int
    font_style: str
    theme_selection: str
    images: bool
    logo: bool
    notes: bool

    prompt: str
    raw_response: str
    structured_output: Optional[Dict[str, Any]]
    error: Optional[str]
