from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catalog.views import BookViewSet, EventViewSet, register_user

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/users/register/', register_user, name='register_user'),
]
