from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl

from app.llm.anthropic_provider import AnthropicProvider
from app.llm.dependencies import get_anthropic_provider
from app.llm.exceptions import LLMClassificationError, LLMFetchError
from app.llm.schemas import PatchNoteClassification

router = APIRouter()


class ClassifyRequest(BaseModel):
    url: HttpUrl


@router.post("/classify", response_model=PatchNoteClassification)
async def classify(
    request: ClassifyRequest,
    provider: AnthropicProvider = Depends(get_anthropic_provider),
) -> PatchNoteClassification:
    try:
        return await provider.fetch_and_classify(str(request.url))
    except LLMFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except LLMClassificationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
