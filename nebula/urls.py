from django.urls import path

from nebula import views

urlpatterns = [
    path('generate-config/<member_id>/', views.generate_config_file, name='generate_config')
]
