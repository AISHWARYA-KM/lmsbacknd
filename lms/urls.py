from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    # Auth
    RegisterView, CustomLoginView, SimplePasswordResetView,

    # User
    user_profile, my_assigned_courses, ListRegisteredUsersAPIView, delete_user,

    # Course
    CourseListAPIView, CourseDetailAPIView, AddCourseAPIView, AdminViewCoursesAPIView,
    assign_course_to_user, AssignedCoursesListAPIView,
     org_view_courses,OrganizationAddCourseView,OrganizationProfileView,

    # Batch
    CreateBatchView, list_batches_for_org,
    AddUserToBatchView, assign_course_to_batch,
    ListBatchCoursesView, view_users_in_batch,
    remove_course_by_name, remove_user_from_batch,

    # User Creation
    admin_create_user, admin_or_org_create_user, create_organization_user,
    non_admin_users, list_batches_with_users,list_batches_with_courses,
    

    # Organization
    org_view_courses,list_all_batch_courses,
)

urlpatterns = [
    # 🔐 Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reset-password/', SimplePasswordResetView.as_view(), name='reset-password'),


    # 👤 User Profile
    path('profile/', user_profile, name='user-profile'),
    path('my-courses/', my_assigned_courses, name='my-assigned-courses'),

    # 📚 Shared Courses
    path('courses/', CourseListAPIView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailAPIView.as_view(), name='course-detail'),

    # 🛠 Admin Panel
    path('admin/create-user/', admin_create_user, name='admin-create-user'),
    path('admin/create-organization/', create_organization_user, name='admin-create-organization'),
    path('admin/add-course/', AddCourseAPIView.as_view(), name='admin-add-course'),
    path('admin/assign-course/', assign_course_to_user, name='admin-assign-course'),
    path('admin/view-courses/', AdminViewCoursesAPIView.as_view(), name='admin-view-courses'),
    path('admin/list-assignments/', AssignedCoursesListAPIView.as_view(), name='admin-list-assignments'),
    path('admin/delete-user/<int:user_id>/', delete_user, name='delete-user'),

    # 📋 User Lists
    path('users/', ListRegisteredUsersAPIView.as_view(), name='list-users'),
    path('users/non-admin/', non_admin_users,name='non-admin-users'),

    # 🏢 Organization Routes
    path('org/create-user/', admin_or_org_create_user, name='org-create-user'),
    path('org/add-course/', OrganizationAddCourseView.as_view(), name='org-add-course'),
    path('org/batches-with-users/', list_batches_with_users, name='batches-with-users'),
    path('org/view-courses/', org_view_courses, name='org-view-courses'),

    path('org/batches-with-courses/', list_batches_with_courses, name='batches-with-courses'),

    path('api/organization/profile/', OrganizationProfileView.as_view(), name='organization-profile'),

    # 🧑‍🤝‍🧑 Batch Management
    path('org/batches/create/', CreateBatchView.as_view(), name='create-batch'),
    path('org/batches/', list_batches_for_org, name='list-batches'),
    path('org/batches/<int:batch_id>/add-user/', AddUserToBatchView.as_view(), name='assign-user-to-batch'),
    path('org/batches/<int:batch_id>/assign-course/', assign_course_to_batch, name='assign-course-to-batch'),
    path('org/batches/<int:batch_id>/courses/', ListBatchCoursesView.as_view(), name='list-batch-courses'),
    path('org/batches/<int:batch_id>/users/', view_users_in_batch, name='view-users-in-batch'),
    path('org/remove-course-by-name/', remove_course_by_name, name='remove_course_by_name'),
    path('org/batch-courses/', list_all_batch_courses, name='list-all-batch-courses'),

    path('org/batches/<int:batch_id>/remove-user/<str:username>/', remove_user_from_batch, name='remove-user-from-batch'),

    

]
