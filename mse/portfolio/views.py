from django.shortcuts import render
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from twilio.rest import Client

# Create your views here.
def about(request):
    return render(request , "portfolio/about.html")

def projects(request):
    return render(request , "portfolio/projects.html")

def skills(request):
    return render(request , "portfolio/skills.html")

def contacts(request):
    return render(request , "portfolio/contacts.html")


def contact_submit(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # ---- EMAIL ----
        send_mail(
            subject=f"Portfolio Contact from {name}",
            message=f"From: {name}\nEmail: {email}\n\nMessage:\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["okalis05@yahoo.com"],
            fail_silently=False,
        )

        # ---- SMS (Twilio) ----
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

        client.messages.create(
            body=f"📩 Portfolio Message\nFrom: {name}\nEmail: {email}\n\n{message}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to="+15135109397",
        )

        messages.success(request, "Message sent successfully!")
        return redirect("portfolio:about")

