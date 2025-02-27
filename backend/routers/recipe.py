from fastapi import APIRouter, HTTPException
from core.recommender import fetch_recipe_info

router = APIRouter()

@router.get("/recipe/{recipe_id}")
def get_recipe_by_id(recipe_id: str):
    """
    Returns the raw CSV row matching the requested RecipeId (int).
    """
    info = fetch_recipe_info(recipe_id)
    if not info:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    return info
