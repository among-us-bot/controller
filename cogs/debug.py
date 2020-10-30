"""
Created by Epic at 10/30/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext


class Debug(CogType):
    @CogType.command("debug")
    async def debug(self, ctx: CommandContext):
        debug_info = await self.get_debug_info(ctx)
        await ctx.send(embed={"title": "AQue debug info", "description": debug_info, "color": 0x00FFFF})

    async def get_debug_info(self, ctx: CommandContext):
        output = ""
        output += f"Guild workers: {self.bot.workers.worker_counts[ctx.message.guild_id]}/" \
                  f"{len(self.bot.workers.workers)}\n"
        worker_count = self.bot.workers.worker_counts[ctx.message.guild_id] - 1
        for worker_id, worker in enumerate(self.bot.workers.workers):
            output += f"{'~~' if worker_id > worker_count else ''}" \
                      f"{worker.worker_name} [(Invite)](https://discord.com/api/oauth2/authorize?" \
                      f"client_id={worker.user_id}&" \
                      f"scope=bot)" \
                      f"{'~~' if worker_id > worker_count else ''}\n"
        return output


def setup(bot: ExtendedClient):
    Debug(bot)
