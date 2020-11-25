"""
Created by Epic at 10/22/20
"""
from cog_manager import CogManager
from workers import WorkerUtil
from payloads import Payloads

from speedcord.client import Client
from pymongo import MongoClient
from os import environ as env
from logging import getLogger


class ExtendedClient(Client):
    def __init__(self, default_prefix, intents: int):
        super().__init__(intents)
        self.default_prefix = default_prefix
        self.cog_manager = CogManager(self)
        self.workers = WorkerUtil(self)
        self.payloads = Payloads()
        self.config_cache = {}

        self.mongo_client = MongoClient(env["DATABASE_HOST"])
        self.database = self.mongo_client[env["DATABASE_DB"]]
        self.config_table = self.database["guild_config"]
        self.whitelisted_table = self.database["whitelisted"]

        self.loop.create_task(self.workers.start())

    async def get_prefix(self, guild_id: str):
        config = self.get_config(guild_id)
        return config.get("prefix") or self.default_prefix

    def get_config(self, guild_id: str):
        config = self.config_cache.get(guild_id)
        if config is None:
            # Fetch the config
            config = self.config_table.find_one({"_id": guild_id}) or {}
            self.config_cache[guild_id] = config
        return config

    def update_config(self, guild_id: str, changes: dict):
        if guild_id in self.config_cache.keys():
            del self.config_cache[guild_id]
        if self.config_table.find_one({"_id": guild_id}) is None:
            changes["_id"] = guild_id
            self.config_table.insert_one(changes)
            return
        self.config_table.update_one({"_id": guild_id}, {"$set": changes})


class CogType:
    def __init__(self, bot: ExtendedClient):
        self.bot = bot
        self.logger = getLogger(self.__module__)
        for attr_name in dir(self):
            func = getattr(self, attr_name)
            command_syntax = getattr(func, "__command_syntax__", None)
            if command_syntax is not None:
                checks = getattr(func, "__command_checks__", [])
                self.bot.cog_manager.register_command(func, command_syntax, **getattr(func, "__command_attrs__", {}),
                                                      checks=checks)

            event_name = getattr(func, "__event_name__", None)
            if event_name is not None:
                self.bot.event_dispatcher.register(event_name, func)

    @staticmethod
    def command(command_syntax=None, **kwargs):
        def inner(func):
            nonlocal command_syntax
            if command_syntax is None:
                command_syntax = func.__name__
            func.__command_syntax__ = command_syntax
            func.__command_attrs__ = kwargs
            return func

        return inner

    @staticmethod
    def event(event_name=None):
        def inner(func):
            nonlocal event_name
            if event_name is None:
                event_name = func.__name__[2:]
            func.__event_name__ = event_name
            return func

        return inner
