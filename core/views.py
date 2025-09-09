from django.shortcuts import render
from .recommender import HybridRecommender
from rest_framework.response import Response
from rest_framework import generics,status
from .models import Product, BrowsingHistory,RoutinePlan,QuizResult,Users
from .serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .routine_builder import RoutineBuilder
from rest_framework.authtoken.models import Token
class RegisterAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            if Users.objects.filter(email=data.get('email')).exists():
                return Response({
                    "success": False,
                    "error": "User already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
                
            user = Users.objects.create(
                email=data['email'],
                name=data['name'],
                skin_type=data.get('skin_type', ''),
                concerns=data.get('concerns', []),
                preferences=data.get('preferences', []),
                device_type=data.get('device_type', '')
            )
            user.set_password(data['password'])
            user.save()
            
            return Response({
                "success": True,
                "message": "User created successfully",
                "user": {
                    "user_id": user.user_id,
                    "email": user.email,
                    "name": user.name,
                    "skin_type": user.skin_type
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Registration failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return Response({
                    "success": False,
                    "error": "Email and password are required"
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = Users.objects.get(email=email)
            except Users.DoesNotExist:
                return Response({
                    "success": False,
                    "error": "Invalid credentials"
                }, status=status.HTTP_401_UNAUTHORIZED)

            if not user.check_password(password):
                return Response({
                    "success": False,
                    "error": "Invalid credentials"
                }, status=status.HTTP_401_UNAUTHORIZED)
                
            token, created =Token.objects.get_or_create(user=user)
            return Response({
                "success": True,
                "message": "Login successful",
                "token": token.key,
                "user": {
                    "user_id": user.user_id,
                    "email": user.email,
                    "name": user.name,
                    "skin_type": user.skin_type
                }
            })
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Login failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
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
            product = Product.objects.get(product_id=product_id)
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
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class RecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated]  
    def get(self, request):
        try:
            user = request.user
            limit = self.get_limit_param(request)
            context = self.get_context_params(request)
            recommender = HybridRecommender()
            recommended_products = recommender.get_recommendations(
                user=user,
                num_recommendations=limit,
                context=context)
            response_data = self.build_response(recommender, recommended_products, user, context)
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return self.handle_error(e)

    def get_limit_param(self, request):
        try:
            limit = int(request.GET.get('limit', 10))
            return max(1, min(limit, 50)) 
        except ValueError:
            return 10

    def get_context_params(self, request):
        return {
            'season': request.GET.get('season', '').lower(),
            'device': request.GET.get('device', '').lower()}

    def build_response(self, recommender, products, user, context):
        serializer = ProductSerializer(products, many=True)
        recommendations = []
        for product in products:
            reason = recommender.get_recommendation_reason(product, user, context)
            product_data = serializer.data[products.index(product)]
            recommendations.append({
                **product_data,
                "reason": reason,})
        return {
            "count": len(recommendations),
            "context": context,
            "recommendations": recommendations}

    def handle_error(self, error):
        error_message = f"Failed to generate recommendations: {str(error)}"
        return Response(
            {
                "error": "Recommendation service unavailable",
                "details": error_message
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RoutineBuilderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            builder = RoutineBuilder()
            routines = builder.generate_routines(user, request.data.get('quiz_data'))
            return Response({
                "success": True,
                "message": "Routines generated successfully",
                "data": routines
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to generate routines: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            user = request.user
            routines = RoutinePlan.objects.filter(user=user).order_by('-created_at')
            
            routines_data = []
            for routine in routines:
                routines_data.append({
                    'routine_id': routine.routine_id,
                    'plan_name': routine.plan_name,
                    'steps': routine.steps,
                    'created_at': routine.created_at,
                    'user_email': routine.user.email
                })
            return Response({
                "success": True,
                "count": len(routines_data),
                "routines": routines_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to fetch routines: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoutineDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, routine_id):
        try:
            routine = RoutinePlan.objects.get(routine_id=routine_id, user=request.user)
            return Response({
                "success": True,
                "routine": {
                    'routine_id': routine.routine_id,
                    'plan_name': routine.plan_name,
                    'steps': routine.steps,
                    'created_at': routine.created_at
                }
            })
            
        except RoutinePlan.DoesNotExist:
            return Response({
                "success": False,
                "error": "Routine not found"
            }, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, routine_id):
        try:
            routine = RoutinePlan.objects.get(routine_id=routine_id, user=request.user)
            routine.delete()
            
            return Response({
                "success": True,
                "message": "Routine deleted successfully"
            })
            
        except RoutinePlan.DoesNotExist:
            return Response({
                "success": False,
                "error": "Routine not found"
            }, status=status.HTTP_404_NOT_FOUND)
            


class QuizAPIView(APIView):
    permission_classes = [IsAuthenticated]
    QUIZ_QUESTIONS = [
        {
            'question_id': 1,
            'question_text': "What is your skin type?",
            'question_type': "single",
            'options': [
                {'value': 'oily', 'text': 'Oily', 'related_field': 'skin_type'},
                {'value': 'dry', 'text': 'Dry', 'related_field': 'skin_type'},
                {'value': 'combination', 'text': 'Combination', 'related_field': 'skin_type'},
                {'value': 'sensitive', 'text': 'Sensitive', 'related_field': 'skin_type'},
                {'value': 'normal', 'text': 'Normal', 'related_field': 'skin_type'},
            ]
        },
        {
            'question_id': 2,
            'question_text': "What are your main skin concerns? (Select all that apply)",
            'question_type': "multiple",
            'options': [
                {'value': 'acne', 'text': 'Acne', 'related_field': 'concerns'},
                {'value': 'aging', 'text': 'Aging', 'related_field': 'concerns'},
                {'value': 'redness', 'text': 'Redness', 'related_field': 'concerns'},
                {'value': 'dark_spots', 'text': 'Dark Spots', 'related_field': 'concerns'},
                {'value': 'dullness', 'text': 'Dullness', 'related_field': 'concerns'},
                {'value': 'dryness', 'text': 'Dryness', 'related_field': 'concerns'},
                {'value': 'oiliness', 'text': 'Excess Oil', 'related_field': 'concerns'},
            ]
        },
        {
            'question_id': 3,
            'question_text': "Do you have any product preferences?",
            'question_type': "multiple",
            'options': [
                {'value': 'vegan', 'text': 'Vegan', 'related_field': 'preferences'},
                {'value': 'cruelty_free', 'text': 'Cruelty-Free', 'related_field': 'preferences'},
                {'value': 'fragrance_free', 'text': 'Fragrance-Free', 'related_field': 'preferences'},
                {'value': 'organic', 'text': 'Organic', 'related_field': 'preferences'},
                {'value': 'hypoallergenic', 'text': 'Hypoallergenic', 'related_field': 'preferences'},
            ]
        },
        {
            'question_id': 4,
            'question_text': "What is your budget range?",
            'question_type': "single",
            'options': [
                {'value': 'low', 'text': 'Under $50', 'related_field': 'budget_range'},
                {'value': 'medium', 'text': '$50 - $100', 'related_field': 'budget_range'},
                {'value': 'high', 'text': 'Over $100', 'related_field': 'budget_range'},
            ]
        }
    ]

    def get(self, request):
        try:
            return Response({
                "success": True,
                "questions": self.QUIZ_QUESTIONS,
                "total_questions": len(self.QUIZ_QUESTIONS)
            })
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to fetch questions: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self, request):
        try:
            user = request.user
            answers = request.data.get('answers', {})
            
            if not answers:
                return Response({
                    "success": False,
                    "error": "No answers provided"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            skin_type = answers.get('skin_type', '')
            concerns = answers.get('concerns', [])
            preferences = answers.get('preferences', [])
            budget_range = answers.get('budget_range', '')
            
            if not skin_type:
                return Response({
                    "success": False,
                    "error": "Skin type is required"
                }, status=status.HTTP_400_BAD_REQUEST)
                
            quiz_result = QuizResult.objects.create(
                user=user,
                skin_type=skin_type,
                concerns=concerns,
                preferences=preferences,
                budget_range=budget_range
            )
            
            self.update_user_profile(user, {
                'skin_type': skin_type,
                'concerns': concerns,
                'preferences': preferences
            })
            
            return Response({
                "success": True,
                "message": "Quiz submitted successfully",
                "quiz_id": quiz_result.quiz_id,
                "results": {
                    "skin_type": quiz_result.skin_type,
                    "concerns": quiz_result.concerns,
                    "preferences": quiz_result.preferences,
                    "budget_range": quiz_result.budget_range
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to process quiz: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_user_profile(self, user, quiz_data):
        user.skin_type = quiz_data['skin_type']
        user.concerns = quiz_data['concerns']
        user.preferences = quiz_data['preferences']
        user.save()
        

class QuizResultAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user = request.user
            quiz_results = QuizResult.objects.filter(user=user).order_by('-timestamp')
            
            results_data = []
            for result in quiz_results:
                results_data.append({
                    'quiz_id': result.quiz_id,
                    'skin_type': result.skin_type,
                    'concerns': result.concerns,
                    'preferences': result.preferences,
                    'budget_range': result.budget_range,
                    'timestamp': result.timestamp
                })
            
            return Response({
                "success": True,
                "count": len(results_data),
                "results": results_data
            })
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to fetch quiz results: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_single(self, request, quiz_id):
        try:
            quiz_result = QuizResult.objects.get(quiz_id=quiz_id, user=request.user)
            
            return Response({
                "success": True,
                "result": {
                    'quiz_id': quiz_result.quiz_id,
                    'skin_type': quiz_result.skin_type,
                    'concerns': quiz_result.concerns,
                    'preferences': quiz_result.preferences,
                    'budget_range': quiz_result.budget_range,
                    'timestamp': quiz_result.timestamp
                }
            })
            
        except QuizResult.DoesNotExist:
            return Response({
                "success": False,
                "error": "Quiz result not found"
            }, status=status.HTTP_404_NOT_FOUND)

