"""
Created by Epic at 10/29/20
"""
from speedcord.http import HttpClient, Route
from aiohttp import ClientSession
from logging import getLogger
from asyncio import Event, get_event_loop
from speedcord import __version__ as speedcord_version, Client
from os import environ as env
from random import choice
from math import ceil


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
    def __init__(self, client: Client):
        with open("worker_names.txt") as f:
            self.worker_names = f.readlines()
        self.client = client
        self.tokens = env["WORKER_TOKENS"].split(" ")
        self.worker_counts = {}
        self.members_per_worker = int(env["MEMBERS_PER_WORKER"])
        self.http = WorkerHttp()
        self.logger = getLogger("workers.manager")

        self.token_to_worker_name = {}
        self.worker_name_to_token = {}
        for index, token in enumerate(self.tokens):
            worker_name = self.worker_names[index]
            self.token_to_worker_name[token] = worker_name
            self.worker_name_to_token[worker_name] = token

        # Handlers
        self.client.event_dispatcher.register("GUILD_CREATE", self.on_guild_create)

    async def request(self, guild_id: int, route: Route, **kwargs):
        selected_tokens = self.tokens[:self.worker_counts[guild_id]]
        token = choice(selected_tokens)
        worker_name = self.token_to_worker_name[token]
        kwargs["token"] = token
        logger = getLogger(f"workers.{worker_name}")
        logger.debug(f"{route.method} {route.path}")
        return await self.http.request(route, **kwargs)

    async def on_guild_create(self, guild, shard):
        worker_count = ceil(guild["member_count"] / self.members_per_worker)
        self.worker_counts[guild["id"]] = worker_count
        self.logger.debug(f"{guild['name']} is now using {worker_count} workers!")
