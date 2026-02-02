from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_email_view(request):
    email = request.GET.get('email')  # or POST data

    subject = "Your new order and payment is successful"
    message = "Stay awake, wait for your order and enjoy"
    from_email = "yourmail@gmail.com"
    recipient_list = [email]

    html_message = render_to_string("bill_invoice_temp.html")
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        return HttpResponse("Email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Error sending email: {str(e)}")