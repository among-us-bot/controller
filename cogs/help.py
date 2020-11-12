"""
Created by Epic at 11/6/20
"""
from custom_types import CogType, ExtendedClient
from cog_manager import CommandContext


class Help(CogType):
    @CogType.command("help ?(\\w*)")
    async def help(self, ctx: CommandContext):
        command_name = ctx.args[0]
        if command_name is None or command_name.strip() == "":
            prefix = await self.bot.get_prefix(ctx.message.guild_id)
            header = f"**Use `{prefix}help command` for help on a command**\n__Commands:__\n"
            command_names = [command_details.get("usage") or command_details.get("name") for command_details in
                             self.bot.cog_manager.commands]
            await ctx.send(header + "\n".join(command_names))
        elif command_name in [command["name"] for command in self.bot.cog_manager.commands]:
            command = {}
            for command in self.bot.cog_manager.commands:
                if command["name"] == command_name:
                    break
            await ctx.send(f"**Usage:** {command['usage']}\n"
                           f"**Description**: {command['description']}")
        else:
            await ctx.send("Not found!")


def setup(bot: ExtendedClient):
    Help(bot)
