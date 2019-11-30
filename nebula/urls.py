from django.urls import path

from nebula import views

urlpatterns = [
    path('generate-config/<member_id>/', views.generate_config_file, name='generate_config'),
    path('join/<member_id>/', views.join_member, name='join_member'),
    path('leave/<member_id>/', views.leave_member, name='leave_member'),
    path('update/<member_id>/', views.update_member, name='update_member')
]
