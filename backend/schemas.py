from typing import Optional
from pydantic import BaseModel, Field, field_validator


class GeneratePPTRequest(BaseModel):
    groq_api_key: str = Field(
        ...,
        description="User-provided Groq API key (request-scoped, never persisted)",
    )
    topic: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Presentation topic or title",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional detailed description or context for the presentation topic",
    )
    number_of_slides: int = Field(
        default=6,
        ge=3,
        le=10,
        description="Target number of slides (3 to 10)",
    )
    font_style: str = Field(
        default="Modern Sans-Serif",
        max_length=100,
        description="Font style or typography direction",
    )
    theme_selection: str = Field(
        default="Professional Blue",
        max_length=100,
        description="Theme or color style",
    )
    images: bool = Field(
        default=False,
        description="Whether to generate visual asset guidelines/prompts for slides",
    )
    logo: bool = Field(
        default=False,
        description="Whether to include logo placement specifications",
    )
    notes: bool = Field(
        default=True,
        description="Whether to generate speaker notes for each slide",
    )

    @field_validator("groq_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Groq API key cannot be empty.")
        return v

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Topic cannot be empty.")
        return v


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "Nova PPT Gen"
