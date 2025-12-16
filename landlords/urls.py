# landlords/urls.py

from django.urls import path
from . import views
from .views import delete_property_image

app_name = 'landlords'

urlpatterns = [
    # Dashboard
    path('', views.LandlordDashboardView.as_view(), name='landlord_dashboard'),

    # Property Management
    path('properties/', views.LandlordPropertyListView.as_view(), name='landlord_property_list'),
    path('add/', views.LandlordPropertyCreateView.as_view(), name='landlord_property_create'),
    path('edit/<int:pk>/', views.LandlordPropertyUpdateView.as_view(), name='landlord_property_update'),
    path('delete/<int:pk>/', views.LandlordPropertyDeleteView.as_view(), name='landlord_property_delete'),
    path('delete-image/<int:image_id>/', delete_property_image, name='delete_property_image'),

    # Browse All Properties (Landlords view as tenants)
    path('browse/', views.LandlordBrowsePropertiesView.as_view(), name='landlords_browse'),

    # Landlord Property Detail
    path('properties/<int:pk>/', views.LandlordPropertyDetailView.as_view(), name='landlord_property_detail'),

    # Favorite / Unfavorite Property
    path('favorite/<int:property_id>/', views.LandlordFavoritePropertyView.as_view(), name='favorite_property'),
]
