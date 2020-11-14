"""
Created by Epic at 10/31/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext
from checks import staff_check

from speedcord.http import Route
from yaml import dump


class Config(CogType):
    @CogType.command("config set matchmaking-category (\\d+)",
                     usage="config set matchmaking-category <matchmaking-category-id>",
                     description="Sets the category for matchmaking types")
    @staff_check
    async def set_matchmaking_category(self, ctx: CommandContext):
        self.bot.update_config(ctx.message.guild_id, {"matchmaking-category": ctx.args[0]})
        await ctx.send("Matchmaking category set!")

    @CogType.command("config create matchmaking-type ([A-z,-]+) (\\d+)",
                     usage="config create matchmaking-type <name> <required-players>",
                     description="Creates a different matchmaking type for the matchmaker")
    @staff_check
    async def create_matchmaking_type(self, ctx: CommandContext):
        matchmaking_type = ctx.args[0]
        required_users = int(ctx.args[1])

        if required_users <= 1:
            return await ctx.send("You need at least 2 players in a lobby.")

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
            "type": 2,
            "user_limit": required_users
        })
        data = await response.json()
        channel_id = data["id"]
        matchmaking_data = {
            "channel_id": channel_id,
            "name": matchmaking_type,
            "required_users": required_users,
        }
        matchmaking_types[channel_id] = matchmaking_data
        self.bot.update_config(ctx.message.guild_id, {"matchmaking-types": matchmaking_types})
        await ctx.send("Created a matchmaking category!")

    @CogType.command(
        command_syntax="config delete matchmaking-type ([A-z,-]+)",
        usage="config delete matchmaking-type <name>",
        description="Deletes a matchmaking portal",
        name="delete-matchmaking-type"
    )
    @staff_check
    async def delete_matchmaking_type(self, ctx: CommandContext):
        matchmaking_type = ctx.args[0]
        config = self.bot.get_config(ctx.message.guild_id)

        matchmaking_types = config.get("matchmaking-types", {})
        if matchmaking_type not in [match_type["name"] for match_type in matchmaking_types.values()]:
            return await ctx.send("This matchmaking type doesn't exist!")
        del matchmaking_types[matchmaking_type]
        config["matchmaking-types"] = matchmaking_types
        self.bot.update_config(ctx.message.guild_id, config)
        await ctx.send("Done! Delete the channel to finish.")

    @CogType.command("config set waiting-vc (\\d+)", usage="config set waiting-vc <vc-id>",
                     description="Sets the channel being used for people waiting for a match")
    @staff_check
    async def set_waiting_vc(self, ctx: CommandContext):
        self.bot.update_config(ctx.message.guild_id, {"matchmaking-waiting-vc": ctx.args[0]})
        await ctx.send("Waiting VC updated!")

    @CogType.command("config display", usage="config display", description="Shows the config in YAML format")
    @staff_check
    async def get_config(self, ctx: CommandContext):
        config = self.bot.get_config(ctx.message.guild_id)
        await ctx.send(f"```yaml\n{dump(config)}\n```")


def setup(bot: ExtendedClient):
    Config(bot)
