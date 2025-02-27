from pydantic import BaseModel, Field
from typing import List, Optional

# Ingredient schema
class Ingredient(BaseModel):
    id: str
    name: str
    amount: str
    unit: str
    notes: Optional[str] = None
    category: Optional[str] = None
    amountInGrams: Optional[float] = None

# Recipe step schema
class RecipeStep(BaseModel):
    title: str
    description: str
    duration: int  # minutes

# Nutrition info schema
class NutritionInfo(BaseModel):
    calories: int
    protein: float
    carbohydrates: float
    fat: float
    saturatedFat: float
    transFat: float
    cholesterol: float
    sodium: float
    fiber: float
    sugars: float
    vitaminD: float
    calcium: float
    iron: float
    potassium: float
    fatDailyValue: float
    saturatedFatDailyValue: float
    cholesterolDailyValue: float
    sodiumDailyValue: float
    carbohydratesDailyValue: float
    fiberDailyValue: float
    proteinDailyValue: float
    vitaminDDailyValue: float
    calciumDailyValue: float
    ironDailyValue: float
    potassiumDailyValue: float
    servingSize: str

# Full recipe schema
class RecipeInfo(BaseModel):
    id: str
    title: str
    description: str
    imageUrl: str
    cookingTime: int
    servings: int
    calories: int
    difficulty: str
    categories: List[str]
    cookingMethod: str
    ingredients: List[Ingredient]
    steps: List[RecipeStep]
    rating: float
    reviews: int
    userId: str
    userName: str
    createdAt: str  # ISO8601
    nutritionInfo: NutritionInfo

# Response model expecting a "recipes" array
class RecipeResponse(BaseModel):
    recipes: List[RecipeInfo]
# Request model for recommendations
class RecommendationRequest(BaseModel):
    cooking_method: Optional[str] = None
    servings_bin: Optional[str] = None
    diet_types: List[str] = []
    meal_type: List[str] = []
    cook_time: Optional[str] = None
    # health_types will be combined from separate protein and carb selects:
    health_types: List[str] = []
    cuisine_region: Optional[str] = None
    ingredients: List[str] = []
    top_k: int = 5
