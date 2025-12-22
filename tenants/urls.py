# tenants/urls.py

from django.urls import path
from .views import (BrowsePropertiesView, 
                    FavoritePropertyView, 
                    FavoritePropertyDeleteView, 
                    TenantProfileView, 
                    RequestViewingView,
                    TenantAccountUpdateView,
                    TenantProfileDeleteView,
)


app_name = 'tenants'

urlpatterns = [
    path('', BrowsePropertiesView.as_view(), name='browse_properties'),
    path('favorite/<int:property_id>/', FavoritePropertyView.as_view(), name='favorite_property'),
    path('favorite/delete/<int:pk>/', FavoritePropertyDeleteView.as_view(), name='favorite_delete'),
    path('profile/', TenantProfileView.as_view(), name='tenant_profile'),

    path('request-viewing/<int:property_id>/', RequestViewingView.as_view(), name='request_viewing'),

    path('account/edit/', TenantAccountUpdateView.as_view(), name='tenant_account_edit'),
    path('profile/delete/', TenantProfileDeleteView.as_view(), name='tenant_profile_delete'),
]