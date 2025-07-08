from django.urls import path
from .views import RegisterView, SimplePasswordResetView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CourseListAPIView, CourseDetailAPIView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("reset-password/", SimplePasswordResetView.as_view(), name='reset-password'),
    path('api/courses/', CourseListAPIView.as_view(), name='course-list'),
    path('api/courses/<int:pk>/', CourseDetailAPIView.as_view()),
]
