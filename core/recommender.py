from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Count, Q
from .models import Product, BrowsingHistory, UserProfile, QuizResult
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import numpy as np

class HybridRecommender:
    def __init__(self):
        self.vectorizer = CountVectorizer()
        self.content_weight = 0.5
        self.collab_weight = 0.3
        self.context_weight = 0.2
        
    def get_recommendations(self, user, num_recommendations=10, context=None):
        all_products = list(Product.objects.all())

        if not all_products:
            return []
        
        content_scores = self.content_based_scores(user, all_products)
        collab_scores = self.collaborative_scores(user, all_products)
        context_scores = self.contextual_scores(all_products, context)
        
        
        final_scores = (
            self.content_weight * content_scores +
            self.collab_weight * collab_scores +
            self.context_weight * context_scores
        )
        
        top_indices = np.argsort(final_scores)[::-1][:num_recommendations]
        recommended_products = [all_products[i] for i in top_indices]
        
        return recommended_products
        
    def content_based_scores(self, user, all_products):
        try:
            features = []
            for product in all_products:
                feature_text=f"{product.category} {product.skin_types} "
                feature_text += f"{product.concerns_targeted} {product.ingredients}"
                features.append(feature_text)
                
            feature_matrix = self.vectorizer.fit_transform(features)
            user_profile = self.create_user_profile(user, feature_matrix, all_products)
            
            if user_profile is not None:
                similarity_scores = cosine_similarity(user_profile, feature_matrix)
                return similarity_scores.flatten()
            return self.content_from_quiz_profile(user, all_products, feature_matrix)
        
        except Exception as e:
            print(f"Content-based error: {e}")
            return np.zeros(len(all_products))
    def create_user_profile(self, user, feature_matrix, all_products):
        user_view_history = BrowsingHistory.objects.filter(
            user=user, 
            interaction_type='view'
        )[:10]
        
        if not user_view_history.exists():
            return None
        
        product_indices = []
        for history in user_view_history:
            try:
                index = all_products.index(history.product)
                product_indices.append(index)
            except ValueError:
                continue
        
        if not product_indices:
            return None
    
        user_vectors = feature_matrix[product_indices]
        return user_vectors.mean(axis=0)
    
    def content_from_quiz_profile(self, user, all_products, feature_matrix):
        try:
            quiz_result = QuizResult.objects.filter(user=user).latest('timestamp')            
            quiz_profile = f"{quiz_result.skin_type} {quiz_result.concerns} {quiz_result.preferences}"
            quiz_profile_vector = self.vectorizer.transform([quiz_profile])
            similarity_scores = cosine_similarity(quiz_profile_vector, feature_matrix)
            return similarity_scores.flatten()
            
        except QuizResult.DoesNotExist:
            return np.zeros(len(all_products))
        
    def collaborative_scores(self, user, all_products):
        try:
            similar_users=self.find_similar_users(user)
            if not similar_users:
                return np.zeros(len(all_products))
            scores=np.zeros(len(all_products))
            for product in all_products:
                product_index=all_products.index(product)
                view_count=BrowsingHistory.objects.filter(Q(user__in=similar_users)&Q(product=product)&Q(interaction_type='view')).count()
                scores[product_index]=view_count
            return scores
        except Exception as e:
            print(f"Collaborative error: {e}")
            return np.zeros(len(all_products))
    def find_similar_users(self, user, max_users=5):
        user_viewed_products = set(BrowsingHistory.objects.filter(
            user=user, 
            interaction_type='view'
        ).values_list('product_id', flat=True))
        
        if not user_viewed_products:
            return []
        
        similar_users = []
        for other_user in User.objects.exclude(id=user.id):
            other_viewed = set(BrowsingHistory.objects.filter(
                user=other_user,
                interaction_type='view'
            ).values_list('product_id', flat=True))
            
            intersection = len(user_viewed_products.intersection(other_viewed))
            union = len(user_viewed_products.union(other_viewed))
            
            if union > 0:
                similarity = intersection / union
                if similarity > 0.2: 
                    similar_users.append((other_user, similarity))
        
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return [user[0] for user, similarity in similar_users[:max_users]]
    def contextual_scores(self, all_products, context):
    
        scores = np.ones(len(all_products))       
        if not context:
            return scores  
        try:
            
            if context.get('season'):
                season = context['season'].lower()
                for i, product in enumerate(all_products):
                    if self.is_seasonal_product(product, season):
                        scores[i] *= 1.5 
            

            if context.get('device'):
                device = context['device'].lower()
                for i, product in enumerate(all_products):
                    if device == 'mobile' and product.category in ['cleanser', 'moisturizer', 'sunscreen']:
                        scores[i] *= 1.3  
                        
        except Exception as e:
            print(f"Contextual error: {e}")
        
        return scores
    def is_seasonal_product(self, product, season):
        
        seasonal_keywords = {
            'summer': ['sunscreen', 'spf', 'lightweight', 'gel', 'oil-free'],
            'winter': ['hydrating', 'cream', 'rich', 'moisturizing', 'balm'],
            'spring': ['lightweight', 'refreshing', 'toner', 'serum'],
            'fall': ['repair', 'serum', 'moisturizer', 'treatment']
        }
        
        product_text = f"{product.name} {product.category} {product.ingredients}".lower()
        
        if season in seasonal_keywords:
            return any(keyword in product_text for keyword in seasonal_keywords[season])
        
        return False