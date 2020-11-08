"""
Created by Epic at 11/1/20
"""
from custom_types import CogType, ExtendedClient

from asyncio import Lock
from speedcord.http import Route


class Queue(CogType):
    def __init__(self, bot):
        super().__init__(bot)
        self.loop = self.bot.loop
        self.waiting_in_queue = {}
        self.players_in_queue = []
        self.banned_players = []
        self.categories = {}
        self.category_locks = {}
        self.move_to_games_locks = {}
        self.max_category_uses = 50

    async def get_category(self, guild_id: str):
        lock = self.category_locks.get(guild_id, None)
        if lock is None:
            lock = Lock()
            self.category_locks[guild_id] = lock
        async with lock:
            guild_categories = self.categories.get(guild_id, None)
            if guild_categories is None:
                guild_categories = {}
                self.categories[guild_id] = guild_categories
            for category_id, category_uses in self.categories.get(guild_id, None).items():
                if category_uses >= self.max_category_uses:
                    continue
                category_uses += 1
                self.categories[guild_id][category_id] = category_uses
                return category_id
            route = Route("POST", "/guilds/{guild_id}/channels", guild_id=guild_id)
            response = await self.bot.http.request(route, json={
                "name": "aque-lobby",
                "type": 4
            })
            response_data = await response.json()
            self.categories[guild_id][response_data["id"]] = 1
            self.logger.debug(f"Created new category in guild {guild_id}")
            return response_data["id"]

    @CogType.event("VOICE_STATE_UPDATE")
    async def move_to_temp_queue(self, data, shard):
        channel_id = data["channel_id"]
        user_id = data["member"]["user"]["id"]
        guild_id = data["guild_id"]
        config = self.bot.get_config(guild_id)

        # Moving to the temp vc
        if channel_id not in config.get("matchmaking-types", {}).keys():
            return

        # Yeeting banned players
        if user_id in self.banned_players:
            args, kwargs = self.bot.payloads.move_member(guild_id, user_id, None)
            await self.bot.workers.request(guild_id, *args, **kwargs)
            return

        waiting_vc = config.get("matchmaking-waiting-vc", None)
        if waiting_vc is None:
            return
        currently_waiting_in_queue = self.waiting_in_queue.get(guild_id, None)
        if currently_waiting_in_queue is None:
            currently_waiting_in_queue = []
        currently_waiting_in_queue.append({
            "id": user_id,
            "match-type": config["matchmaking-types"][channel_id]["name"],
            "matchmaking-channel-id": channel_id,
            "premium": False
        })
        self.waiting_in_queue[guild_id] = currently_waiting_in_queue
        args, kwargs = self.bot.payloads.move_member(guild_id, user_id, waiting_vc)
        await self.bot.workers.request(guild_id, *args, **kwargs)

    @CogType.event("VOICE_STATE_UPDATE")
    async def move_to_games(self, data: dict, shard):
        channel_id = data["channel_id"]
        user_id = data["member"]["user"]["id"]
        guild_id = data["guild_id"]
        config = self.bot.get_config(guild_id)
        lock = self.move_to_games_locks.get(guild_id, None)

        if channel_id != config.get("matchmaking-waiting-vc", None):
            return

        if lock is None:
            lock = Lock()
            self.move_to_games_locks[guild_id] = lock
        async with lock:
            if user_id in self.players_in_queue:
                return
            self.players_in_queue.append(user_id)
            game_counts = {}
            game_players = {}
            gamemode_players = {}
            current_players = self.waiting_in_queue[guild_id].copy()
            for player in current_players:
                match_type = player["match-type"]

                in_this_queue = game_counts.get(match_type, 0)
                in_this_queue += 1
                game_counts[match_type] = in_this_queue

                current_players_in_gametype = game_players.get(match_type, [])
                current_players_in_gametype.append(player)
                game_players[match_type] = current_players_in_gametype

                if in_this_queue >= config["matchmaking-types"][player["matchmaking-channel-id"]]["required_users"]:
                    self.logger.debug(f"Moving players to lobby. Guild id: {guild_id}. Match type: {match_type}")
                    category_id = await self.get_category(guild_id)
                    route = Route("POST", "/guilds/{guild_id}/channels", guild_id=guild_id)
                    response = await self.bot.http.request(route, json={
                        "name": "aque-lobby",
                        "parent_id": category_id,
                        "type": 2
                    })
                    response_data = await response.json()
                    game_vc = response_data["id"]
                    for to_be_moved in game_players[match_type]:
                        to_be_moved_id = to_be_moved["id"]
                        self.waiting_in_queue[guild_id].remove(to_be_moved)
                        args, kwargs = self.bot.payloads.move_member(guild_id, to_be_moved_id, game_vc)
                        await self.bot.workers.request(guild_id, *args, **kwargs)
                    return


def setup(bot: ExtendedClient):
    Queue(bot)
