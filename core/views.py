from django.shortcuts import render

from rest_framework.response import Response
from rest_framework import generics,status
from .models import Product, BrowsingHistory
from .serializers import ProductSerializer


class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
class LogInteraction(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        user = request.user  
        data = request.data
        product_id=data.get('product_id')
        interaction_type=data.get('interaction_type')
        if not product_id or not interaction_type:
            return Response(
                {"error": "Both 'product_id' and 'interaction_type' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        valid_interactions = [choice[0] for choice in BrowsingHistory.INTERACTION_CHOICES]
        if interaction_type not in valid_interactions:
            return Response(
                {"error": f"Invalid interaction_type. Must be one of: {valid_interactions}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        BrowsingHistory.objects.create(
            user=user,
            product=product,
            interaction_type=interaction_type,
        )
        return Response(
            {"status": "Interaction logged successfully."},
            status=status.HTTP_201_CREATED
        )

class CreateProduct(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # Check if the data is valid
        if serializer.is_valid():
            serializer.save()  # Save the new product to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)