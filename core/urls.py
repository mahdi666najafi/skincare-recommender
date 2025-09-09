from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('auth/register/', views.RegisterAPIView.as_view(), name='register'),
    path('auth/login/', views.LoginAPIView.as_view(), name='login'),
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('interaction-log/', views.LogInteraction.as_view(), name='log-interaction'),
    path('create-product/', views.CreateProduct.as_view(), name='create-product'),
    path('recommendations/', views.RecommendationAPIView.as_view(), name='get-recommendations'),
    path('routines/generate/', views.RoutineBuilderAPIView.as_view(), name='generate-routines'),
    path('routines/', views.RoutineBuilderAPIView.as_view(), name='get-routines'),
    path('routines/<int:routine_id>/', views.RoutineDetailAPIView.as_view(), name='routine-detail'),    
    path('quiz/questions/', views.QuizAPIView.as_view(), name='quiz-questions'),
    path('quiz/submit/', views.QuizAPIView.as_view(), name='quiz-submit'),
    path('quiz/results/', views.QuizResultAPIView.as_view(), name='quiz-results'),
    path('quiz/results/<int:quiz_id>/', views.QuizResultAPIView.as_view(), name='quiz-result-detail'),
]