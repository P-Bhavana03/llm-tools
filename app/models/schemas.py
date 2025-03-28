from pydantic import BaseModel


class ExecuteRequest(BaseModel):
    prompt: str


class ExecuteResponse(BaseModel):
    result: list[str]
