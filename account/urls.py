from django.urls import path
from .views import UserRegistrationView,UserLoginView,UserProfileView,UserLogoutView,activate

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user-profile'),
    path('active/<uid64>/<token>', activate, name='activate'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]

