import numpy as np
import os
import os.path
from sentence_transformers import SentenceTransformer
from openrecall.config import model_cache_path

def get_model(model_name):
    cache_path = os.path.join(model_cache_path, model_name)
    if os.path.isdir(cache_path):
        return SentenceTransformer(cache_path)
    else:
        model = SentenceTransformer(model_name)
        model.save(cache_path)
        return model


def get_embedding(text):
    model = get_model("all-MiniLM-L6-v2")
    sentences = text.split("\n")
    sentence_embeddings = model.encode(sentences)
    mean = np.mean(sentence_embeddings, axis=0)
    mean = mean.astype(np.float64)
    return mean


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
