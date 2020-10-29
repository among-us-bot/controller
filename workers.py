"""
Created by Epic at 10/29/20
"""
from speedcord.http import Route
from logging import getLogger
from speedcord import Client
from os import environ as env
from random import choice
from math import ceil


class WorkerUtil:
    def __init__(self, client: Client):
        with open("worker_names.txt") as f:
            self.worker_names = f.readlines()
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
            worker = Client(0, token)
            worker.name = self.worker_names[index]
            await worker.connect()
            for shard in worker.shards:
                await shard.send({
                    "op": 3,
                    "d": {
                        "since": 0,
                        "activities": [
                            {
                                "name": f"Among Us (Crewmate IGN: {worker.name})"
                            }
                        ]
                    }
                })

    def get_worker_for_guild(self, guild_id: int) -> Client:
        worker_count = self.worker_counts[guild_id]
        worker_pool_for_this_guild = self.workers[:worker_count]
        worker = choice(worker_pool_for_this_guild)
        return worker

    async def request(self, guild_id: int, route: Route, **kwargs):
        worker = self.get_worker_for_guild(guild_id)
        return await worker.http.request(route, **kwargs)

    async def on_guild_create(self, guild, shard):
        worker_count = ceil(guild["member_count"] / self.members_per_worker)
        self.worker_counts[guild["id"]] = worker_count
        self.logger.debug(f"{guild['name']} is now using {worker_count} workers!")
