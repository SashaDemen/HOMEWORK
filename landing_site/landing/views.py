from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from .models import Order

@ensure_csrf_cookie
def index(request: HttpRequest):
    return render(request, 'landing/index.html', {})

@require_POST
def create_order(request: HttpRequest):
    # Honeypot field
    if (request.POST.get('website') or '').strip():
        return JsonResponse({'ok': False, 'error': 'Spam detected'}, status=400)

    name = (request.POST.get('name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    phone = (request.POST.get('phone') or '').strip()
    product = (request.POST.get('product') or '').strip()
    message = (request.POST.get('message') or '').strip()

    errors = {}
    if not name or len(name) < 2:
        errors['name'] = 'Укажите имя'
    if not email or '@' not in email:
        errors['email'] = 'Невалидный email'
    if not phone:
        errors['phone'] = 'Укажите телефон'
    if not product:
        errors['product'] = 'Выберите продукт/услугу'

    if errors:
        return JsonResponse({'ok': False, 'errors': errors}, status=400)

    order = Order.objects.create(
        name=name, email=email, phone=phone, product=product, message=message,
        ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT','')
    )
    return JsonResponse({'ok': True, 'message': 'Спасибо! Заявка отправлена.'})
