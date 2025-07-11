from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import AdminViewCoursesAPIView

from .views import (
    RegisterView, CustomLoginView, SimplePasswordResetView,
    CourseListAPIView, CourseDetailAPIView,
    AddCourseAPIView, delete_user, # ✅ Corrected
    user_profile,
    admin_create_user, assign_course_to_user, 
    my_assigned_courses,
    AdminViewCoursesAPIView,
    ListRegisteredUsersAPIView,
    AssignedCoursesListAPIView
)

urlpatterns = [
    #  Auth Routes
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reset-password/', SimplePasswordResetView.as_view(), name='reset-password'),

    #  Course Access (shared)
    path('courses/', CourseListAPIView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailAPIView.as_view(), name='course-detail'),

    #  Logged-in User
    path('profile/', user_profile, name='user-profile'),
    path('my-courses/', my_assigned_courses, name='my-assigned-courses'),

    #  Admin-only
    path('admin/add-course/', AddCourseAPIView.as_view(), name='admin-add-course'),  # ✅ FIXED
    path('admin/create-user/', admin_create_user, name='admin-create-user'),
    path('admin/assign-course/', assign_course_to_user, name='admin-assign-course'),
    path('admin/view-courses/', AdminViewCoursesAPIView.as_view(), name='admin-view-courses'),
    path('users/', ListRegisteredUsersAPIView.as_view(), name='list-users'),
    path('admin/list-assignments/', AssignedCoursesListAPIView.as_view(), name='admin-list-assignments'),  # ✅ add this
    path('admin/delete-user/<int:user_id>/', delete_user, name='delete-user'),
    path('admin/delete-user/<int:user_id>/', delete_user, name='delete-user'),


]
