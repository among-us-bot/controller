"""
Created by Epic at 11/13/20
"""
from functools import wraps
from cog_manager import CommandContext
from os import environ as env

owner_ids = env["OWNER_IDS"].split(" ")


def owner_check(func):
    @wraps(func)
    async def inner(_, ctx: CommandContext):
        if ctx.message.author["id"] in owner_ids:
            await func(_, ctx)
        else:
            await ctx.send(f"<@{ctx.message.author['id']}>, you are boring me.")

    return inner


def staff_check(func):
    @wraps(func)
    async def inner(_, ctx: CommandContext):
        guild_config = ctx.client.get_config(ctx.message.guild_id)
        if str(guild_config.get("config-role")) in ctx.message.member["roles"]:
            await func(_, ctx)
        else:
            await ctx.send(f"<@{ctx.message.author['id']}>, only staff has access to this.")

    return inner
