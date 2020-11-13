"""
Created by Epic at 10/30/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext
from checks import owner_check


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
