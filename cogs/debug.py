"""
Created by Epic at 10/30/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext

from logging import getLogger


class Debug(CogType):
    def __init__(self, bot: ExtendedClient):
        self.bot = bot
        self.logger = getLogger("commands.about")
        self.worker_perms = 285215760

        super().__init__(bot)

    @CogType.command("debug")
    async def debug(self, ctx: CommandContext):
        debug_info = await self.get_debug_info(ctx)
        await ctx.send(embed={"title": "AQue debug info", "description": debug_info, "color": 0x00FFFF})

    async def get_debug_info(self, ctx: CommandContext):
        output = ""
        output += f"Guild workers: {self.bot.workers.worker_counts[ctx.message.guild_id]}/" \
                  f"{len(self.bot.workers.workers)}\n"
        for worker in self.bot.workers.workers:

            output += f"{worker.worker_name} [(Invite)](https://discord.com/api/oauth2/authorize?" \
                      f"client_id={worker.user_id}&" \
                      f"permissions={self.worker_perms}&" \
                      f"scope=bot)\n"
        return output


def setup(bot: ExtendedClient):
    Debug(bot)
