from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main Trading Floors
    path('', views.dashboard, name='dashboard'),
    path('portfolio/', views.portfolio_view, name='portfolio'),
    path('trade/', views.trade, name='trade'),
    
    # ADD THIS LINE RIGHT HERE:
    path('history/', views.history_view, name='history'),

    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- PASSWORD RESET URLS ---
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(template_name='core/password_reset.html'), 
         name='password_reset'),
    
    path('reset_password_sent/', 
         auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_sent.html'), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_form.html'), 
         name='password_reset_confirm'),
    
    path('reset_password_complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), 
         name='password_reset_complete'),
         
     # Path to Watchlist
    path('toggle-watchlist/', views.toggle_watchlist, name='toggle_watchlist'),

     #profile
    path('profile/', views.profile_view, name='profile'),
     
     #Tutorial.
    path('tutorial/', views.tutorial_view, name='tutorial'),

]