"""
Created by Epic at 10/29/20
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from custom_types import ExtendedClient as Client
else:
    from speedcord import Client
from speedcord.http import Route
from logging import getLogger
from aiohttp import ClientWebSocketResponse
from ujson import dumps
from os import environ as env


class WorkerUtil:
    def __init__(self, client: Client):
        self.client = client
        self.loop = self.client.loop
        self.logger = getLogger("workers.manager")
        self.ws: ClientWebSocketResponse = None

    async def start(self):
        self.ws = await self.client.http.create_ws(env["WORKER_MANAGER_HOST"])

    async def request(self, guild_id: str, route: Route, **kwargs):
        await self.send_ws("request", {
            "guild_id": guild_id,
            "data": {
                "method": route.method,
                "path": route.path,
                "route_params": {
                    "guild_id": route.guild_id,
                    "channel_id": route.channel_id,
                    "kwargs": kwargs
                }
            }
        })

    async def send_ws(self, event_name, event_data):
        await self.ws.send_json({"t": event_name, "d": event_data}, dumps=dumps)
