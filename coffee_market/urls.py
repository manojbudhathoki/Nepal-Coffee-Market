from django.contrib import admin
from django.urls import path, include
from directory import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('producers/', views.producer_list, name='producer_list'),
    path('producer/<slug:slug>/', views.producer_detail, name='producer_detail'),
    path('coffee-guide/', views.coffee_guide, name='coffee_guide'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('about/', views.about, name='about'),
    path('', include('directory.urls')),
]
