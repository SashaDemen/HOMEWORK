from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, EventViewSet

# Routers are declared in project urls; this file is not used directly.
