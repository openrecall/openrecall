import pytest
import numpy as np
from openrecall.nlp import cosine_similarity


def test_cosine_similarity_identical_vectors():
    a = np.array([1, 0, 0])
    b = np.array([1, 0, 0])
    assert cosine_similarity(a, b) == 1.0


def test_cosine_similarity_orthogonal_vectors():
    a = np.array([1, 0, 0])
    b = np.array([0, 1, 0])
    assert cosine_similarity(a, b) == 0.0


def test_cosine_similarity_opposite_vectors():
    a = np.array([1, 0, 0])
    b = np.array([-1, 0, 0])
    assert cosine_similarity(a, b) == -1.0


def test_cosine_similarity_non_unit_vectors():
    a = np.array([3, 0, 0])
    b = np.array([1, 0, 0])
    assert cosine_similarity(a, b) == 1.0


def test_cosine_similarity_arbitrary_vectors():
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    expected_similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    assert cosine_similarity(a, b) == pytest.approx(expected_similarity)


def test_cosine_similarity_zero_vector():
    a = np.array([0, 0, 0])
    b = np.array([1, 0, 0])
    result = cosine_similarity(a, b)
    assert np.isnan(
        result
    ), "Expected result to be NaN when one of the vectors is a zero vector"
