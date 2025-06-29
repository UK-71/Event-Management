from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    
    path('', users_views.homepage, name='homepage'),  # Public homepage
    path('dashboard/', users_views.dashboard, name='dashboard'),  # Faculty/Student dashboard
    path('redirect/', users_views.redirect_after_login, name='redirect_after_login'),  # Logic redirect
]
