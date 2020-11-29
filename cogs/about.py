"""
Created by Epic at 10/24/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext

from os import environ as env


class About(CogType):
    @CogType.command(
        command_syntax="about",
        name="about",
        usage="about",
        description="Gets basic info about the bot")
    async def about(self, ctx: CommandContext):
        await ctx.send("AQue is a bot to manage your among us matchmaking servers easily!\n"
                       f"Join {env['DISCORD']} if you want it for yourself!")


def setup(bot: ExtendedClient):
    return About(bot)
