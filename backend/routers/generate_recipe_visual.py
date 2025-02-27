from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json

from models.schemas import RecommendationRequest
from core.recipe_visual import generate_recipe_with_visual

router = APIRouter()

@router.post("/generate_recipe_visual")
def generate_recipe_visual_endpoint(request: RecommendationRequest):
    """
    Endpoint that runs the full LLM+VLM pipeline and returns a final JSON with:
      { "title": ..., "description": ..., "recipe": ..., "image_url": ... }
    """
    try:
        final_output = generate_recipe_with_visual(request.dict())
        # The final output is a JSON string, so parse and return it directly.
        return JSONResponse(content=json.loads(final_output))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
