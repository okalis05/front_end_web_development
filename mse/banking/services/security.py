import random
from django.utils.timezone import now, timedelta
from banking.models import BankingOTP

def generate_otp(user):
    code = str(random.randint(100000, 999999))
    BankingOTP.objects.create(
        user=user,
        code=code,
        expires_at=now() + timedelta(minutes=5)
    )
    print("OTP (demo):", code)  # replace with SMS/email later
    return code

def verify_otp(user, code):
    try:
        otp = BankingOTP.objects.filter(user=user).latest("expires_at")
        return otp.code == code and otp.is_valid()
    except BankingOTP.DoesNotExist:
        return False
