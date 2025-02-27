# recommender.py

from typing import List, Dict, Any, Tuple
from pykeen.predict import predict_target
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from core.model import model, triples_factory
from core.data_loading import recipes_df
from core.kg_utils import map_health_attribute

DEBUG = True
def map_user_input_to_criteria(
    cooking_method: str,
    servings_bin: str,   # still received for prompt purposes
    diet_types: List[str],
    meal_type: List[str],
    cook_time: str,      # still received for prompt purposes
    health_types: List[str],
    cuisine_region: str,
    ingredients: List[str],
) -> List[Tuple[str, str]]:
    """
    Maps user input to criteria tuples for the KG lookup.
    Note: 'servings_bin' and 'cook_time' are deliberately excluded
    from the KG matching because they are not available in the knowledge graph.
    They will, however, be included in the LLM prompt.
    """
    criteria = []

    # Map diet types (e.g., "Standard" => "diet_type_Standard")
    for dt in diet_types:
        dt_clean = dt.strip()
        tail = f"diet_type_{dt_clean}"
        criteria.append((tail, "hasDietType"))

    # Map meal types (e.g., "dinner" => "meal_type_dinner")
    for mt in meal_type:
        mt_clean = mt.strip()
        tail = f"meal_type_{mt_clean}"
        criteria.append((tail, "isForMealType"))

    # Map health types (e.g., "High Calorie" => "health_attribute_High Calorie")
    for ht in health_types:
        ht_clean = ht.strip()
        relation = map_health_attribute(ht_clean)
        tail = f"health_attribute_{ht_clean}"
        criteria.append((tail, relation))

    # Map cuisine region (e.g., "Southeast Asia" => "cuisine_region_Southeast Asia")
    if cuisine_region:
        cr = cuisine_region.strip()
        tail = f"cuisine_region_{cr}"
        criteria.append((tail, "hasCuisineRegion"))

    # Map ingredients (e.g., "Tomato" => "ingredient_Tomato")
    for ing in ingredients:
        ing_clean = ing.strip()
        tail = f"ingredient_{ing_clean}"
        criteria.append((tail, "containsIngredient"))

    return criteria




def _normalize_scores(df: pd.DataFrame) -> pd.DataFrame:
    if DEBUG:
        print(f"[DEBUG] Normalizing scores for dataframe with shape: {df.shape}")

    if df.empty:
        df["normalized_score"] = 0.0
        if DEBUG:
            print("[DEBUG] DataFrame is empty. Set normalized_score to 0.0")
        return df

    scaler = MinMaxScaler()
    df["normalized_score"] = scaler.fit_transform(df[["score"]])
    return df

def get_matching_recipes(
    criteria: List[Tuple[str, str]],
    top_k: int,
    flexible: bool = False
) -> List[str]:
    if DEBUG:
        print(f"[DEBUG] Getting matching recipes for criteria: {criteria} with top_k: {top_k} and flexible: {flexible}")
    if not criteria:
        return []

    all_preds = []
    for tail, relation in criteria:
        if DEBUG:
            print(f"[DEBUG] Predicting for tail: {tail}, relation: {relation}")
        preds = predict_target(
            model=model,
            relation=relation,
            tail=tail,
            triples_factory=triples_factory
        ).df
        preds = _normalize_scores(preds)
        preds["weighted_score"] = preds["normalized_score"]  # no weighting
        preds = preds[["head_label", "weighted_score"]]
        all_preds.append(preds)

    # Merge results
    merged = all_preds[0]
    for other in all_preds[1:]:
        how_type = "outer" if flexible else "inner"
        merged = merged.merge(other, on="head_label", how=how_type, suffixes=("", "_y"))
        merged["weighted_score"] = merged["weighted_score"].fillna(0) + merged["weighted_score_y"].fillna(0)
        merged.drop(columns=["weighted_score_y"], inplace=True)

    # Filter to recipe_***
    merged = merged[merged["head_label"].str.startswith("recipe_")]
    merged.sort_values(by="weighted_score", ascending=False, inplace=True)
    merged = merged.head(top_k)

    # Convert "recipe_123" -> "123"
    def parse_recipe_id(node_str: str) -> str:
        return node_str.split("recipe_", 1)[1]

    ids = merged["head_label"].apply(parse_recipe_id).to_list()
    if DEBUG:
        print(f"[DEBUG] Final top {top_k} recipe IDs: {ids}")
    return ids

def fetch_recipe_info(recipe_id: str) -> Dict[str, Any]:
    try:
        rid_int = int(recipe_id)
    except ValueError:
        return None

    row = recipes_df[recipes_df["RecipeId"] == rid_int]
    if row.empty:
        return None
    return row.iloc[0].to_dict()
