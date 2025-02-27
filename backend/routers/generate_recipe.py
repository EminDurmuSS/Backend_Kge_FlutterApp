from fastapi import APIRouter, HTTPException
import json
from models.schemas import RecommendationRequest
from core.llm_generator import generate_recipe_llm

router = APIRouter()

@router.post("/generate_recipe")
def generate_recipe(request: RecommendationRequest):
    """
    Endpoint that generates a single recipe JSON (with "recipes": [...] ) via LLM.
    """
    recipe = generate_recipe_llm(request.dict())
    try:
        recipe_json = json.loads(recipe)
        return recipe_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing generated recipe: {e}")
