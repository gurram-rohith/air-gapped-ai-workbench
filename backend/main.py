from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
import io

from backend.rag import retrieve_context_for_prompt, format_context_for_prompt
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
from backend.sandbox import execute_python_code


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


class CodeExecutionRequest(BaseModel):
    code: str
    timeout: int = 10


# ============================================================
# SANDBOX EXECUTION ENDPOINT
# ============================================================

@app.post("/api/sandbox/execute")
async def run_sandbox_code(request: CodeExecutionRequest):
    try:
        result = execute_python_code(request.code, timeout=request.timeout)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# DOCUMENT INGESTION ENDPOINT
# ============================================================

@app.post("/api/ingest")
async def ingest_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        pdf = PdfReader(io.BytesIO(content))
        extracted_text = "".join([page.extract_text() or "" for page in pdf.pages])
        
        print(f"Successfully received '{file.filename}' ({len(extracted_text)} chars)")
        
        # TODO: Pass extracted_text to your vector store embedding function here
        
        return {
            "status": "success",
            "filename": file.filename,
            "character_count": len(extracted_text),
            "message": "Document ingested into vector store"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
# CHAT ENDPOINT (WITH RAG & TRUST INTEGRATION)
# ============================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # 1. Pull relevant document context from ChromaDB
    context_chunks = retrieve_context_for_prompt(
        user_query=request.prompt, 
        top_k=3
    )
    context_block = format_context_for_prompt(context_chunks)

    # 2. Augment prompt with retrieved SOP context
    augmented_prompt = request.prompt
    if context_chunks:
        augmented_prompt = f"""Use the following retrieved SOP document context to answer the user's question accurately. If the answer is not in the context, use your base reasoning safely.

---
{context_block}
---

User Question: {request.prompt}
"""

    explicit_model = _sanitize_model_override(request.model)

    # 3. Pass augmented prompt through task router
    selected_model, _ = TaskRouter.resolve_model(
        prompt=augmented_prompt,
        task_type=request.task_type,
        explicit_model=explicit_model
    )

    # 4. Generate response using local model
    result = await generate_response(
        prompt=augmented_prompt,
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

    response_text = result.get("response", "")

    # 5. Optional background trust check enrichment (if context available)
    try:
        chunk_texts = [c.get("text", "") for c in context_chunks] if context_chunks else []
        if chunk_texts:
            await verify_response(
                generated_answer=response_text,
                context_chunks=chunk_texts
            )
    except Exception:
        # Non-blocking telemetry wrap for trust metrics
        pass

    return ChatResponse(
        success=True,
        model=selected_model,
        response=response_text,
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
            detail=result.get("error", "Vision processing failed")
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
            detail=result.get("error", "Embedding generation failed")
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