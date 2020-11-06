"""
Created by Epic at 10/30/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext

from os import environ as env
from functools import wraps

owner_ids = env["OWNER_IDS"].split(" ")


def owner_check(func):
    @wraps(func)
    async def inner(_, ctx: CommandContext):
        if ctx.message.author["id"] in owner_ids:
            await func(_, ctx)
        else:
            await ctx.send(f"<@{ctx.message.author['id']}>, you are boring me.")

    return inner


class Admin(CogType):
    @CogType.command("admin force-workers (\\d+) (\\d+)")
    @owner_check
    async def force_workers(self, ctx: CommandContext):
        guild_id = str(ctx.args[0])
        worker_count = int(ctx.args[1])
        self.bot.workers.worker_counts[guild_id] = worker_count

        await ctx.send("Updated worker count!")

    @CogType.command("admin set-config-role (\\d+)")
    @owner_check
    async def set_config_role(self, ctx: CommandContext):
        config_role_id = ctx.args[0]
        
        self.bot.update_config(ctx.message.guild_id, {"config-role": config_role_id})
        await ctx.send("Updated!")


def setup(bot: ExtendedClient):
    Admin(bot)
