# accounts/urls.py
from django.urls import path
from .views import (
    home, signup_view, login_view, dashboard, logout_view,
    farmer_dashboard, landowner_dashboard, customer_dashboard,
    delete_land, cancel_request
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),

    path('farmer/dashboard/', farmer_dashboard, name='farmer_dashboard'),
    path('landowner/dashboard/', landowner_dashboard, name='landowner_dashboard'),
    path('customer/dashboard/', customer_dashboard, name='customer_dashboard'),

    path('landowner/delete-land/<int:pk>/', delete_land, name='delete_land'),
    path('farmer/cancel-request/<int:pk>/', cancel_request, name='cancel_request'),
]
