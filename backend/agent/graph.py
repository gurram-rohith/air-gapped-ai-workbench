import re
from typing import Optional
from backend.agent.state import AgentState
from backend.core.router import TaskRouter
from backend.core.ollama_client import generate_response
from backend.schemas import TaskType

class AgentEngine:
    """Core state machine that coordinates prompt routing and model execution."""

    @classmethod
    async def run(
        cls, 
        prompt: str, 
        task_type: Optional[TaskType] = None, 
        explicit_model: Optional[str] = None
    ) -> AgentState:
        
        # 1. Automatic Model & Task Resolution
        selected_model, resolved_task = TaskRouter.resolve_model(
            prompt=prompt, 
            task_type=task_type, 
            explicit_model=explicit_model
        )

        state = AgentState(
            user_prompt=prompt,
            task_type=resolved_task,
            selected_model=selected_model
        )

        # 2. Local GPU Generation Step
        response_data = await generate_response(
            prompt=prompt, 
            model=selected_model
        )
        
        if not response_data.get("success"):
            state.error = response_data.get("error", "Inference server error")
            return state

        state.generated_draft = response_data.get("response", "")

        # 3. Code Parsing & Tool Triggering (Ready for Dev 4's Sandbox)
        if state.task_type == TaskType.CODING:
            code_match = re.search(r"```python\n(.*?)```", state.generated_draft, re.DOTALL)
            if code_match:
                state.tool_calls.append("sandbox.execute_python_code")

        return state