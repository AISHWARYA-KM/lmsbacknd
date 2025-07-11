from django.contrib import admin
from .models import Course, UserCourse, UserProfile

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'level', 'price_type', 'instructor', 'created_by']
    search_fields = ['title', 'instructor']
    list_filter = ['category', 'level', 'price_type']

@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at']
    search_fields = ['user__username', 'course__title']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user']
