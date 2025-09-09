import pytest
from django.contrib.auth import get_user_model
from core.models import Product

@pytest.fixture
def user(db):
    User = get_user_model()
    u = User.objects.create_user(email="alice@example.com", name="Alice", password="secret123", skin_type="dry")
    return u

@pytest.fixture
def products(db):
    items = [
        dict(name="Hydrating Cleanser", brand="CeraVe", category="cleanser", ingredients="ceramide hyaluronic", price=12.5, rating=4.5, skin_types=["dry","sensitive"], image_url=""),
        dict(name="Oil Control Gel", brand="La Roche-Posay", category="moisturizer", ingredients="niacinamide zinc", price=18.0, rating=4.2, skin_types=["oily","combination"], image_url=""),
        dict(name="Soothing Serum", brand="The Ordinary", category="serum", ingredients="azelaic acid", price=10.0, rating=4.1, skin_types=["sensitive","dry"], image_url=""),
        dict(name="Daily Sunscreen SPF50", brand="Isntree", category="sunscreen", ingredients="uv filter", price=16.0, rating=4.7, skin_types=["oily","combination","dry"], image_url=""),
    ]
    created = []
    for data in items:
        p = Product.objects.create(
            name=data["name"],
            brand=data["brand"],
            category=data["category"],
            ingredients=data["ingredients"],
            price=data["price"],
            rating=data["rating"],
            skin_types=data["skin_types"],
            image_url=data["image_url"]
        )
        created.append(p)
    return created
