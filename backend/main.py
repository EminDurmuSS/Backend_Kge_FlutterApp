from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import recommend, recipe, unique_ingredients, generate_recipe, generate_recipe_visual

app = FastAPI(
    title="Food Recommendation API",
    version="1.0",
)

# Allow CORS for testing (restrict in production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(recommend.router)
app.include_router(recipe.router)
app.include_router(unique_ingredients.router)
app.include_router(generate_recipe.router)
app.include_router(generate_recipe_visual.router)

@app.get("/")
def root():
    return {"message": "Hello! This is the KG-based Food Recommendation API with visual integration."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
