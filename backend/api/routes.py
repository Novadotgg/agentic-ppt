import os
import re
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from langchain_groq import ChatGroq

from backend.schemas import GeneratePPTRequest, HealthResponse
from backend.agent.graph import presentation_graph
from backend.agent.state import PresentationState
from backend.ppt.generator import create_presentation_file

router = APIRouter(prefix="/api", tags=["Presentation"])


def cleanup_temp_file(file_path: str):
    """Safely removes the generated temporary PPT file after streaming."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass


def sanitize_filename(topic: str) -> str:
    """Creates a clean, safe filename from the topic string."""
    cleaned = re.sub(r"[^\w\s-]", "", topic.lower()).strip()
    cleaned = re.sub(r"[-\s]+", "_", cleaned)
    return cleaned[:50] or "nova_presentation"


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Simple health check endpoint."""
    return HealthResponse(status="ok", service="Nova PPT Gen")


@router.post("/generate-ppt")
def generate_ppt(request: GeneratePPTRequest):
    """
    Generates a PowerPoint presentation using LangGraph & ChatGroq, and returns the .pptx file.
    The Groq API key is request-scoped and never logged, persisted, or stored in state.
    """
    # 1. Instantiate request-scoped LLM (never stored globally or persisted)
    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    try:
        request_llm = ChatGroq(
            groq_api_key=request.groq_api_key,
            model=model_name,
            temperature=0.3,
            max_tokens=8192,
            max_retries=2,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to initialize Groq client with provided key.",
        )

    # 2. Build initial state for LangGraph (without the API key)
    initial_state: PresentationState = {
        "topic": request.topic,
        "description": request.description,
        "number_of_slides": request.number_of_slides,
        "font_style": request.font_style,
        "theme_selection": request.theme_selection,
        "images": request.images,
        "logo": request.logo,
        "notes": request.notes,
    }

    # 3. Execute LangGraph workflow with request-scoped LLM passed via config
    try:
        result_state = presentation_graph.invoke(
            initial_state,
            config={"configurable": {"llm": request_llm}},
        )
    except Exception as e:
        err_str = str(e).lower()
        if "401" in err_str or "unauthorized" in err_str or "invalid_api_key" in err_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Groq API key is invalid or unauthorized.",
            )
        # Surface the real error message for easier debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LangGraph workflow error: {str(e)[:300]}",
        )

    # 4. Check for workflow-level errors
    if result_state.get("error"):
        error_msg = result_state["error"]
        if "unauthorized" in error_msg.lower() or "invalid_api_key" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Groq API key is invalid or unauthorized.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {error_msg}",
        )

    structured_data = result_state.get("structured_output")
    if not structured_data or not structured_data.get("slides"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to produce structured presentation slides.",
        )

    # 5. Generate temporary .pptx file
    try:
        temp_file_path = create_presentation_file(
            presentation_data=structured_data,
            default_topic=request.topic,
            default_font=request.font_style,
            default_theme=request.theme_selection,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create PowerPoint presentation.",
        )

    # 6. Return downloadable FileResponse with background cleanup
    filename = f"{sanitize_filename(request.topic)}.pptx"

    return FileResponse(
        path=temp_file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename,
        background=BackgroundTask(cleanup_temp_file, temp_file_path),
    )
