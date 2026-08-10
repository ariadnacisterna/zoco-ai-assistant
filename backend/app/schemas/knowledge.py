from datetime import datetime

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    FiniteFloat,
    NonNegativeInt,
)

from app.core.enums import ServiceStatus


class ScrapedPage(BaseModel):
    """Public page extracted from the ZOCO website."""

    source_url: AnyHttpUrl
    title: str
    content: str


class KnowledgeChunkCreate(BaseModel):
    """Knowledge chunk prepared for MongoDB."""

    source_url: AnyHttpUrl
    title: str
    content: str
    chunk_index: NonNegativeInt
    updated_at: datetime
    embedding: list[FiniteFloat] = Field(min_length=1)


class RetrievedKnowledgeChunk(BaseModel):
    """Knowledge chunk selected by semantic similarity."""

    source_url: AnyHttpUrl
    title: str
    content: str
    chunk_index: NonNegativeInt
    similarity: FiniteFloat = Field(ge=-1.0, le=1.0)


class KnowledgeUpdateResponse(BaseModel):
    """Response returned after updating the knowledge base."""

    status: ServiceStatus
    pages_processed: NonNegativeInt
    chunks_stored: NonNegativeInt
    updated_at: datetime
