"""
Created by Epic at 9/5/20
"""
from custom_types import ExtendedClient

from os import environ as env
from logging import getLogger, WARNING, DEBUG
from color_format import basicConfig

client = ExtendedClient(default_prefix="/", intents=641)
log = getLogger()
log.setLevel(DEBUG)
basicConfig(log)
#getLogger("speedcord").setLevel(WARNING)

client.cog_manager.register_cog("about")
client.cog_manager.register_cog("debug")
client.cog_manager.register_cog("admin")

client.token = env["TOKEN"]
client.run()
