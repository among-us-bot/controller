"""
Created by Epic at 10/24/20
"""
from custom_types import CogType
from custom_types import ExtendedClient

from logging import getLogger


class About(CogType):
    def __init__(self, bot: ExtendedClient):
        self.bot = bot
        self.logger = getLogger("commands.about")

        super().__init__(bot)

    @CogType.command("about")
    async def about(self, ctx):
        r = await ctx.send("AQue is a bot to manage your among us matchmaking servers easily!\n"
                           "Join https://discord.gg/tyqNFuU if you want it for yourself!")
        self.logger.debug(await r.text())


def setup(bot: ExtendedClient):
    About(bot)
