import json
import os
import re
from typing import Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_groq import ChatGroq

from backend.agent.state import PresentationState


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
            pass  # fall through to broader extraction

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


def generate_presentation_node(
    state: PresentationState,
    config: Optional[RunnableConfig] = None,
) -> Dict[str, Any]:
    """
    LangGraph Node 2: Calls request-scoped ChatGroq with prompt and parses JSON.
    NOTE: The LLM instance is passed via config['configurable']['llm'] to guarantee
    that user API keys are request-scoped and never stored in state or logs.
    """
    configurable = config.get("configurable", {}) if config else {}
    llm = configurable.get("llm")

    # Fallback to env key for local CLI testing if no request-scoped LLM is injected
    if not llm:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {
                "error": "Groq API key is missing or not provided in request.",
                "raw_response": "",
                "structured_output": None,
            }
        model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        llm = ChatGroq(
            model=model_name,
            temperature=0.3,
            max_tokens=8192,
            groq_api_key=api_key,
            max_retries=2,
        )

    prompt_content = state.get("prompt", "")

    try:
        response = llm.invoke([
            SystemMessage(content=(
                "You are an expert presentation designer. "
                "Respond ONLY with a single valid JSON object, no prose, no markdown explanation. "
                "Wrap your JSON in ```json ... ``` code fences."
            )),
            HumanMessage(content=prompt_content),
        ])

        raw_text = response.content if hasattr(response, "content") else str(response)
        parsed_json = extract_json(raw_text)

        if not parsed_json:
            # Print to uvicorn terminal so developer can see the raw output
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
        }

    except Exception as e:
        err_str = str(e).lower()
        if "401" in err_str or "unauthorized" in err_str or "invalid_api_key" in err_str or "authentication" in err_str:
            return {
                "error": "Groq API key is invalid or unauthorized.",
                "raw_response": "",
                "structured_output": None,
            }
        if "404" in err_str or "model_not_found" in err_str or "does not exist" in err_str:
            return {
                "error": "Model not found on your Groq account. The default model has been updated — please restart the server.",
                "raw_response": "",
                "structured_output": None,
            }
        return {
            "error": f"Groq error: {str(e)[:400]}",
            "raw_response": "",
            "structured_output": None,
        }
