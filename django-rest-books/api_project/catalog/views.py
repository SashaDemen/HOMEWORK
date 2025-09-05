from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Book, Event, RSVP
from .serializers import BookSerializer, UserRegistrationSerializer, EventSerializer, RescheduleSerializer, RSVPSerializer
from .permissions import IsStaffOrReadOnly

# -------- Part 1: Books --------
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('id')
    serializer_class = BookSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def list(self, request, *args, **kwargs):
        # GET /books -> 200 with list
        qs = self.get_queryset()
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # POST /books -> 201 on success
        ser = self.get_serializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        # GET /books/{id} -> 200 or 404 handled by DRF
        return super().retrieve(request, *args, **kwargs)

# -------- Part 2: Registration with deep validation --------
@api_view(['POST'])
def register_user(request):
    ser = UserRegistrationSerializer(data=request.data)
    if not ser.is_valid():
        return Response({'ok': False, 'errors': ser.errors}, status=status.HTTP_400_BAD_REQUEST)

    data = ser.validated_data
    # If a user with email already exists (using username=email for simplicity)
    if User.objects.filter(username=data['email']).exists():
        return Response({'ok': False, 'errors': {'email': ['Користувач з таким email вже існує.']}}, status=status.HTTP_409_CONFLICT)

    user = User.objects.create_user(
        username=data['email'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        password=data['password'],
    )
    # phone can be stored elsewhere; for brevity we ignore persistence of phone
    return Response({'ok': True, 'id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)

# -------- Part 3: Events with specific codes --------
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-start_at')
    serializer_class = EventSerializer
    permission_classes = [IsStaffOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if not qs.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # 403 if no permission
        if not self.check_permissions(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        ser = self.get_serializer(data=request.data)
        if ser.is_valid():
            event = ser.save(creator=request.user if request.user.is_authenticated else None)
            out = self.get_serializer(event).data
            return Response(out, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        # PUT /events/{id}
        try:
            event = self.get_queryset().get(pk=kwargs['pk'])
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 403 if no permission
        if not (request.user and request.user.is_authenticated and request.user.is_staff):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # 422 if trying to change forbidden fields
        allowed = {'title','description','start_at','end_at','location'}
        extra = set(request.data.keys()) - allowed
        if extra:
            return Response({'detail': f'Заборонені для зміни поля: {sorted(list(extra))}'}, status=422)

        ser = self.get_serializer(event, data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_200_OK)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        # DELETE /events/{id}
        try:
            event = self.get_queryset().get(pk=kwargs['pk'])
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not (request.user and request.user.is_authenticated and request.user.is_staff):
            return Response(status=status.HTTP_403_FORBIDDEN)

        event.delete()
        return Response({'detail':'Видалено'}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            event = self.get_queryset().get(pk=kwargs['pk'])
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        ser = self.get_serializer(event)
        return Response(ser.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='reschedule')
    def reschedule(self, request, pk=None):
        # PATCH /events/{id}/reschedule
        try:
            event = self.get_queryset().get(pk=pk)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        ser = RescheduleSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        data = ser.validated_data
        event.start_at = data['start_at']
        if 'end_at' in data:
            event.end_at = data['end_at']
        event.save()
        return Response(self.get_serializer(event).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='rsvp')
    def rsvp(self, request, pk=None):
        # POST /events/{id}/rsvp
        try:
            event = self.get_queryset().get(pk=pk)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        ser = RSVPSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        email = ser.validated_data['email']
        if RSVP.objects.filter(event=event, user_email=email).exists():
            return Response({'detail':'Користувач вже зареєстрований'}, status=status.HTTP_409_CONFLICT)
        RSVP.objects.create(event=event, user_email=email)
        return Response({'detail':'Реєстрацію підтверджено'}, status=status.HTTP_200_OK)
