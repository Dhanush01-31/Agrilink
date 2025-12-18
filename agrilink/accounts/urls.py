from django.urls import path
from .views import (
    home,
    signup_view,
    login_view,
    dashboard,
    logout_view,
    farmer_dashboard,
    delete_farmer_details,
    cancel_request,
    landowner_dashboard
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),

    path('farmer/dashboard/', farmer_dashboard, name='farmer_dashboard'),
    path('farmer/delete/<int:pk>/', delete_farmer_details, name='delete_farmer_details'),
    path('farmer/cancel-request/<int:pk>/', cancel_request, name='cancel_request'),
    path('landowner/dashboard/', landowner_dashboard, name='landowner_dashboard'),
]
