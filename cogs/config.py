"""
Created by Epic at 10/31/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext

from speedcord.http import Route
from ujson import dumps


def staff_check(func):
    async def inner(_, ctx: CommandContext):
        guild_config = ctx.client.get_config(ctx.message.guild_id)
        if str(guild_config.get("config-role")) in ctx.message.member["roles"]:
            await func(_, ctx)
        else:
            await ctx.send(f"<@{ctx.message.author['id']}>, only staff has access to this.")

    return inner


class Config(CogType):
    @CogType.command("config set matchmaking-category (\\d+)")
    @staff_check
    async def set_matchmaking_category(self, ctx: CommandContext):
        self.bot.update_config(ctx.message.guild_id, {"matchmaking-category": int(ctx.args[0])})
        await ctx.send("Matchmaking category set!")

    @CogType.command("config create matchmaking-type ([A-z,-]+) (\\d+)")
    @staff_check
    async def create_matchmaking_type(self, ctx: CommandContext):
        matchmaking_type = ctx.args[0]
        required_users = int(ctx.args[1])

        config = self.bot.get_config(ctx.message.guild_id)

        matchmaking_types = config.get("matchmaking-types", {})
        if config.get("matchmaking-category", None) is None:
            return await ctx.send("Please set a matchmaking category first")
        if matchmaking_type in [match_type["name"] for match_type in matchmaking_types.values()]:
            return await ctx.send("This matchmaking type already exists!")
        route = Route("POST", "/guilds/{guild_id}/channels", guild_id=ctx.message.guild_id)
        response = await self.bot.http.request(route, json={
            "name": matchmaking_type,
            "parent_id": config["matchmaking-category"],
            "type": 2
        })
        data = await response.json()
        channel_id = data["id"]
        matchmaking_data = {
            "channel_id": channel_id,
            "name": matchmaking_type,
            "required_users": required_users
        }
        matchmaking_types[channel_id] = matchmaking_data
        self.bot.update_config(ctx.message.guild_id, {"matchmaking-types": matchmaking_types})
        await ctx.send("Created a matchmaking category!")

    @CogType.command("config set waiting-vc (\\d+)")
    @staff_check
    async def set_waiting_vc(self, ctx: CommandContext):
        self.bot.update_config(ctx.message.guild_id, {"matchmaking-waiting-vc": ctx.args[0]})
        await ctx.send("Waiting VC updated!")

    @CogType.command("config display")
    @staff_check
    async def get_config(self, ctx: CommandContext):
        config = self.bot.get_config(ctx.message.guild_id)
        await ctx.send(f"```json\n{dumps(config, indent=4)}\n```")


def setup(bot: ExtendedClient):
    Config(bot)
