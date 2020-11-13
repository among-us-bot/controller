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
    @CogType.command("admin set-config-role (\\d+)", usage="admin set-config-role <role-id>",
                     description="Set the permission role for a guild")
    @owner_check
    async def set_config_role(self, ctx: CommandContext):
        config_role_id = ctx.args[0]

        self.bot.update_config(ctx.message.guild_id, {"config-role": config_role_id})
        await ctx.send("Updated!")

    @CogType.command("admin debug (\\w*)", usage="admin debug <attribute.subattr>")
    @owner_check
    async def debug(self, ctx: CommandContext):
        current_attr = self.bot
        try:
            for attr_name in ctx.args[0].split("."):
                current_attr = getattr(current_attr, attr_name)
            await ctx.send(str(current_attr))
        except AttributeError:
            await ctx.send("Not found.")


def setup(bot: ExtendedClient):
    Admin(bot)
