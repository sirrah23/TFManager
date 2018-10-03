from django.contrib.auth import views
from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.auth_login, name='login'),
    path('logout/', views.auth_logout, name='logout'),
    path('folder/<int:folder_id>/', views.folder, name='folder'),
    path('folder/create/', views.folder_create, name='folder_create'),
    path('file/<int:file_id>/', views.file, name='file'),
    path('file/edit/<int:file_id>/', views.file_edit, name='file_edit'),
    path('file/<int:file_id>/version/<int:version_num>/',
         views.file_ver, name='file_ver'),
    path('file/<int:file_id>/history/', views.file_hist, name='file_hist'),
    path('file/create/', views.file_create, name='file_create')
]
