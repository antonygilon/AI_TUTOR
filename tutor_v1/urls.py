from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
#path('compute_probability/<int>',)
path('upload_questions/', views.upload_questions),  
path('diagnostic-test/',views.create_diagnostic_test),
path('update-model/',views.update_hmm),

]