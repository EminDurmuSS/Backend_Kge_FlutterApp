import json
from core.llm_session import chat_session
from core.recommender import map_user_input_to_criteria, get_matching_recipes, fetch_recipe_info

def format_recipe_example(recipe: dict) -> str:
    """
    Format a recipe dictionary to display certain keys as an example for the LLM prompt.
    """
    keys = [
        "Name", "Description", "RecipeCategory", "Keywords", "RecipeInstructions",
        "cook_time", "Healthy_Type", "Diet_Types", "meal_type", "ScrapedIngredients",
        "CuisineRegion", "Cooking_Method", "servings_bin"
    ]
    output_lines = []
    for key in keys:
        value = recipe.get(key, "Not provided")
        output_lines.append(f"{key}: {value}")
    return "\n".join(output_lines)

def format_user_criteria(criteria: dict) -> str:
    lines = []
    lines.append("User Criteria:")

    cooking_method = criteria.get("cooking_method", [])
    if isinstance(cooking_method, list):
        lines.append(f"  - Cooking Method(s): {', '.join(cooking_method) or 'Any'}")
    else:
        lines.append(f"  - Cooking Method(s): {cooking_method or 'Any'}")

    lines.append(f"  - Cuisine Region: {criteria.get('cuisine_region', 'Any')}")

    diet_types = criteria.get("diet_types", [])
    if isinstance(diet_types, list):
        lines.append(f"  - Diet Types: {', '.join(diet_types) or 'Any'}")
    else:
        lines.append(f"  - Diet Types: {diet_types or 'Any'}")

    meal_type = criteria.get("meal_type", [])
    if isinstance(meal_type, list):
        lines.append(f"  - Meal Types: {', '.join(meal_type) or 'Any'}")
    else:
        lines.append(f"  - Meal Types: {meal_type or 'Any'}")

    # Include cook time and servings for the LLM prompt (but not for KG matching)
    lines.append(f"  - Cooking Time: {criteria.get('cook_time', 'Any time')}")
    lines.append(f"  - Servings: {criteria.get('servings_bin', 'Any servings')}")

    ingredients = criteria.get("ingredients", [])
    if isinstance(ingredients, list):
        lines.append(f"  - Ingredients: {', '.join(ingredients) or 'None specified'}")
    else:
        lines.append(f"  - Ingredients: {ingredients or 'None specified'}")

    health_types = criteria.get("health_types", [])
    if isinstance(health_types, list):
        lines.append(f"  - Health Types: {', '.join(health_types) or 'Any'}")
    else:
        lines.append(f"  - Health Types: {health_types or 'Any'}")

    return "\n".join(lines)



def generate_recipe_llm(user_criteria: dict) -> str:
    """
    Generate a new recipe using the LLM based on user criteria + 5 example recipes for inspiration.
    Returns a JSON string containing { "recipes": [ {...}, ... ] }.
    """
    criteria = map_user_input_to_criteria(
        cooking_method=user_criteria.get("cooking_method", ""),
        servings_bin=user_criteria.get("servings_bin", ""),
        diet_types=user_criteria.get("diet_types", []),
        meal_type=user_criteria.get("meal_type", []),
        cook_time=user_criteria.get("cook_time", ""),
        health_types=user_criteria.get("health_types", []),
        cuisine_region=user_criteria.get("cuisine_region", ""),
        ingredients=user_criteria.get("ingredients", [])
    )

    # Retrieve up to 5 sample recipe IDs using the KGE model
    example_recipe_ids = get_matching_recipes(criteria=criteria, top_k=5, flexible=False)
    
    # Fetch detailed info for the sample recipes
    example_recipes = []
    for rid in example_recipe_ids:
        recipe_info = fetch_recipe_info(rid)
        if recipe_info:
            example_recipes.append(recipe_info)

    # Format the example recipes for the prompt
    formatted_examples = ""
    for idx, recipe in enumerate(example_recipes, start=1):
        formatted_examples += f"Example Recipe {idx}:\n{format_recipe_example(recipe)}\n{'-'*40}\n"

    formatted_criteria = format_user_criteria(user_criteria)

    # Construct final LLM prompt
    prompt = f"""
You are a world-class culinary expert and innovative chef known for your exceptionally creative dishes.
Your task is to generate a completely new recipe that meets the following criteria:

{formatted_criteria}

Use the following example recipes for inspiration:
{formatted_examples}

Output a single JSON object with a top-level key "recipes". This key should map
to an array containing exactly one recipe object with these keys (and no extra keys):

- "id": A unique identifier (can be empty)
- "title": A creative and enticing recipe title
- "description": A vivid and imaginative description 
- "imageUrl": The final image URL of the dish
- "cookingTime": Total cooking time (minutes)
- "servings": Number of servings
- "calories": Calorie count
- "difficulty": Recipe difficulty (Easy, Medium, Hard)
- "categories": An array of category strings
- "cookingMethod": The cooking method used
- "ingredients": An array of ingredient objects
- "steps": An array of instruction objects
- "nutritionInfo": An object containing nutritional details

Example JSON:
{{
  "recipes": [
    {{
      "id": "",
      "title": "Example Recipe Title",
      "description": "A brief creative description incorporating.",
      "cookingTime": 45,
      "servings": 4,
      "calories": 500,
      "difficulty": "Medium",
      "categories": ["Example", "Inspiration"],
      "cookingMethod": "baking",
      "ingredients": [
        {{
          "name": "Ingredient 1",
          "amount": "1",
          "unit": "cup",
          "notes": "",
          "category": "Category",
          "amountInGrams": 100
        }}
      ],
      "steps": [
        {{
          "title": "Step 1",
          "description": "Do something.",
          "duration": 10
        }}
      ],
      "nutritionInfo": {{
        "calories": 500,
        "protein": 20,
        "carbohydrates": 50,
        "fat": 10,
        "saturatedFat": 2,
        "transFat": 0,
        "cholesterol": 0,
        "sodium": 300,
        "fiber": 5,
        "sugars": 8,
        "vitaminD": 0,
        "calcium": 100,
        "iron": 5,
        "potassium": 400,
        "fatDailyValue": 15,
        "saturatedFatDailyValue": 10,
        "cholesterolDailyValue": 0,
        "sodiumDailyValue": 13,
        "carbohydratesDailyValue": 20,
        "fiberDailyValue": 25,
        "proteinDailyValue": 30,
        "vitaminDDailyValue": 0,
        "calciumDailyValue": 10,
        "ironDailyValue": 15,
        "potassiumDailyValue": 12,
        "servingSize": "1 serving"
      }}
    }}
  ]
}}
Now, please generate the recipe.
"""
    print("---- Prompt Sent to Gemini LLM ----")
    print(prompt)
    print("---- End of Prompt ----\n")

    response = chat_session.send_message(prompt)
    raw_text = response.text.strip()
    print("Gemini response text:", repr(raw_text))

    # Remove leading/trailing code fences if any
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        json_text = "\n".join(lines).strip()
    else:
        json_text = raw_text

    if not json_text:
        # fallback JSON if LLM returns nothing
        fallback = {
            "recipes": [
                {
                    "id": "",
                    "title": "No Recipe Generated",
                    "description": "The language model did not return a recipe. Please try again.",
                    "imageUrl": "",
                    "cookingTime": 0,
                    "servings": 0,
                    "calories": 0,
                    "difficulty": "",
                    "categories": [],
                    "cookingMethod": "",
                    "ingredients": [],
                    "steps": [],
                    "rating": 0.0,
                    "reviews": 0,
                    "userId": "",
                    "userName": "",
                    "createdAt": "",
                    "nutritionInfo": {}
                }
            ]
        }
        return json.dumps(fallback)
    
    return json_text
