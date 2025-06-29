from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Public homepage
def homepage(request):
    if request.user.is_authenticated:
        return redirect_after_login(request)  # Automatically redirect if logged in
    return render(request, 'users/homepage.html')

# Shared dashboard for faculty & students
@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')

# Redirect after login based on user type
@login_required
def redirect_after_login(request):
    if request.user.type == 'ADMIN':
        return redirect('/admin/')  # Redirect to Django admin panel
    return redirect('dashboard')  # Faculty/Student go to dashboard
