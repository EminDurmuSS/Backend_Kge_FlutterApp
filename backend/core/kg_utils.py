import re
import pickle
import numpy as np
import networkx as nx
from typing import List, Tuple, Dict, Any

UNKNOWN_PLACEHOLDER = "unknown"

def map_health_attribute(element: str) -> str:
    """
    Maps a given 'Healthy_Type' string into a normalized relation name.
    """
    e = element.lower()
    if "protein" in e:
        return "HasProteinLevel"
    elif "carb" in e:
        return "HasCarbLevel"
    elif "fat" in e and "saturated" not in e:
        return "HasFatLevel"
    elif "saturated_fat" in e:
        return "HasSaturatedFatLevel"
    elif "calorie" in e:
        return "HasCalorieLevel"
    elif "sodium" in e:
        return "HasSodiumLevel"
    elif "sugar" in e:
        return "HasSugarLevel"
    elif "fiber" in e:
        return "HasFiberLevel"
    elif "cholesterol" in e:
        return "HasCholesterolLevel"
    else:
        return "HasHealthAttribute"

def split_and_clean(value: str, delimiter: str) -> List[str]:
    """
    Splits a string by delimiter and strips whitespace, returning non-empty parts.
    """
    return [v.strip() for v in value.split(delimiter) if v.strip()]

def create_graph_and_triples(recipes: Dict[Any, Dict[str, Any]]) -> Tuple[nx.DiGraph, np.ndarray]:
    """
    Creates a directed graph and a triples array from the given recipe data dictionary.
    """
    G = nx.DiGraph()
    triples = []
    
    attribute_mappings = {
        "Cooking_Method": ("usesCookingMethod", "cooking_method"),
        "servings_bin": ("hasServingsBin", "servings_bin"),
        "cook_time": ("hasCookTime", "cook_time"),
        "CuisineRegion": ("hasCuisineRegion", "cuisine_region"),
    }
    
    list_attributes = {
        "Diet_Types": ("hasDietType", "diet_type", ","),
        "meal_type": ("isForMealType", "meal_type", ","),
    }
    
    ingredient_relation = "containsIngredient"
    ingredient_node_type = "ingredient"
    ingredient_delimiter = ";"
    
    for recipe_id, details in recipes.items():
        recipe_node = ("recipe", recipe_id)
        G.add_node(recipe_node, type="recipe", RecipeId=recipe_id)
        
        # Single-value attributes
        for col, (relation, node_type) in attribute_mappings.items():
            element = details.get(col)
            if element and element != UNKNOWN_PLACEHOLDER and str(element).strip():
                element_clean = str(element).strip()
                node_id = (node_type, element_clean)
                if not G.has_node(node_id):
                    G.add_node(node_id, type=node_type, label=element_clean)
                G.add_edge(recipe_node, node_id, relation=relation)
                triples.append((str(recipe_node), relation, str(node_id)))
        
        # Healthy_Type
        healthy = details.get("Healthy_Type")
        if healthy and healthy != UNKNOWN_PLACEHOLDER and str(healthy).strip():
            healthy_elements = split_and_clean(str(healthy), ",")
            for element in healthy_elements:
                if element:
                    relation = map_health_attribute(element)
                    node_id = ("health_attribute", element)
                    if not G.has_node(node_id):
                        G.add_node(node_id, type="health_attribute", label=element)
                    G.add_edge(recipe_node, node_id, relation=relation)
                    triples.append((str(recipe_node), relation, str(node_id)))
        
        # Multi-value attributes
        for col, (relation, node_type, delimiter) in list_attributes.items():
            value = details.get(col)
            if value and value != UNKNOWN_PLACEHOLDER and str(value).strip():
                elements = split_and_clean(str(value), delimiter)
                for element in elements:
                    if element:
                        node_id = (node_type, element)
                        if not G.has_node(node_id):
                            G.add_node(node_id, type=node_type, label=element)
                        G.add_edge(recipe_node, node_id, relation=relation)
                        triples.append((str(recipe_node), relation, str(node_id)))
        
        # Ingredients
        best_usda = details.get("BestUsdaIngredientName")
        if best_usda and best_usda != UNKNOWN_PLACEHOLDER and str(best_usda).strip():
            ingredients = split_and_clean(str(best_usda), ingredient_delimiter)
            for ingredient in ingredients:
                if ingredient:
                    node_id = ("ingredient", ingredient.lower())
                    if not G.has_node(node_id):
                        G.add_node(node_id, type=ingredient_node_type, label=ingredient)
                    G.add_edge(recipe_node, node_id, relation=ingredient_relation)
                    triples.append((str(recipe_node), ingredient_relation, str(node_id)))
                    
    triples_array = np.array(triples, dtype=str)
    return G, triples_array

def save_triples(triples_array: np.ndarray, file_path: str) -> None:
    """
    Saves the triples to a CSV file.
    """
    import pandas as pd
    df = pd.DataFrame(triples_array, columns=["Head", "Relation", "Tail"])
    df.to_csv(file_path, index=False)

def save_graph(G: nx.DiGraph, file_path: str) -> None:
    """
    Saves the graph object via pickle.
    """
    with open(file_path, "wb") as f:
        pickle.dump(G, f)
