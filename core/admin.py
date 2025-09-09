from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Users, BrowsingHistory, QuizResult, RoutinePlan

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'rating', 'skin_types_list', 'get_image']
    list_filter = ['category', 'brand', 'price']
    search_fields = ['name', 'brand', 'ingredients']

    def skin_types_list(self, obj):
        return obj.skin_types
    skin_types_list.short_description = 'Skin Types'

    def get_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="50" height="50" />', obj.image_url)
        return "No Image"
    get_image.short_description = 'Image'

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'skin_type', 'device_type', 'created_at']
    list_filter = ['skin_type', 'device_type', 'created_at']
    search_fields = ['email', 'name']
    readonly_fields = ['user_id', 'created_at']

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'skin_type', 'concerns_list', 'preferences_list', 'timestamp']
    list_filter = ['skin_type', 'timestamp']
    search_fields = ['user__email']
    readonly_fields = ['quiz_id', 'timestamp']

    def concerns_list(self, obj):
        return ', '.join(obj.concerns) if obj.concerns else 'None'
    concerns_list.short_description = 'Concerns'

    def preferences_list(self, obj):
        return ', '.join(obj.preferences) if obj.preferences else 'None'
    preferences_list.short_description = 'Preferences'

@admin.register(RoutinePlan)
class RoutinePlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan_name', 'steps_count', 'created_at']
    list_filter = ['plan_name', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['routine_id', 'created_at']

    def steps_count(self, obj):
        return len(obj.steps)
    steps_count.short_description = 'Number of Steps'

@admin.register(BrowsingHistory)
class BrowsingHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'interaction_type', 'timestamp']
    list_filter = ['interaction_type', 'timestamp']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['id', 'timestamp']