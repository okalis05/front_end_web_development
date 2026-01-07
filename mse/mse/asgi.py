import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path

import pipeline.routing
import sentinel.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mse.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        # -------------------------
        # HTTP: Sentinel SSE first, then Django
        # -------------------------
        "http": URLRouter(
            sentinel.routing.urlpatterns + [
                # Fallback: everything else → Django
                re_path(r".*", django_asgi_app),
            ]
        ),

        # -------------------------
        # WebSockets: Pipeline
        # -------------------------
        "websocket": AuthMiddlewareStack(
            URLRouter(pipeline.routing.websocket_urlpatterns)
        ),
    }
)

