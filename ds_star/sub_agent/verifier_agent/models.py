from pydantic import BaseModel, Field


class IsEnough(BaseModel):
    result: bool = Field(
        ...,
        description="Whether the current plan and its code implementation is enough to answer the question.",
    )
