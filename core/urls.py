from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'), 
    path('portfolio/', views.portfolio_view, name='portfolio'), 
    path('history/', views.history_view, name='history'), 
    path('trade/', views.trade, name='trade'),
]