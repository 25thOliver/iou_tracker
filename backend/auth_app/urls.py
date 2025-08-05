from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'auth_app'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
