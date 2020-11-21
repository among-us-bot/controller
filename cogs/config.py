"""
Created by Epic at 10/31/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext
from checks import staff_check

from speedcord.http import Route
from yaml import dump


class Config(CogType):
    @CogType.command(
        command_syntax="config set matchmaking-category (\\d+)",
        name="set-matchmaking-category",
        usage="config set matchmaking-category <matchmaking-category-id>",
        description="Sets the category for matchmaking types")
    @staff_check
    async def set_matchmaking_category(self, ctx: CommandContext):
        self.bot.update_config(ctx.message.guild_id, {"matchmaking-category": ctx.args[0]})
        await ctx.send("Matchmaking category set!")

    @CogType.command(
        command_syntax="config create matchmaking-type ([A-z,-]+) (\\d+)",
        name="create-matchmaking-type",
        usage="config create matchmaking-type <name> <required-players>",
        description="Creates a different matchmaking type for the matchmaker"
    )
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
        name="delete-matchmaking-type",
        usage="config delete matchmaking-type <name>",
        description="Deletes a matchmaking portal",
    )
    @staff_check
    async def delete_matchmaking_type(self, ctx: CommandContext):
        matchmaking_type = ctx.args[0]
        config = self.bot.get_config(ctx.message.guild_id)

        matchmaking_types = config.get("matchmaking-types", {})
        if matchmaking_type not in [match_type["name"] for match_type in matchmaking_types.values()]:
            return await ctx.send("This matchmaking type doesn't exist!")
        for match_id, match_type in matchmaking_types.items():
            if match_type["name"] == matchmaking_type:
                del matchmaking_types[match_id]
                config["matchmaking-types"] = matchmaking_types
                self.bot.update_config(ctx.message.guild_id, config)
                await ctx.send("Done! Delete the channel to finish.")
                return

    @CogType.command(
        command_syntax="config set waiting-vc (\\d+)",
        name="set-waiting-vc",
        usage="config set waiting-vc <vc-id>",
        description="Sets the channel being used for people waiting for a match"
    )
    @staff_check
    async def set_waiting_vc(self, ctx: CommandContext):
        self.bot.update_config(ctx.message.guild_id, {"matchmaking-waiting-vc": ctx.args[0]})
        await ctx.send("Waiting VC updated!")

    @CogType.command(
        command_syntax="config display",
        usage="config display",
        description="Shows the config in YAML format"
    )
    @staff_check
    async def get_config(self, ctx: CommandContext):
        config = self.bot.get_config(ctx.message.guild_id)
        await ctx.send(f"```yaml\n{dump(config)}\n```")

    @CogType.command(
        command_syntax="config set prefix (.*)",
        name="set-prefix",
        usage="config set prefix <prefix>",
        description="Set the bot prefix"
    )
    @staff_check
    async def set_prefix(self, ctx: CommandContext):
        self.bot.update_config(ctx.message.guild_id, {"prefix": ctx.args[0]})
        await ctx.send("Updated!")


def setup(bot: ExtendedClient):
    return Config(bot)
