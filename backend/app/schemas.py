from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


def strip_non_empty(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("Value cannot be blank")
    return stripped


class NotebookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return strip_non_empty(value)


class NotebookUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=120)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return strip_non_empty(value)


class NotebookResponse(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str


class SourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    content: str = Field(min_length=1)

    @field_validator("title", "content")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return strip_non_empty(value)


class SourceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    enabled: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return strip_non_empty(value)

    @model_validator(mode="after")
    def require_change(self) -> "SourceUpdate":
        if self.title is None and self.enabled is None:
            raise ValueError("Provide title or enabled")
        return self


class SourceResponse(BaseModel):
    id: int
    notebook_id: int
    title: str
    type: str
    status: str
    enabled: bool
    error: str | None
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: int
    notebook_id: int
    role: str
    content: str
    citations: list[dict[str, Any]]
    created_at: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        return strip_non_empty(value)


class ChatResponse(BaseModel):
    answer: str
    citations: list[dict[str, Any]]
    user_message: MessageResponse
    assistant_message: MessageResponse
