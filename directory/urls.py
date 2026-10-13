from django.urls import path
from . import views
urlpatterns = [
 path('history/', views.coffee_history, name='coffee_history'), path('contact/', views.contact, name='contact'),
 path('accounts/register/', views.register, name='register'), path('accounts/login/', views.user_login, name='login'), path('accounts/logout/', views.user_logout, name='logout'),
 path('buyer-dashboard/', views.buyer_dashboard, name='buyer_dashboard'), path('favourites/', views.favourites, name='favourites'), path('producer-dashboard/', views.producer_dashboard, name='producer_dashboard'), path('producer-dashboard/profile/', views.edit_producer_profile, name='edit_producer_profile'), path('producer-dashboard/products/add/', views.add_product, name='add_product'), path('producer-dashboard/products/<int:product_id>/edit/', views.edit_product, name='edit_product'), path('producer-dashboard/products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
 path('producer/<slug:slug>/save/', views.toggle_favorite, name='toggle_favorite'), path('producer/<slug:slug>/review/', views.submit_review, name='submit_review'), path('producer/<slug:slug>/claim/', views.claim_producer, name='claim_producer'),
]
