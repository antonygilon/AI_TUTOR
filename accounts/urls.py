
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   
    path('register',views.register,name="register"),
    path('logout',views.logout,name="logout"),
    path('home2',views.home2,name="home2"),
    
    path('login',views.login,name="login")
  

]
