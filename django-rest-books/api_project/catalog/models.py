from django.db import models
from django.contrib.auth import get_user_model

class Book(models.Model):
    title = models.CharField('Назва', max_length=255)
    author = models.CharField('Автор', max_length=255)
    year = models.IntegerField('Рік видання', null=True, blank=True)
    quantity = models.IntegerField('Доступна кількість', default=0)

    def __str__(self):
        return f"{self.title} — {self.author}"

class Event(models.Model):
    title = models.CharField('Назва', max_length=255)
    description = models.TextField('Опис', blank=True)
    start_at = models.DateTimeField('Початок')
    end_at = models.DateTimeField('Завершення', null=True, blank=True)
    location = models.CharField('Локація', max_length=255, blank=True)
    creator = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='events')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class RSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user_email')

    def __str__(self):
        return f"{self.user_email} -> {self.event_id}"
