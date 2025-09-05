from django.db import models

class Order(models.Model):
    name = models.CharField('Имя', max_length=120)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=60)
    product = models.CharField('Продукт/услуга', max_length=160)
    message = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    ip = models.GenericIPAddressField('IP', null=True, blank=True)
    user_agent = models.TextField('User-Agent', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.product}"
