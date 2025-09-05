from django.contrib import admin
from .models import Book, Event, RSVP

admin.site.register(Book)
admin.site.register(Event)
admin.site.register(RSVP)
