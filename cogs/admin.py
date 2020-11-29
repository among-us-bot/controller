"""
Created by Epic at 10/30/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext
from checks import developer_check


class Admin(CogType):
    @CogType.command(
        command_syntax="admin set-config-role (\\d+)",
        name="set-config-role",
        usage="admin set-config-role <role-id>",
        description="Sets the role used for staff permissions in the current server")
    @developer_check
    async def set_config_role(self, ctx: CommandContext):
        config_role_id = ctx.args[0]

        self.bot.update_config(ctx.message.guild_id, {"config-role": config_role_id})
        await ctx.send("Updated!")

    @CogType.command(
        command_syntax="admin debug (\\w*)",
        name="debug",
        usage="admin debug <attribute.subattribute...>",
        description="Gets a variable. Useful for debugging errors")
    @developer_check
    async def debug(self, ctx: CommandContext):
        current_attr = self.bot
        try:
            for attr_name in ctx.args[0].split("."):
                current_attr = getattr(current_attr, attr_name)
            await ctx.send(str(current_attr))
        except AttributeError:
            await ctx.send("Not found.")

    @CogType.command(
        command_syntax="admin whitelist add (\\d+)",
        name="whitelist-add",
        usage="admin whitelist add <guild-id>",
        description="Adds a guild to the invite whitelist allowing it to be invited")
    @developer_check
    async def add_to_whitelist(self, ctx: CommandContext):
        guild_id = ctx.args[0]
        if self.bot.whitelisted_table.find_one({"_id": guild_id}) is not None:
            prefix = self.bot.get_prefix(ctx.message.guild_id)
            return await ctx.send(f"Guild is already on the whitelist."
                                  f" Change whitelist status using `{prefix}admin whitelist clear_status <guild_id>`")
        self.bot.whitelisted_table.insert_one({"_id": guild_id, "invited": False})
        await ctx.send("Added to whitelist!")

    @CogType.command(
        command_syntax="admin whitelist clear-status (\\d+)",
        name="whitelist-clear-status",
        usage="admin whitelist clear-status <guild-id>",
        description="Clears a guilds invited status allowing it to be invited again")
    @developer_check
    async def clear_whitelist_status(self, ctx: CommandContext):
        guild_id = ctx.args[0]
        self.bot.whitelisted_table.update_one({"_id": guild_id}, {"$set": {"invited": False}})
        await ctx.send("Cleared their invited status.")

    @CogType.command(
        command_syntax="admin whitelist remove (\\d+)",
        name="whitelist-remove",
        usage="admin whitelist remove <guild-id>",
        description="Removes a guild from the invite whitelist.")
    @developer_check
    async def remove_from_whitelist(self, ctx: CommandContext):
        guild_id = ctx.args[0]
        self.bot.whitelisted_table.delete_one({"_id": guild_id})
        await ctx.send("Removed their whitelist access")

    @CogType.command(
        command_syntax="admin whitelist status (\\d+)",
        name="whitelist-status",
        usage="admin whitelist status <guild-id>",
        description="Checks the status of a guild to check if they are whitelisted/already invited/not whitelisted")
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

    @CogType.command(
        command_syntax="admin set analytics-url (.+)",
        name="set-analytics-url",
        usage="admin set analytics-url <analytics-url>",
        description="Sets the analytics url used for the analytics command")
    @developer_check
    async def set_analytics_url(self, ctx: CommandContext):
        url = ctx.args[0]
        self.bot.update_config(ctx.message.guild_id, {"analytics-url": url})
        await ctx.send("Ok.")


def setup(bot: ExtendedClient):
    return Admin(bot)
