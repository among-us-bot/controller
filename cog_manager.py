"""
Created by Epic at 10/22/20
"""
from .custom_types import ExtendedClient as Client
#from speedcord import Client
from speedcord.ext.typing.context import MessageContext
from importlib import import_module
from logging import getLogger
from re import compile


class CommandContext:
    def __init__(self, message: dict, client):
        self.client = client
        self.message = MessageContext(client, self.message_data)
        self.message_data = message


class CogManager:
    def __init__(self, client: Client):
        self.client = client
        self.logger = getLogger("controller.manager.cog_manager")
        self.commands = []

    def register_cog(self, cog_name):
        module = import_module("." + cog_name, "cogs")
        getattr(module, "setup")(self.client)
        self.logger.debug(f"Added cog '{cog_name}'")

    def register_command(self, command, command_syntax):
        self.commands.append((compile(command_syntax), command))
        self.logger.debug(f"Registered command {command.__name__}")

    def process_message(self, message: dict):
        if message["author"].get("bot", False):
            return
        prefix = await self.client.get_prefix(message.get("guild_id"))
        if not message["content"].startswith(prefix):
            return
        content_without_prefix = message["content"][len(prefix)-1:]
        context = CommandContext(message, self.client)
