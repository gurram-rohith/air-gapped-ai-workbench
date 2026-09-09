from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# --- Task Routing Enums ---
class TaskType(str, Enum):
    GENERAL = "general"
    REASONING = "reasoning"
    CODING = "coding"
    VISION = "vision"

# --- Gateway & Core Inference Schemas ---
class ChatRequest(BaseModel):
    prompt: str = Field(..., description="User prompt or question")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    
    # Optional overrides hidden from default Swagger examples by setting default=None
    task_type: Optional[TaskType] = Field(None, description="Optional manual task override")
    model: Optional[str] = Field(None, description="Optional manual model override")

class ChatResponse(BaseModel):
    success: bool
    model: str
    response: str
    done: bool = True
    error: Optional[str] = None

# --- Embeddings Schemas (For Dev 3 / RAG) ---
class EmbeddingRequest(BaseModel):
    text: str = Field(..., description="Text content to generate embeddings for")
    model: Optional[str] = Field("nomic-embed-text", description="Target embedding model")

class EmbeddingResponse(BaseModel):
    success: bool
    embedding: List[float]
    dimension: int
    model: str
    error: Optional[str] = None

# --- Vision Schemas ---
class VisionAnalysisRequest(BaseModel):
    prompt: str = Field("Describe this image in detail.", description="Question or prompt about the image")
    image_base64: str = Field(..., description="Base64-encoded image string")
    model: Optional[str] = Field("moondream", description="Target vision model")

class VisionAnalysisResponse(BaseModel):
    success: bool
    model: str
    response: str
    error: Optional[str] = None

# --- RAG Pipeline Schemas (For Dev 3) ---
class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = Field(3, description="Number of context chunks to retrieve")

class RAGQueryResponse(BaseModel):
    query: str
    retrieved_chunks: List[str]
    generated_answer: str

# --- Code Sandbox Schemas (For Dev 4) ---
class SandboxExecutionRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = Field(5, description="Execution timeout in seconds")

class SandboxExecutionResponse(BaseModel):
    success: bool
    output: str
    execution_time_ms: float
    error: Optional[str] = None

# --- Trust Layer Schemas (For Dev 5) ---
class GroundingVerificationRequest(BaseModel):
    answer: str
    source_contexts: List[str]

class GroundingVerificationResponse(BaseModel):
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    is_grounded: bool
    unsupported_claims: List[str] = []