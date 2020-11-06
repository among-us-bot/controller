"""
Created by Epic at 11/6/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext


class Help(CogType):
    @CogType.command("help( ?\\w)*")
    async def help(self, ctx: CommandContext):
        command_name = ctx.args[0]
        if command_name is None:
            prefix = await self.bot.get_prefix(ctx.message.guild_id)
            header = f"**Use `{prefix}help command` to get info on a command**\n\n"
            command_names = [command_details["name"] for command_details in self.bot.cog_manager.commands]
            await ctx.send(header + "\n".join(command_names))


def setup(bot: ExtendedClient):
    Help(bot)
