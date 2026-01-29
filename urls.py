from django.urls import path
from . import views

urlpatterns = [

    path('', views.home_view, name='design-home'),

    path('projects/', views.ProjectListView.as_view(), name='projects-list'),
    path('projects/add/', views.ProjectCreateView.as_view(), name='project-create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project-update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('about/', views.about_view, name='design-about'),
    # Calendar and events
    path('calendar/', views.calendar_view, name='calendar'),
    path('events/add/', views.event_create_view, name='event-create'),
    # Service landing pages
    path('services/planning/', views.service_planning_view, name='service-planning'),
    path('services/waste/', views.service_waste_view, name='service-waste'),
    path('services/taxation/', views.service_taxation_view, name='service-taxation'),
    path('services/licenses/', views.service_licenses_view, name='service-licenses'),
    path('services/request/', views.service_request_view, name='service-request'),
    path('contact/', views.contact_view, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
    # Event detail + calendar
    path('events/<int:pk>/', views.event_detail_view, name='event-detail'),
    path('meetings/<int:pk>/', views.meeting_detail_view, name='meeting-detail'),
    path('cost-of-living/', views.cost_of_living_view, name='cost-of-living'),
    # Supplier CRUD
    path('suppliers/', views.SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier-create'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier-detail'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier-update'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier-delete'),
]
