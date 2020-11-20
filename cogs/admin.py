"""
Created by Epic at 10/30/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext
from checks import developer_check


class Admin(CogType):
    @CogType.command("admin set-config-role (\\d+)", usage="admin set-config-role <role-id>",
                     description="Set the permission role for a guild")
    @developer_check
    async def set_config_role(self, ctx: CommandContext):
        config_role_id = ctx.args[0]

        self.bot.update_config(ctx.message.guild_id, {"config-role": config_role_id})
        await ctx.send("Updated!")

    @CogType.command("admin debug (\\w*)", usage="admin debug <attribute.subattr>")
    @developer_check
    async def debug(self, ctx: CommandContext):
        current_attr = self.bot
        try:
            for attr_name in ctx.args[0].split("."):
                current_attr = getattr(current_attr, attr_name)
            await ctx.send(str(current_attr))
        except AttributeError:
            await ctx.send("Not found.")

    @CogType.command("admin whitelist add (\\d+)", usage="admin whitelist add <guild_id>",
                     description="Adds a guild to the whitelist allowing it to be invited")
    @developer_check
    async def add_to_whitelist(self, ctx: CommandContext):
        guild_id = ctx.args[0]
        if self.bot.whitelisted_table.find_one({"_id": guild_id}) is not None:
            prefix = self.bot.get_prefix(ctx.message.guild_id)
            return await ctx.send(f"Guild is already on the whitelist."
                                  f" Change whitelist status using `{prefix}admin whitelist clear_status <guild_id>`")
        self.bot.whitelisted_table.insert_one({"_id": guild_id, "invited": False})
        await ctx.send("Added to whitelist!")

    @CogType.command("admin whitelist clear_status (\\d+)", usage="admin whitelist clear_status <guild_id>")
    @developer_check
    async def clear_whitelist_status(self, ctx: CommandContext):
        guild_id = ctx.args[0]
        self.bot.whitelisted_table.update_one({"_id": guild_id}, {"$set": {"invited": False}})
        await ctx.send("Cleared their invited status.")

    @CogType.command("admin whitelist remove (\\d+)", usage="admin whitelist remove <guild_id>")
    @developer_check
    async def remove_from_whitelist(self, ctx: CommandContext):
        guild_id = ctx.args[0]
        self.bot.whitelisted_table.delete_one({"_id": guild_id})
        await ctx.send("Removed their whitelist access")

    @CogType.command("admin whitelist status (\\d+)", usage="admin whitelist status <guild_id>")
    @developer_check
    async def get_whitelist_status(self, ctx: CommandContext):
        guild_id = ctx.args[0]
        whitelist_status = self.bot.whitelisted_table.find_one({"_id": guild_id})
        whitelisted = True
        invited = False
        if whitelist_status is None:
            whitelisted = False
        elif whitelist_status["invited"]:
            invited = True
        await ctx.send(f"**Whitelist status**\nWhitelisted: {whitelisted}\nInvited: {invited}")


def setup(bot: ExtendedClient):
    return Admin(bot)
