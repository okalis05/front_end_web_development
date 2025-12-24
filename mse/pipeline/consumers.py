import json
from channels.generic.websocket import AsyncWebsocketConsumer


class PipelineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.pipeline_slug = self.scope["url_route"]["kwargs"]["pipeline_slug"]
        self.group_name = f"pipeline_{self.pipeline_slug}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "connected",
            "scope": "pipeline",
            "pipeline": self.pipeline_slug,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def pipeline_update(self, event):
        await self.send(text_data=json.dumps(event.get("payload", {})))


class RunConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.run_id = self.scope["url_route"]["kwargs"]["run_id"]
        self.group_name = f"run_{self.run_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            "type": "connected",
            "scope": "run",
            "run_id": self.run_id,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def run_update(self, event):
        await self.send(text_data=json.dumps(event.get("payload", {})))
