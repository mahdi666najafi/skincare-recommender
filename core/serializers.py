from rest_framework import serializers
from .models import Product,Users

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['user_id', 'email', 'name', 'skin_type', 'concerns', 'preferences', 'device_type']