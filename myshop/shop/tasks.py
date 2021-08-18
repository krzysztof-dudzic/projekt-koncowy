from celery import task
from django.core.mail import send_mail
from .models import Order
from django.core.mail import EmailMessage
from io import BytesIO
from django.template.loader import render_to_string
from django.conf import settings
import weasyprint

# create order and message


@task
def order_created(order_id):
    order = Order.objects.get(id=order_id)
    subject = f'Order nr {order.id}'
    message = f'Dear, {order.first_name}!\n\nYou have successfully placed an order.' \
              f'Your order ID is  {order.id}.'
    mail_sent = send_mail(subject, message, 'admin@myshop.com', [order.email])
    return mail_sent


@task
def payment_completed(order_id):
    order = Order.objects.get(id=order_id)
    subject = f'My shop - EE Invoice nr {order.id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject, message, 'admin@myshop.com', [order.email])
    html = render_to_string('shop/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    email.send()
