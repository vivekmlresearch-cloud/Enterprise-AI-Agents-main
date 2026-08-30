from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ActionResult


class ExecuteActionRequest(BaseModel):
    action_type: Literal['email', 'slack', 'pagerduty', 'webhook']
    title: str
    message: str
    recipient: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False


class ExecuteActionResponse(ActionResult):
    pass
