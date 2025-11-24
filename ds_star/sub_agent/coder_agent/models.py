import re

from pydantic import BaseModel, Field, field_validator


class ExecutableCode(BaseModel):
    code: str = Field(..., description="The Python code to execute.")

    @field_validator("code")
    @classmethod
    def clean_code_block(cls, v: str) -> str:
        # 1. 마크다운 코드 블록 패턴 제거 (```python ... ``` or ``` ... ```)
        # re.DOTALL: .이 개행 문자를 포함하도록 설정
        pattern = r"^```(?:python)?\s*(.*)\s*```$"
        match = re.match(pattern, v.strip(), re.DOTALL)

        if match:
            return match.group(1).strip()

        # 2. 마크다운이 없는 경우 양쪽 공백만 제거 후 반환
        return v.strip()
