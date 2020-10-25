"""
Created by Epic at 10/22/20
"""
from speedcord import Client
from importlib import import_module
from logging import getLogger
from re import compile


class CogManager:
    def __init__(self, bot: Client):
        self.bot = bot
        self.logger = getLogger("controller.manager.cog_manager")
        self.commands = []

    def register_cog(self, cog_name):
        module = import_module("." + cog_name, "cogs")
        getattr(module, "setup")(self.bot)
        self.logger.debug(f"Added cog '{cog_name}'")

    def register_command(self, command, command_syntax):
        self.commands.append((compile(command_syntax), command))
        self.logger.debug(f"Registered command {command.__name__}")

