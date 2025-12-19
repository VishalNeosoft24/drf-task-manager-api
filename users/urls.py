from . import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('', view=views.UserListCreateViews.as_view(), name='user_create'),
    path('<int:pk>/', view=views.UserDetailsView.as_view(), name='user_details'),
    path('<int:pk>/new/', view=views.UserDetailsGenericView.as_view(), name='user_details'),
    path('user_login/', view=views.UserLoginView.as_view(), name='user_login'),

    # Get Access + Refresh Token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Refresh Access Token
    path('token/refresh/', views.CookieTokenRefreshView.as_view(), name='token_refresh'),

    # Optional – verify token validity
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]