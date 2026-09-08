from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from backend.schemas import TaskType

class AgentState(BaseModel):
    user_prompt: str
    task_type: TaskType = TaskType.GENERAL
    selected_model: str = "phi3.5"
    retrieved_context: Optional[str] = None
    generated_draft: Optional[str] = None
    tool_calls: List[str] = Field(default_factory=list)
    execution_result: Optional[Dict[str, Any]] = None
    saved_artifact_path: Optional[str] = None
    error: Optional[str] = None