"""
Created by Epic at 10/24/20
"""
from custom_types import CogType
from custom_types import ExtendedClient


class About(CogType):
    def __init__(self, bot: ExtendedClient):
        self.bot = bot

        super().__init__(bot)

    @CogType.command("about")
    async def about(self, ctx):
        await ctx.send(content="AQue is a bot to manage your among us matchmaking servers easily!\n"
                               "Join https://discord.gg/tyqNFuU if you want it for yourself!")


def setup(bot: ExtendedClient):
    About(bot)
