"""
Created by Epic at 10/22/20
"""
from manager import CogManager

from speedcord.client import Client


class ExtendedClient(Client):
    def __init__(self, prefix, intents: int):
        self.prefix = prefix
        self.cog_manager = CogManager(self)
        super().__init__(intents)
