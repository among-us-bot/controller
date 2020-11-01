"""
Created by Epic at 11/1/20
"""
from custom_types import CogType, ExtendedClient

class MoveToQueue(CogType):
    def __init__(self, bot):
        super().__init__(bot)
        self.loop = self.bot.loop
        self.waiting_in_queue = {}
        self.players_in_a_match = []
        self.banned_players = []

    @CogType.event("VOICE_STATE_UPDATE")
    async def move_to_temp_queue(self, data, shard):
        channel_id = data["channel_id"]
        user_id = data["member"]["user"]["id"]
        guild_id = data["guild_id"]
        config = self.bot.get_config(guild_id)

        # Auto-banning players
        if user_id in self.banned_players:
            args, kwargs = self.bot.payloads.move_member(guild_id, user_id, None)
            await self.bot.workers.request(guild_id, *args, **kwargs)
            return
        if user_id in self.players_in_a_match:
            self.banned_players.append(user_id)
            self.loop.call_later(config.get("autoban-time", 60), lambda: self.banned_players.remove(user_id))
            return
        self.players_in_a_match.append(user_id)
        # Moving to the temp vc
        if channel_id not in config.get("matchmaking-types", {}).keys():
            return
        waiting_vc = config.get("matchmaking-waiting-vc", None)
        if waiting_vc is None:
            return
        args, kwargs = self.bot.payloads.move_member(guild_id, user_id, waiting_vc)
        await self.bot.workers.request(guild_id, *args, **kwargs)
        self.waiting_in_queue[user_id] = {
            "match-type": config["matchmaking-types"][channel_id]["name"],
            "premium": False
        }


def setup(bot: ExtendedClient):
    MoveToQueue(bot)
