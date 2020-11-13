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
            message = ""
            prefix = await self.bot.get_prefix(ctx.message.guild_id)
            message += f"**Use `{prefix}help command` for help on a command**\n"
            permissions = {}
            command_names = []
            for command in self.bot.cog_manager.commands:
                can_run = True
                for check, check_name in command["checks"]:
                    if check_name in permissions.keys():
                        if not permissions[check_name]:
                            can_run = False
                    check_result = check(ctx)
                    permissions[check_name] = check_result
                    if not check_result:
                        can_run = False
                if can_run:
                    command_names.append(command.get("usage") or command.get("name"))
            permissions_header = ""
            for permission_name, permission_value in permissions.items():
                if permission_name.endswith("_check"):
                    permission_name = permission_name[:-6]
                if permission_value:
                    permissions_header += f"`{permission_name}` "
                else:
                    permissions_header += f"~~`{permission_name}`~~"
            message += "__Permissions__\n"
            message += permissions_header + "\n\n"
            message += "__Commands__\n"
            message += "\n".join(command_names)
            await ctx.send(message)
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
