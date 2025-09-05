from rest_framework import serializers
from .models import Book, Event, RSVP
from django.utils import timezone
import re

class BookSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'year', 'quantity']

    def validate_title(self, v):
        if not v or not v.strip():
            raise serializers.ValidationError('Назва є обов\'язковою.')
        return v.strip()

    def validate_author(self, v):
        if not v or not v.strip():
            raise serializers.ValidationError('Автор є обов\'язковим.')
        return v.strip()

    def validate_year(self, v):
        if v is not None and (v < 0 or v > timezone.now().year + 1):
            raise serializers.ValidationError('Некоректний рік.')
        return v

    def validate_quantity(self, v):
        if v is not None and v < 0:
            raise serializers.ValidationError('Кількість не може бути від\'ємною.')
        return v

class UserRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField()

    def validate_first_name(self, v):
        if len(v) < 2 or not re.match(r'^[A-Za-zА-Яа-яЁёІіЇїЄєҐґ]+$', v):
            raise serializers.ValidationError('Ім\'я: мінімум 2 символи, лише літери.')
        return v

    def validate_last_name(self, v):
        if len(v) < 2 or not re.match(r'^[A-Za-zА-Яа-яЁёІіЇїЄєҐґ]+$', v):
            raise serializers.ValidationError('Прізвище: мінімум 2 символи, лише літери.')
        return v

    def validate_password(self, v):
        # at least 8 chars, one upper, one lower, one digit, one special
        if (len(v) < 8 or
            not re.search(r'[A-Z]', v) or
            not re.search(r'[a-z]', v) or
            not re.search(r'\d', v) or
            not re.search(r'[!@#$%^&*()_+\-=[\]{};:\\|,.<>/?~`]', v)):
            raise serializers.ValidationError('Пароль має містити мінімум 8 символів, велику/маленьку літеру, цифру та спецсимвол.')
        return v

    def validate_phone(self, v):
        # Generic mobile pattern (E.164-like), or strictly UA: +380XXXXXXXXX
        if not re.match(r'^\+?\d{10,15}$', v):
            raise serializers.ValidationError('Номер телефону має відповідати патерну мобільного телефону.')
        return v

class EventSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    creator = serializers.ReadOnlyField(source='creator.id')

    class Meta:
        model = Event
        fields = ['id','title','description','start_at','end_at','location','creator','created_at','updated_at']
        read_only_fields = ['creator','created_at','updated_at']

    def validate(self, attrs):
        start = attrs.get('start_at') or getattr(self.instance, 'start_at', None)
        end = attrs.get('end_at') or getattr(self.instance, 'end_at', None)
        if start and end and end < start:
            raise serializers.ValidationError({'end_at':'Кінець не може бути раніше початку.'})
        return attrs

    def validate_start_at(self, v):
        # allow creating in future or present
        return v

class RescheduleSerializer(serializers.Serializer):
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs):
        start = attrs['start_at']
        if start < timezone.now():
            raise serializers.ValidationError('Нова дата має бути в майбутньому.')
        end = attrs.get('end_at')
        if end and end < start:
            raise serializers.ValidationError('Кінець не може бути раніше початку.')
        return attrs

class RSVPSerializer(serializers.Serializer):
    email = serializers.EmailField()
