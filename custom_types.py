"""
Created by Epic at 10/22/20
"""
from manager import CogManager

from speedcord.client import Client
from speedcord.shard import DefaultShard
from speedcord.exceptions import InvalidToken, Unauthorized


class ExtendedClient(Client):
    def __init__(self, default_prefix, intents: int):
        self.default_prefix = default_prefix
        self.cog_manager = CogManager(self)
        super().__init__(intents)

    async def get_prefix(self, guild):
        return self.default_prefix

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
