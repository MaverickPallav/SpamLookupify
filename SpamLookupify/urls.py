from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    ContactListCreateView,
    ContactDetailView,
    ReportSpamView,
    SearchView,
    LogoutView,
)

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/contacts/', ContactListCreateView.as_view(), name='contact-list-create'),
    path('api/contacts/<int:contact_id>/', ContactDetailView.as_view(), name='contact-detail'),
    path('api/report-spam/', ReportSpamView.as_view(), name='report-spam'),
    path('api/search/', SearchView.as_view(), name='search'),
]