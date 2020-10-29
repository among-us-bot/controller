"""
Created by Epic at 9/5/20
"""
from custom_types import ExtendedClient

from os import environ as env
from logging import getLogger, WARNING
from color_format import basicConfig

client = ExtendedClient(default_prefix="/", intents=512)
basicConfig(getLogger())
getLogger("speedcord").setLevel(WARNING)
client.cog_manager.register_cog("about")

client.token = env["TOKEN"]
client.run()
