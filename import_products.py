
import json
import os
import django
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_DOWN
from core.models import Product 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skincare.settings')
django.setup()

def import_products():
    with open('sample_products.json', 'r', encoding='utf-8') as file:
        products = json.load(file)
    
    for product_data in products:
        try:
            price = Decimal(str(product_data['price'])).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            product = Product(
                name=product_data['name'],
                brand=product_data['brand'],
                category=product_data['category'],
                skin_types=product_data['skin_types'],
                concerns_targeted=product_data['concerns_targeted'],
                ingredients=product_data['ingredients'],
                price=price,
                rating=product_data['rating'],
                image_url=product_data['image_url'],
                tags=product_data['tags']
            )
            product.full_clean()
            product.save()
            print(f"Imported: {product}")
        except ValidationError as e:
            print(f"Error importing {product_data['name']}: {e}")
        except Exception as e:
            print(f"Unexpected error for {product_data['name']}: {e}")

if __name__ == '__main__':
    import_products()
