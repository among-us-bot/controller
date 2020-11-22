"""
Created by Epic at 10/22/20
"""
from checks import CheckError

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .custom_types import ExtendedClient as Client
else:
    from speedcord import Client
from speedcord.http import Route
from speedcord.ext.typing.context import MessageContext
from importlib import import_module
from logging import getLogger
from re import compile, Pattern


class CommandContext:
    def __init__(self, message: dict, client: Client, args, guild_config: dict):
        self.client = client
        self.message_data = message
        self.message = MessageContext(client, self.message_data)
        self.args = args
        self.guild_config = guild_config

    async def request(self, *args, **kwargs):
        return await self.client.workers.request(self.message.guild_id, *args, **kwargs)

    async def send(self, content=None, **kwargs):
        route = Route("POST", "/channels/{channel_id}/messages", channel_id=self.message.channel_id,
                      guild_id=self.message.guild_id)
        kwargs["content"] = content
        return await self.request(route, json=kwargs)

    async def reply(self, content=None, **kwargs):
        kwargs["content"] = content
        kwargs["message_reference"] = {
            "message_id": self.message.id
        }


class CogManager:
    def __init__(self, client: Client):
        self.client = client
        self.logger = getLogger("controller.manager.cog_manager")
        self.commands = []
        self.cogs = {}
        self.client.event_dispatcher.register("MESSAGE_CREATE", self.process_message)

    def register_cog(self, cog_name):
        module = import_module("." + cog_name, "cogs")
        cog = getattr(module, "setup")(self.client)
        self.cogs[cog_name] = cog
        self.logger.debug(f"Added cog '{cog_name}'")

    def register_command(self, function, syntax, *, usage=None, description=None, name=None, checks=None):
        if checks is None:
            checks = []
        command_details = {
            "func": function,
            "syntax": compile(syntax),
            "usage": usage,
            "description": description,
            "name": name or function.__name__,
            "checks": checks
        }
        self.commands.append(command_details)
        self.logger.debug(f"Registered command {command_details['name']}")

    async def process_message(self, message: dict, shard):
        if message["author"].get("bot", False):
            return
        guild_config = self.client.get_config(message.get("guild_id"))
        prefix = guild_config.get("prefix", self.client.default_prefix)
        if not message["content"].startswith(prefix):
            return
        content_without_prefix = message["content"][len(prefix):]

        command_syntax: Pattern
        self.logger.debug(content_without_prefix)
        for command_details in self.commands:
            match = command_details["syntax"].fullmatch(content_without_prefix)
            if match is None:
                continue
            context = CommandContext(message, self.client, match.groups(), guild_config)

            # Verify checks
            for check, check_name in command_details["checks"]:
                check_result = check(context)
                if not check_result:
                    await context.reply(f"<@{context.message.author['id']}>, you can't run this command! "
                                        f"Check failed: `{check_name.upper()}`.")
                    return

            await command_details["func"](context)
            self.logger.debug("Processing command")
            return
        if guild_config.get("unknown-command-messages", True):
            context = CommandContext(message, self.client, [], guild_config)
            await context.reply(f"<@{context.message.author['id']}>, unknown command!")
