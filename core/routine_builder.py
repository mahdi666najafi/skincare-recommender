from .models import Product, QuizResult, RoutinePlan, Users
from .recommender import HybridRecommender
from django.utils import timezone

class RoutineBuilder:
    ROUTINE_STEPS = {
        'full': ['cleanser', 'toner', 'serum', 'moisturizer', 'sunscreen'],
        'hydration': ['cleanser', 'serum', 'moisturizer'],
        'minimalist': ['cleanser', 'moisturizer', 'sunscreen']
    }
    
    STEP_INSTRUCTIONS = {
        'cleanser': "Apply to damp skin, massage gently for 60 seconds, and rinse thoroughly with lukewarm water.",
        'toner': "Apply with a cotton pad or clean hands, gently sweep across face and neck.",
        'serum': "Apply 2-3 drops to face and neck, gently pat until fully absorbed.",
        'moisturizer': "Take a dime-sized amount, warm between palms and press into skin.",
        'sunscreen': "Apply generously as the final step, reapply every 2 hours when outdoors."
    }

    def __init__(self):
        self.recommender = HybridRecommender()

    def generate_routines(self, user, quiz_data=None):
        if not quiz_data:
            quiz_data = self.get_quiz_data(user)
        
        routines = {}
        
        for plan_type in ['full', 'hydration', 'minimalist']:
            routine_data = self.generate_single_routine(user, plan_type, quiz_data)
            routine_plan = self.save_routine_plan(user, plan_type, routine_data['steps'])
            routines[plan_type] = {
                **routine_data,
                'routine_id': routine_plan.routine_id
            }
        
        return routines

    def generate_single_routine(self, user, plan_type, quiz_data):
        steps = self.ROUTINE_STEPS[plan_type]
        routine_steps = []
        
        for step in steps:
            product = self.get_product_for_step(user, step, quiz_data)
            if product:
                routine_steps.append({
                    'step': step,
                    'step_name': self.get_step_display_name(step),
                    'product_id': str(product.product_id),
                    'product_name': product.name,
                    'product_brand': product.brand,
                    'product_price': str(product.price),
                    'product_image': product.image_url,
                    'instructions': self.STEP_INSTRUCTIONS[step],
                    'category': product.category
                })
        
        return {
            'plan_name': plan_type,
            'plan_display_name': self.get_plan_display_name(plan_type),
            'steps': routine_steps,
            'total_steps': len(routine_steps),
            'estimated_time': f"{len(routine_steps) * 2}-{len(routine_steps) * 3} minutes",
            'generated_at': timezone.now().isoformat()
        }

    def get_product_for_step(self, user, step, quiz_data):
        available_products = Product.objects.filter(category=step)
        
        if not available_products:
            return None
        filtered_products = self.filter_by_quiz_preferences(available_products, quiz_data)
        
        if filtered_products:
            recommended = self.recommender.get_recommendations(
                user=user,
                num_recommendations=min(5, len(filtered_products)),
                context={'season': 'general'}
            )
            for product in recommended:
                if product in filtered_products:
                    return product
            
            return filtered_products[0]
        
        return available_products.order_by('?').first()  

    def filter_by_quiz_preferences(self, products, quiz_data):
        filtered_products = []
        
        for product in products:
            skin_match = (
                not quiz_data.get('skin_type') or 
                quiz_data['skin_type'] in product.skin_types
            )
            
            concerns_match = True
            if quiz_data.get('concerns') and product.concerns_targeted:
                product_concerns = [c.strip() for c in product.concerns_targeted]
                user_concerns = [c.strip() for c in quiz_data['concerns']]
                concerns_match = any(concern in product_concerns for concern in user_concerns)
            
            if skin_match and concerns_match:
                filtered_products.append(product)
        
        return filtered_products

    def get_quiz_data(self, user):
        try:
            quiz = QuizResult.objects.filter(user=user).latest('timestamp')
            return {
                'skin_type': quiz.skin_type,
                'concerns': quiz.concerns if quiz.concerns else [],
                'preferences': quiz.preferences if quiz.preferences else []
            }
        except QuizResult.DoesNotExist:
            return {
                'skin_type': None,
                'concerns': [],
                'preferences': []
            }

    def save_routine_plan(self, user, plan_type, steps):
        return RoutinePlan.objects.create(
            user=user,
            plan_name=plan_type,
            steps=steps
        )

    def get_step_display_name(self, step):
        names = {
            'cleanser': 'Cleanser',
            'toner': 'Toner',
            'serum': 'Treatment Serum',
            'moisturizer': 'Moisturizer',
            'sunscreen': 'Sunscreen'
        }
        return names.get(step, step.title())

    def get_plan_display_name(self, plan_type):
        names = {
            'full': 'Complete Care Routine',
            'hydration': 'Hydration Boost Routine',
            'minimalist': 'Essential Minimal Routine'
        }
        return names.get(plan_type, plan_type.title())

    def get_user_routines(self, user):
        return RoutinePlan.objects.filter(user=user).order_by('-created_at')