"""
Created by Epic at 10/22/20
"""
#from .custom_types import ExtendedClient as Client
from speedcord import Client
from speedcord.ext.typing.context import MessageContext
from importlib import import_module
from logging import getLogger
from re import compile, Pattern


class CommandContext:
    def __init__(self, message: dict, client, args):
        self.client = client
        self.message_data = message
        self.message = MessageContext(client, self.message_data)
        self.args = args

    async def send(self, **kwargs):
        await self.message.send(**kwargs)


class CogManager:
    def __init__(self, client: Client):
        self.client = client
        self.logger = getLogger("controller.manager.cog_manager")
        self.commands = []
        self.client.event_dispatcher.register("MESSAGE_CREATE", self.process_message)

    def register_cog(self, cog_name):
        module = import_module("." + cog_name, "cogs")
        getattr(module, "setup")(self.client)
        self.logger.debug(f"Added cog '{cog_name}'")

    def register_command(self, command, command_syntax):
        self.commands.append((compile(command_syntax), command))
        self.logger.debug(f"Registered command {command.__name__}")

    async def process_message(self, message: dict, shard):
        if message["author"].get("bot", False):
            return
        prefix = await self.client.get_prefix(message.get("guild_id"))
        if not message["content"].startswith(prefix):
            return
        content_without_prefix = message["content"][len(prefix):]

        command_syntax: Pattern
        for command_syntax, command in self.commands:
            match = command_syntax.fullmatch(content_without_prefix)
            if match is None:
                continue
            context = CommandContext(message, self.client, match.groups())
            await command(context)
            return
        self.logger.debug("Unknown command!")

