from __future__ import annotations

import asyncio
import json
import time
from channels.generic.http import AsyncHttpConsumer


class SentinelSSEConsumer(AsyncHttpConsumer):
    """
    SSE stream consumer.
    Clients connect to /sentinel/stream/<industry_key>/
    We join a Channels group and forward emitted messages to the browser.
    """

    async def handle(self, body: bytes):
        # Extract industry key from the URL route kwargs
        industry_key = self.scope.get("url_route", {}).get("kwargs", {}).get("industry_key", "")
        if not industry_key:
            await self.send_response(400, b"Missing industry key", headers=[(b"Content-Type", b"text/plain")])
            return

        # Group per industry
        self.group_name = f"sentinel.{industry_key}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        headers = [
            (b"Content-Type", b"text/event-stream; charset=utf-8"),
            (b"Cache-Control", b"no-cache, no-transform"),
            (b"Connection", b"keep-alive"),
            (b"X-Accel-Buffering", b"no"),
        ]
        await self.send_headers(headers=headers)

        # Initial hello + heartbeat interval
        await self._send_sse(event="hello", data={"ok": True, "industry_key": industry_key, "ts": time.time()})

        last_heartbeat = time.time()

        try:
            while True:
                # heartbeat comment every 15s
                now = time.time()
                if now - last_heartbeat >= 15:
                    await self.send_body(b": heartbeat\n\n", more_body=True)
                    last_heartbeat = now

                # Wait for group messages
                try:
                    msg = await asyncio.wait_for(self.channel_layer.receive(self.channel_name), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                # Channels internal messages have "type"
                if not msg:
                    continue

                # Our emits use type="sentinel.message"
                if msg.get("type") == "sentinel.message":
                    event = msg.get("event", "message")
                    payload = msg.get("payload", {})
                    await self._send_sse(event=event, data=payload)

        except asyncio.CancelledError:
            # normal shutdown
            pass
        finally:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await self.send_body(b"", more_body=False)

    async def sentinel_message(self, event):
        """
        Optional: Channels can dispatch to this method if using handler routing,
        but we're explicitly receiving in the loop above.
        """
        return

    async def _send_sse(self, *, event: str, data: dict):
        blob = json.dumps(data, ensure_ascii=False)
        chunk = f"event: {event}\ndata: {blob}\n\n".encode("utf-8")
        await self.send_body(chunk, more_body=True)
