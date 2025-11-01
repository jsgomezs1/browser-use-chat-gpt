"""Pydantic models for ChatGPT Browser Agent."""

from pydantic import BaseModel, Field
from typing import List


class Source(BaseModel):
    """Model for a source citation."""
    url: str = Field(description="The URL of the source")
    order: int = Field(description="The order of appearance of the source")


class ChatGPTResponse(BaseModel):
    """Structured output model for ChatGPT responses."""
    response: str = Field(
        description="The complete ChatGPT response text, preserving all formatting, markdown, line breaks, etc."
    )
    sources: List[Source] = Field(
        description="An ordered list of the sources cited in the answer, preserving their order of appearance. Empty array if no sources provided."
    )


class PromptRequest(BaseModel):
    """Request model for the API endpoint."""
    prompt: str = Field(
        ...,
        description="The prompt to submit to ChatGPT",
        min_length=1,
        max_length=10000
    )
