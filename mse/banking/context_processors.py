from django.conf import settings

def banking_ai_flags(request):
    return {
        "BANKING_AI_ENABLED": getattr(settings, "BANKING_AI_ENABLED", False)
    }
