import pytest
from django.contrib.auth import get_user_model
from core.models import Users, Product, BrowsingHistory, QuizResult, RoutinePlan

@pytest.mark.django_db
def test_user_manager_creates_user_with_hashed_password():
    User = get_user_model()
    u = User.objects.create_user(email="bob@example.com", name="Bob", password="p@ssw0rd", skin_type="oily")
    assert u.email == "bob@example.com"
    assert u.password != "p@ssw0rd"
    assert u.check_password("p@ssw0rd")

@pytest.mark.django_db
def test_user_manager_creates_superuser_flags():
    User = get_user_model()
    su = User.objects.create_superuser(email="admin@example.com", name="Admin", password="admin123")
    assert su.is_staff is True
    assert su.is_superuser is True

@pytest.mark.django_db
def test_product_str_and_fields():
    p = Product.objects.create(
        name="Hydrating Cleanser",
        brand="CeraVe",
        category="cleanser",
        ingredients="ceramide hyaluronic",
        price=12.5,
        rating=4.5,
        skin_types=["dry","sensitive"],
        image_url="https://example.com/img.png"
    )
    assert "Hydrating" in str(p)
    assert isinstance(p.skin_types, list)

@pytest.mark.django_db
def test_browsing_history_creation(user, products):
    entry = BrowsingHistory.objects.create(user=user, product=products[0], interaction_type="view")
    assert entry.user == user
    assert entry.product == products[0]
    assert entry.timestamp is not None

@pytest.mark.django_db
def test_quiz_result_and_routine_plan(user):
    qr = QuizResult.objects.create(
        user=user,
        skin_type="combination",
        concerns=["acne", "redness"],
        preferences=["niacinamide"]
    )
    assert isinstance(qr.concerns, list)
    assert "acne" in qr.concerns

    plan = RoutinePlan.objects.create(
        user=user,
        plan_name="Simple AM",
        steps=[{"step": 1, "type": "cleanser"}, {"step": 2, "type": "sunscreen"}]
    )
    assert len(plan.steps) == 2
    assert plan.plan_name == "Simple AM"
