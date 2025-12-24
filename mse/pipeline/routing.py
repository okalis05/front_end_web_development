from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/pipeline/(?P<pipeline_slug>[-\w]+)/$", consumers.PipelineConsumer.as_asgi()),
    re_path(r"ws/run/(?P<run_id>\d+)/$", consumers.RunConsumer.as_asgi()),
]
