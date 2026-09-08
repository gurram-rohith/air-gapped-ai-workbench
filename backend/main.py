from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.schemas import (
    ChatRequest,
    ChatResponse,
    VisionAnalysisRequest,
    VisionAnalysisResponse,
    EmbeddingRequest,
    EmbeddingResponse
)

from backend.core.ollama_client import (
    generate_response,
    analyze_image,
    generate_embeddings
)

from backend.core.router import TaskRouter
from backend.agent.graph import AgentEngine

# ============================================================
# TRUST LAYER IMPORTS
# ============================================================

from backend.trust_layer.trust_service import verify_response
from backend.trust_layer.approval_queue import (
    get_approval_request,
    review_approval_request
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Air-Gapped AI Workbench Gateway",
    description="Centralized local inference gateway, agent loop, tool router, and Trust Layer.",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "gateway_ip": "192.168.137.212",
        "message": "Air-Gapped AI Workbench Gateway active on RTX 3050"
    }


# ============================================================
# MODEL OVERRIDE SANITIZATION
# ============================================================

def _sanitize_model_override(model_str: str | None) -> str | None:
    if model_str and model_str.strip().lower() != "string":
        return model_str.strip()

    return None


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):

    explicit_model = _sanitize_model_override(request.model)

    selected_model, _ = TaskRouter.resolve_model(
        prompt=request.prompt,
        task_type=request.task_type,
        explicit_model=explicit_model
    )

    result = await generate_response(
        prompt=request.prompt,
        model=selected_model,
        temperature=request.temperature
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=503,
            detail=result.get(
                "error",
                f"Inference server error on model '{selected_model}'"
            )
        )

    return ChatResponse(
        success=True,
        model=selected_model,
        response=result.get("response", ""),
        done=result.get("done", True)
    )


# ============================================================
# VISION ENDPOINT
# ============================================================

@app.post("/api/vision", response_model=VisionAnalysisResponse)
async def vision_endpoint(request: VisionAnalysisRequest):

    result = await analyze_image(
        prompt=request.prompt,
        image_base64=request.image_base64,
        model=request.model
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=503,
            detail=result.get(
                "error",
                "Vision processing failed"
            )
        )

    return VisionAnalysisResponse(
        success=True,
        model=result.get("model", "moondream"),
        response=result.get("response", "")
    )


# ============================================================
# EMBEDDINGS ENDPOINT
# ============================================================

@app.post("/api/embeddings", response_model=EmbeddingResponse)
async def embeddings_endpoint(request: EmbeddingRequest):

    result = await generate_embeddings(
        text=request.text,
        model=request.model
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=503,
            detail=result.get(
                "error",
                "Embedding generation failed"
            )
        )

    return EmbeddingResponse(
        success=True,
        embedding=result.get("embedding", []),
        dimension=result.get("dimension", 0),
        model=result.get("model", "nomic-embed-text")
    )


# ============================================================
# AGENT ENDPOINT
# ============================================================

@app.post("/api/agent/run")
async def run_agent_endpoint(request: ChatRequest):

    explicit_model = _sanitize_model_override(request.model)

    state = await AgentEngine.run(
        prompt=request.prompt,
        task_type=request.task_type,
        explicit_model=explicit_model
    )

    if state.error:
        raise HTTPException(
            status_code=503,
            detail=state.error
        )

    return {
        "user_prompt": state.user_prompt,
        "task_type": (
            state.task_type.value
            if hasattr(state.task_type, "value")
            else state.task_type
        ),
        "selected_model": state.selected_model,
        "generated_draft": state.generated_draft,
        "tool_calls": state.tool_calls,
        "execution_result": state.execution_result,
        "saved_artifact_path": state.saved_artifact_path
    }


# ============================================================
# TRUST LAYER MODELS
# ============================================================

class TrustVerificationRequest(BaseModel):
    generated_answer: str
    context_chunks: list[str]


class HumanReviewRequest(BaseModel):
    decision: str
    reviewer: str


# ============================================================
# TRUST LAYER - VERIFY GROUNDING
# ============================================================

@app.post("/trust/verify")
async def trust_verify(request: TrustVerificationRequest):

    result = await verify_response(
        generated_answer=request.generated_answer,
        context_chunks=request.context_chunks
    )

    return result


# ============================================================
# HUMAN APPROVAL - GET REQUEST
# ============================================================

@app.get("/approval/{request_id}")
async def get_approval(request_id: str):

    request = get_approval_request(request_id)

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found."
        )

    return request


# ============================================================
# HUMAN APPROVAL - REVIEW REQUEST
# ============================================================

@app.post("/approval/{request_id}/review")
async def review_approval(
    request_id: str,
    review: HumanReviewRequest
):

    result = review_approval_request(
        request_id=request_id,
        decision=review.decision,
        reviewer=review.reviewer
    )

    if "error" in result:
        raise HTTPException(
            status_code=400,
            detail=result["error"]
        )

    return result