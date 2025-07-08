from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
      list_display = ['title', 'category', 'level', 'price_type']
      search_fields = ['title', 'instructor']

    

    
    
