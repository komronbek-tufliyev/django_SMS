from django.urls import path
from users import views


urlpatterns = [
    path('', views.homeView, name='home'),
    path('my-account/', views.loginView, name='my-account'),
    path('my-account/register/', views.registerView, name='register'),
    path('my-account/logout/', views.logoutView, name='logout'),
    path('confirm-verify-code/', views.verifyView, name='confirm'),
    path('users-info/', views.show_user_info, name='users-info'),
]
