import os
import re
import pandas as pd
from typing import List
from collections import Counter

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH = os.path.join(BASE_DIR, "data", "dataFullLargerRegionAndCountryWithServingsBin.csv")

def load_recipes_df() -> pd.DataFrame:
    """
    CSV dosyasından tarif verilerini yükler. Dosya bulunamazsa hata fırlatır.
    """
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV not found at {CSV_PATH}")
    return pd.read_csv(CSV_PATH)

# DataFrame'i modül yüklenirken bir kere yükleyelim.
recipes_df = load_recipes_df()

def get_unique_ingredients() -> List[str]:
    """
    'BestUsdaIngredientName' sütunundan malzemeleri ayıklar.
    Noktalı virgülle ayrılan malzeme isimlerini korur.
    
    Malzemeler önce kullanım sıklığına göre (azalan) sonra da alfabetik sıraya göre sıralanır.
    """
    if "BestUsdaIngredientName" not in recipes_df.columns:
        return []
    
    # Tüm satırlardan malzeme isimlerini tek seferde elde etmek için list comprehension kullanıyoruz.
    ingredients = [
        part.strip()
        for ing_str in recipes_df["BestUsdaIngredientName"].dropna()
        for part in ing_str.split(';')
        if part.strip() and part.strip().lower() not in {"unknown", "nan"}
    ]
    
    # Malzeme kullanım frekanslarını sayıyoruz.
    counter = Counter(ingredients)
    
    # Frekansı yüksekten düşüğe, eşitlik durumunda alfabetik sıraya göre sıralıyoruz.
    return sorted(counter.keys(), key=lambda ing: (-counter[ing], ing))

def load_recipes_from_dataframe(df: pd.DataFrame) -> dict:
    """
    DataFrame'den belirli sütunları seçerek RecipeId'ye göre sözlük oluşturur.
    """
    columns_to_keep = [
        "RecipeId", "Cooking_Method", "servings_bin", "Diet_Types",
        "meal_type", "cook_time", "Healthy_Type", "CuisineRegion",
        "BestUsdaIngredientName"
    ]
    missing = set(columns_to_keep) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in CSV: {missing}")

    recipes = {}
    for _, row in df.iterrows():
        recipe_id = row["RecipeId"]
        recipe_data = {col: row[col] for col in columns_to_keep}
        recipes[recipe_id] = recipe_data
    return recipes
