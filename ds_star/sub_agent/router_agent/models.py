from typing import Literal, Optional

from pydantic import BaseModel, Field


class RouterOutput(BaseModel):
    choice: Literal["Add Plan", "Modify Plan"] = Field(
        ...,
        description="The choice of the plan refinement.",
    )
    plan_number: Optional[int] = Field(
        None,
        description="The number of the plan to modify.",
    )
