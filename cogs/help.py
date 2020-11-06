"""
Created by Epic at 11/6/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext

from os import environ as env


class Help(CogType):
    @CogType.command("help")
    async def about(self, ctx: CommandContext):
        await ctx.send("\n".join([i[0] for i in self.bot.cog_manager.commands]))


def setup(bot: ExtendedClient):
    Help(bot)
