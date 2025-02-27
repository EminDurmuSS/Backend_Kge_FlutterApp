import os
import ast
import torch
import pandas as pd
import numpy as np
from pykeen.models import Model
from pykeen.triples import TriplesFactory
from typing import Any

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CORE_DIR, ".."))
MODEL_PATH = os.path.join(BASE_DIR, "embedding", "trained_model.pkl")
TRIPLES_PATH = os.path.join(BASE_DIR, "data", "triples_new_without_ct_ss.csv")

def tuple_to_canonical(s: str) -> str:
    """
    Convert a string representation of a tuple (e.g., "('recipe', 123)")
    into a canonical form "recipe_123".
    """
    try:
        t = ast.literal_eval(s)
        return f"{t[0]}_{t[1]}"
    except Exception as e:
        print(f"Error converting tuple: {str(e)} => {s}")
        return s

def load_kge_model() -> Any:
    """
    Loads the pre-trained PyKEEN model from disk.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    return torch.load(MODEL_PATH, map_location=torch.device("cpu"), weights_only=False)

def get_triples_factory() -> TriplesFactory:
    """
    Loads the triple data from CSV and returns a TriplesFactory for the KGE model.
    """
    df = pd.read_csv(TRIPLES_PATH)
    triples = []
    for h, r, t in df[["Head", "Relation", "Tail"]].values:
        ch = tuple_to_canonical(h)
        cr = r.strip()
        ct = tuple_to_canonical(t)
        triples.append((ch, cr, ct))
    return TriplesFactory.from_labeled_triples(
        triples=np.array(triples, dtype=str),
        create_inverse_triples=False
    )

# Load the model and triples factory once at import
model = load_kge_model().eval()
triples_factory = get_triples_factory()
