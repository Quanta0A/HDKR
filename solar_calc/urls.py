from django.urls import path
from . import views
from .views import index, download_csv

urlpatterns = [
    path('', views.index, name='index'),
    #path('download-xlsx/', views.download_xlsx, name='download_xlsx'), 
     path('download_csv/', views.download_csv, name='download_csv'),
]
