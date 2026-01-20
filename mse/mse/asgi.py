import os
from django.core.asgi import get_asgi_application
from django.urls import re_path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import sentinel.routing
import pipeline.routing
import javascript_viz.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mse.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        # -------------------------
        # HTTP: Sentinel SSE routes first, then Django fallback
        # -------------------------
        "http": URLRouter(
            sentinel.routing.urlpatterns + [
                re_path(r".*", django_asgi_app),
            ]
        ),

        # -------------------------
        # WebSockets: combine ALL websocket routes in one URLRouter
        # -------------------------
        "websocket": AuthMiddlewareStack(
            URLRouter(
                pipeline.routing.websocket_urlpatterns
                + javascript_viz.routing.websocket_urlpatterns
            )
        ),
    }
)
