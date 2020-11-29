from django.urls import path

from app.views.submits import upload

urlpatterns = [
    path('upload/', upload, name='submit')
]

app_name = 'app'