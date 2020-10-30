"""
Created by Epic at 10/22/20
"""
from cog_manager import CogManager
from workers import WorkerUtil
from payloads import Payloads

from speedcord.client import Client
from speedcord.shard import DefaultShard
from speedcord.exceptions import InvalidToken, Unauthorized


class ExtendedClient(Client):
    def __init__(self, default_prefix, intents: int):
        super().__init__(intents)
        self.default_prefix = default_prefix
        self.cog_manager = CogManager(self)
        self.workers = WorkerUtil(self)
        self.payloads = Payloads()

    async def get_prefix(self, guild):
        return self.default_prefix

    async def connect(self):
        """
        Connects to discord and spawns shards. Start has to be called first!
        """
        await self.workers.start()
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
            self.loop.create_task(shard.connect(gateway_url))
            self.shards.append(shard)
        self.connected.set()
        self.logger.info("All shards connected!")


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
                        "name": "Among Us (Imposter)",  # Imposter is the controller, Crewmate 1, 2, 3... is workers
                        "type": 5,
                        "created_at": 0
                    }]
                }
            }
        })


class CogType:
    def __init__(self, client: ExtendedClient):
        self.client = client
        for attr_name in dir(self):
            func = getattr(self, attr_name)
            command_syntax = getattr(func, "__command_syntax__", None)
            if command_syntax is not None:
                self.client.cog_manager.register_command(func, command_syntax)

            event_name = getattr(func, "__event_name__", None)
            if event_name is not None:
                self.client.event_dispatcher.register(event_name, func)

    @staticmethod
    def command(command_syntax=None):
        def inner(func):
            nonlocal command_syntax
            if command_syntax is None:
                command_syntax = func.__name__
            func.__command_syntax__ = command_syntax
            return func

        return inner

    @staticmethod
    def event(event_name=None):
        def inner(func):
            nonlocal event_name
            if event_name is None:
                event_name = func.__name__[2:]
            func.__event_name__ = event_name
            return func

        return inner
