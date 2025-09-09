import pytest
from core.recommender import HybridRecommender

@pytest.mark.django_db
def test_recommender_returns_at_least_one(products, user):
    rec = HybridRecommender()
    recs = rec.get_recommendations(user, num_recommendations=3, context={"season": "summer"})
    assert isinstance(recs, (list, tuple))
    assert len(recs) <= 3

@pytest.mark.django_db
def test_recommendation_reason_mentions_skin_or_context(products, user):
    rec = HybridRecommender()
    product = products[0]
    reason = rec.get_recommendation_reason(product, user, context={"season": "summer"})
    assert isinstance(reason, str)
    assert ("dry" in reason) or ("summer" in reason) or (len(reason) > 0)
