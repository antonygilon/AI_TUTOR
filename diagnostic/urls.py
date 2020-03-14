
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   
    path('test',views.test,name="test"),
    path('upload',views.upload,name="upload"),
    path('upload2',views.upload2,name="upload2"),
    path('attend',views.attend,name="attend"),
    path('upload3',views.upload3,name="upload3"),
    path('store',views.store,name="store"),
    path('delete',views.delete,name="delete"),
    path('score',views.score,name="score"),
    path('dynamic_test',views.dynamic_test,name="dynamic_test"),
    path('dynamic_test2',views.dynamic_test2,name="dynamic_test2"),
    path('help',views.help,name="help"),

    
    
    
  

]
