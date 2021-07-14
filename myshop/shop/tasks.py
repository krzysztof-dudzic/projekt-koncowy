from celery import task
from django.core.mail import send_mail
from .models import Order

# create order and message

@task
def order_created(order_id):
    order = Order.objects.get(id=order_id)
    subject = f'Zamówienie nr {order.id}'
    message = f'Witaj, {order.first_name}!\n\nZłożyłeś zamówienie w naszym sklepie.' \
              f'Identyfikator zamówienia to {order.id}.'
    mail_sent = send_mail(subject, message, 'admin@myshop.com', [order.email])
    return mail_sent
