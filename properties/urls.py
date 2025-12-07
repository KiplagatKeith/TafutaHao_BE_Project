# properties/urls.py

from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='property_list'),  # List all properties
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),  # Property detail
    path('ajax/get-towns/', views.get_towns_by_county, name='get_towns_by_county'),
]
