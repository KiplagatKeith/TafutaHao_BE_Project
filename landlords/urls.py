# landlords/urls.py

from django.urls import path
from . import views
from .views import delete_property_image

app_name = 'landlords'

urlpatterns = [
    path('', views.LandlordDashboardView.as_view(), name='landlord_dashboard'),  # Dashboard

    # Property Management
    path('properties/', views.LandlordPropertyListView.as_view(), name='landlord_property_list'),
    path('add/', views.LandlordPropertyCreateView.as_view(), name='landlord_property_create'),  # renamed
    path('edit/<int:pk>/', views.LandlordPropertyUpdateView.as_view(), name='landlord_property_update'),  # renamed
    path('delete/<int:pk>/', views.LandlordPropertyDeleteView.as_view(), name='landlord_property_delete'),
    path('delete-image/<int:image_id>/', delete_property_image, name='delete_property_image'),
]