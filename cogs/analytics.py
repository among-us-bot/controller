"""
Created by Epic at 11/29/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext


class Analytics(CogType):
    """
    Display analytics about your aque installation
    """

    @CogType.command(
        command_syntax="analytics",
        name="analytics",
        usage="analytics",
        description="Gets the analytics url")
    async def export_analytic(self, ctx: CommandContext):
        await ctx.send(ctx.guild_config.get("analytics-url", "This has not been set up yet."))


def setup(bot: ExtendedClient):
    return Analytics(bot)
