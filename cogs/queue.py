"""
Created by Epic at 11/1/20
"""
from custom_types import CogType, ExtendedClient

from asyncio import Lock, sleep
from speedcord.http import Route
from cog_manager import CommandContext


class DefaultDict(dict):
    def __init__(self, default, *args, **kwargs):
        self.default_value = default
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        value = self.get(item, None)
        if value is not None:
            return value
        value = self.default_value()
        self[item] = value
        return value


class Queue(CogType):
    def __init__(self, bot):
        super().__init__(bot)
        self.loop = self.bot.loop
        self.waiting_in_queue = DefaultDict(lambda: [])
        self.players_in_queue = []
        self.banned_players = []
        self.categories = DefaultDict(lambda: {})
        self.category_locks = DefaultDict(lambda: Lock())
        self.move_to_games_locks = DefaultDict(lambda: Lock())
        self.max_category_uses = 50
        self.active_games = {}
        self.in_game = {}

    async def get_category(self, guild_id: str):
        lock = self.category_locks[guild_id]
        async with lock:
            guild_categories = self.categories[guild_id]
            for category_id, category_uses in guild_categories.items():
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
        self.waiting_in_queue[guild_id].append({
            "id": user_id,
            "match-type": config["matchmaking-types"][channel_id]["name"],
            "matchmaking-channel-id": channel_id,
            "premium": False
        })
        args, kwargs = self.bot.payloads.move_member(guild_id, user_id, waiting_vc)
        await self.bot.workers.request(guild_id, *args, **kwargs)

    @CogType.event("VOICE_STATE_UPDATE")
    async def move_to_games(self, data: dict, shard):
        channel_id = data["channel_id"]
        user_id = data["member"]["user"]["id"]
        guild_id = data["guild_id"]
        config = self.bot.get_config(guild_id)

        if channel_id != config.get("matchmaking-waiting-vc", None):
            return

        async with self.move_to_games_locks[guild_id]:
            if user_id in self.players_in_queue:
                return
            self.players_in_queue.append(user_id)
            game_counts = {}
            game_players = {}
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
                    self.active_games[game_vc] = 0
                    for to_be_moved in game_players[match_type]:
                        to_be_moved_id = to_be_moved["id"]
                        self.waiting_in_queue[guild_id].remove(to_be_moved)
                        args, kwargs = self.bot.payloads.move_member(guild_id, to_be_moved_id, game_vc)
                        await self.bot.workers.request(guild_id, *args, **kwargs)
                        self.players_in_queue.remove(user_id)
                    return

    @CogType.event("VOICE_STATE_UPDATE")
    async def remove_on_disconnect_in_queue(self, data, shard):
        channel_id = data["channel_id"]
        user_id = data["member"]["user"]["id"]
        guild_id = data["guild_id"]

        if channel_id is not None:
            return

        async with self.move_to_games_locks[guild_id]:
            waiting_in_queue = self.waiting_in_queue[guild_id].copy()
            for member in waiting_in_queue:
                if member["id"] == user_id:
                    self.waiting_in_queue[guild_id].remove(member)
                    break

    @CogType.event("VOICE_STATE_UPDATE")
    async def purge_old_games(self, data, shard):
        channel_id = data["channel_id"]
        user_id = data["member"]["user"]["id"]
        guild_id = data["guild_id"]

        if channel_id in self.active_games.keys() and user_id not in self.in_game:
            # User joins a game
            self.in_game[user_id] = channel_id
            return
        if user_id in self.in_game.keys() and channel_id is None:
            # User left a game
            channel_id = self.in_game[user_id]
            del self.in_game[user_id]
            self.active_games[channel_id] -= 1
            if self.active_games[channel_id] < 0:  # In case there is a collision
                del self.active_games[channel_id]
                r = Route("DELETE", "/channels/{channel}", channel=channel_id, guild_id=guild_id)
                resp = await self.bot.http.request(r)
                resp_data = await resp.json()
                parent_id = resp_data["parent_id"]
                self.categories[guild_id][parent_id] -= 1


def setup(bot: ExtendedClient):
    return Queue(bot)
