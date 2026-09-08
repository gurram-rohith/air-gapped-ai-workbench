import re
from typing import Optional
from backend.config import settings
from backend.schemas import TaskType

class TaskRouter:
    """Analyzes incoming prompts to assign the optimal task type and model."""

    # Keywords for rule-based routing
    CODING_KEYWORDS = {
        "code", "python", "script", "function", "debug", "algorithm", 
        "sql", "api", "json", "class", "bug", "syntax", "refactor", "html"
    }
    
    REASONING_KEYWORDS = {
        "calculate", "proof", "derivation", "step-by-step", "analyze", 
        "evaluate", "compare", "logic", "equation", "solve", "formula"
    }

    @classmethod
    def classify_prompt(cls, prompt: str) -> TaskType:
        """Classifies a text prompt into a TaskType."""
        prompt_lower = prompt.lower()
        words = set(re.findall(r'\b\w+\b', prompt_lower))

        if words.intersection(cls.CODING_KEYWORDS):
            return TaskType.CODING
        elif words.intersection(cls.REASONING_KEYWORDS):
            return TaskType.REASONING
        return TaskType.GENERAL

    @classmethod
    def resolve_model(
        cls, 
        prompt: str, 
        task_type: Optional[TaskType] = None, 
        explicit_model: Optional[str] = None
    ) -> tuple[str, TaskType]:
        """Returns the appropriate model tag and resolved task type."""
        if explicit_model:
            return explicit_model, task_type or TaskType.GENERAL

        resolved_task = task_type or cls.classify_prompt(prompt)

        model_map = {
            TaskType.CODING: getattr(settings, "coding_model", "qwen2.5-coder:1.5b"),
            TaskType.VISION: getattr(settings, "vision_model", "moondream"),
            TaskType.REASONING: getattr(settings, "reasoning_model", "phi3.5"),
            TaskType.GENERAL: settings.default_model,
        }

        selected_model = model_map.get(resolved_task, settings.default_model)
        return selected_model, resolved_task