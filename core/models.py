from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class Users(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    skin_type = models.CharField(
        max_length=50,
        choices=[
            ('oily', 'Oily'),
            ('dry', 'Dry'),
            ('sensitive', 'Sensitive'),
            ('combination', 'Combination'),
        ],
        blank=True,
        null=True
    )
    concerns = models.JSONField(default=list) 
    preferences = models.JSONField(default=list)
    device_type = models.CharField(max_length=50,        
        choices=[
            ('mobile', 'Mobile'),
            ('desktop', 'Desktop'),
        ], blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False)  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=[
            ('cleanser', 'Cleanser'),
            ('serum', 'Serum'),
            ('moisturizer', 'Moisturizer'),
            ('toner', 'Toner'),
            ('sunscreen', 'Sunscreen'),
        ]
    )
    skin_types = models.JSONField(default=list)
    concerns_targeted = models.JSONField(default=list)
    ingredients = models.JSONField(default=list)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0.0)
    image_url = models.URLField(blank=True, null=True)
    tags = models.JSONField(default=list)

    def __str__(self):
        return f"{self.brand} {self.name}"


class BrowsingHistory(models.Model):
    INTERACTION_CHOICES=[
            ('view', 'View'),
            ('like', 'Like'),
            ('wishlist', 'Wishlist'),
            ('cart', 'Cart'),
        ]
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='browsing_history')
    timestamp = models.DateTimeField(auto_now_add=True)
    interaction_type = models.CharField(
        max_length=50,
        choices=INTERACTION_CHOICES,
    )

    def __str__(self):
        return f"{self.user.email} - {self.product.name} - {self.interaction_type}"


class QuizResult(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE,related_name='quiz_results')
    skin_type = models.CharField(
        max_length=50,
        choices=[
            ('oily', 'Oily'),
            ('dry', 'Dry'),
            ('sensitive', 'Sensitive'),
            ('combination', 'Combination'),
        ]
    )
    concerns = models.JSONField(default=list) 
    preferences = models.JSONField(default=list) 
    budget_range = models.CharField(max_length=50, blank=True, null=True) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz {self.quiz_id} for {self.user.email}"


class RoutinePlan(models.Model):
    routine_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE,related_name='routine_plans')
    plan_name = models.CharField(max_length=50,choices=[
        ('full', 'Full Plan'),
        ('hydration', 'Hydration Plan'),
        ('minimalist', 'Minimalist Plan'),
    ]) 
    steps = models.JSONField(default=list)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plan_name} for {self.user.email}"


class ContextualData(models.Model):
    context_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='contextual_data')
    device_type = models.CharField(
        max_length=50,
        choices=[
            ('mobile', 'Mobile'),
            ('desktop', 'Desktop'),
        ],
        blank=True,
        null=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    season = models.CharField(
        max_length=50,
        choices=[
            ('winter', 'Winter'),
            ('spring', 'Spring'),
            ('summer', 'Summer'),
            ('autumn', 'Autumn'),
        ],
        blank=True,
        null=True
    )  
    
    def __str__(self):
        return f"Context for {self.user.email} at {self.timestamp}"