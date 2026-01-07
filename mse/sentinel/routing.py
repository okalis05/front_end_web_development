# sentinel/routing.py
from django.urls import re_path
from sentinel.consumers import SentinelSSEConsumer


urlpatterns = [
    re_path(
        r"^sentinel/stream/(?P<industry_key>sports|mortgage|retail|healthcare)/$",
        SentinelSSEConsumer.as_asgi(),
    ),
]
