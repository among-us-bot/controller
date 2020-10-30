"""
Created by Epic at 10/29/20
"""
from speedcord import Client
from speedcord.exceptions import InvalidToken, Unauthorized
from speedcord.http import Route, HttpClient
from speedcord.shard import DefaultShard
from logging import getLogger
from os import environ as env
from random import choice
from math import ceil


class CustomShard(DefaultShard):
    async def identify(self):
        """
        Sends an identify message to the gateway, which is the initial handshake.
        https://discord.com/developers/docs/topics/gateway#identify
        """
        await self.send({
            "op": 2,
            "d": {
                "token": self.client.token,
                "properties": {
                    "$os": "linux",
                    "$browser": "SpeedCord",
                    "$device": "SpeedCord"
                },
                "intents": self.client.intents,
                "shard": (self.id, self.client.shard_count),
                "presence": {
                    "status": "online",
                    "afk": False,
                    "activities": [{
                        "name": f"Among Us (Crewmate IGN: {getattr(self, 'worker_name')})",
                        "type": 5,
                        "created_at": 0
                    }]
                }
            }
        })


class WorkerClient(Client):
    def __init__(self, worker_name, *args, **kwargs):
        self.worker_name = worker_name
        self.user_id = None
        super().__init__(*args, **kwargs)
        self.event_dispatcher.register("READY", self.handle_ready)

    async def connect(self):
        """
        Connects to discord and spawns shards. Start has to be called first!
        """
        if self.token is None:
            raise InvalidToken

        try:
            gateway_url, shard_count, _, connections_reset_after = await self.get_gateway()
        except Unauthorized:
            self.exit_event.clear()
            raise InvalidToken

        if self.shard_count is None or self.shard_count < shard_count:
            self.shard_count = shard_count

        shard_ids = self.shard_ids or range(self.shard_count)
        for shard_id in shard_ids:
            self.logger.debug(f"Launching shard {shard_id}")
            shard = CustomShard(shard_id, self, loop=self.loop)
            shard.worker_name = self.worker_name
            self.loop.create_task(shard.connect(gateway_url))
            self.shards.append(shard)
        self.connected.set()
        self.logger.info("All shards connected!")

    async def handle_ready(self, data, shard):
        self.user_id = data["user"]["id"]


class WorkerUtil:
    def __init__(self, client: Client):
        with open("worker_names.txt") as f:
            self.worker_names = f.read().split("\n")
        self.client = client
        self.loop = self.client.loop
        self.logger = getLogger("workers.manager")

        self.tokens = env["WORKER_TOKENS"].split(" ")
        self.members_per_worker = int(env["MEMBERS_PER_WORKER"])

        self.worker_counts = {}
        self.workers = []

        # Handlers
        self.client.event_dispatcher.register("GUILD_CREATE", self.on_guild_create)

    async def start(self):
        for index, token in enumerate(self.tokens):
            worker_name = self.worker_names[index]
            worker = WorkerClient(worker_name, 0, token)
            worker.http = HttpClient(worker.token)
            await worker.connect()
            self.workers.append(worker)

    def get_worker_for_guild(self, guild_id: str) -> Client:
        worker_count = self.worker_counts[guild_id]
        worker_pool_for_this_guild = self.workers[:worker_count]
        worker = choice(worker_pool_for_this_guild)
        return worker

    async def request(self, guild_id: str, route: Route, **kwargs):
        worker = self.get_worker_for_guild(guild_id)
        return await worker.http.request(route, **kwargs)

    async def on_guild_create(self, guild, shard):
        worker_count = ceil(guild["member_count"] / self.members_per_worker)
        self.worker_counts[guild["id"]] = worker_count
        self.logger.debug(f"{guild['name']} is now using {worker_count} workers!")
