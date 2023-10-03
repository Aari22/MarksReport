from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.user_login, name='login'),  # Update the URL pattern for the empty path
    path('register/', views.register, name='register'),
    path('subject_details/', views.subject_details, name='subject_details'),
    path('generate_report1/', views.generate_report1, name='generate_report1'),
    path('generate_report2/', views.generate_report2, name='generate_report2'),
    path('list_entries/', views.list_entries, name='list_entries'),
    path('logout/', views.logout, name='logout'),
]
