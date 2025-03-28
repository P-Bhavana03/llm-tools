from fastapi import APIRouter, HTTPException
from app.core.services import execute_query
from app.models.schemas import ExecuteRequest, ExecuteResponse

router = APIRouter()


@router.post("/execute")
async def execute(request: ExecuteRequest):
    try:

        result = await execute_query(request.prompt)
        return {"result": result}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )
