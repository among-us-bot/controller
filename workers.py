"""
Created by Epic at 10/29/20
"""
from speedcord.http import HttpClient, Route
from aiohttp import ClientSession
from logging import getLogger
from asyncio import Event, get_event_loop
from speedcord import __version__ as speedcord_version
from os import environ as env
from ujson import loads
from random import choice


class WorkerHttp(HttpClient):
    def __init__(self, *, baseuri="https://discord.com/api/v7", loop=get_event_loop()):
        """
        An http client which handles discord ratelimits.
        :param baseuri: Discord's API uri.
        :param loop: an asyncio.AbstractEventLoop to use for callbacks.
        """
        self.baseuri = baseuri
        self.loop = loop
        self.session = ClientSession()
        self.logger = getLogger("speedcord.http")

        self.ratelimit_locks = {}
        self.global_lock = Event(loop=self.loop)

        # Clear the global lock on start
        self.global_lock.set()

        self.default_headers = {
            "X-RateLimit-Precision": "millisecond",
            "User-Agent": f"DiscordBot (https://github.com/TAG-Epic/speedcord {speedcord_version})"
        }

        self.retry_attempts = 3

    async def request(self, route: Route, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Token {kwargs['token']}"
        kwargs["headers"] = headers
        return super().request(route, **kwargs)


class WorkerUtil:
    def __init__(self):
        with open("worker_names.txt") as f:
            self.worker_names = f.readlines()
        self.tokens = env["WORKER_TOKENS"].split(" ")
        self.worker_counts = loads(env["WORKER_COUNTS"])
        self.http = WorkerHttp()

        self.token_to_worker_name = {}
        self.worker_name_to_token = {}
        for index, token in enumerate(self.tokens):
            worker_name = self.worker_names[index]
            self.token_to_worker_name[token] = worker_name
            self.worker_name_to_token[worker_name] = token

    async def request(self, guild_id: int, route: Route, **kwargs):
        selected_tokens = self.tokens[:self.worker_counts[guild_id]]
        token = choice(selected_tokens)
        worker_name = self.token_to_worker_name[token]
        kwargs["token"] = token
        logger = getLogger(f"workers.{worker_name}")
        logger.debug(f"{route.method} {route.path}")
        return await self.http.request(route, **kwargs)
