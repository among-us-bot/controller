"""
Created by Epic at 10/31/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext


def staff_check(func):
    async def inner(_, ctx: CommandContext):
        guild_config = ctx.client.get_config(ctx.message.guild_id)
        if str(guild_config.get("config-role")) in ctx.message.member["roles"]:
            await func(ctx)
        else:
            await ctx.send(f"<@{ctx.message.author['id']}>, only staff has access to this.")

    return inner


class Config(CogType):
    @CogType.command("config set worker-count (\\d+)")
    @staff_check
    async def set_worker_count(self, ctx: CommandContext):
        self.bot.update_config(ctx.message.guild_id, {"worker-count": int(ctx.args[0])})
        await ctx.send("Updated")

    @CogType.command("config set matchmaking-category <#(\\d+)>")
    @staff_check
    async def set_matchmaking_category(self, ctx: CommandContext):
        self.bot.update_config(ctx.message.guild_id, {"matchmaking-category": int(ctx.args[0])})
        await ctx.send("Matchmaking category set!")


def setup(bot: ExtendedClient):
    Config(bot)
