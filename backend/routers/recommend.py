from fastapi import APIRouter, HTTPException
import logging
from models.schemas import RecommendationRequest
from core.recommender import (
    map_user_input_to_criteria,
    get_matching_recipes
)

router = APIRouter()

@router.post("/recommend")
def recommend_recipes(request: RecommendationRequest):
    """
    Endpoint to get top-K recommended recipe IDs based on user criteria.
    """
    try:
        criteria = map_user_input_to_criteria(
            cooking_method=request.cooking_method,
            servings_bin=request.servings_bin,
            diet_types=request.diet_types,
            meal_type=request.meal_type,
            cook_time=request.cook_time,
            health_types=request.health_types,
            cuisine_region=request.cuisine_region,
            ingredients=request.ingredients,
        )
        logging.info(f"Mapped criteria: {criteria}")

        recipe_ids = get_matching_recipes(criteria=criteria, top_k=request.top_k)
        if not recipe_ids:
            raise HTTPException(status_code=404, detail="No matching recipes found.")
        return recipe_ids
    except Exception as e:
        logging.exception("Error in /recommend endpoint")
        raise HTTPException(status_code=500, detail=f"Recommendation error: {e}")
