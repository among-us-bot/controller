"""
Created by Epic at 9/5/20
"""
from custom_types import ExtendedClient

from os import environ as env
from logging import getLogger, WARNING, DEBUG
from color_format import basicConfig
from pathlib import Path

client = ExtendedClient(default_prefix="/", intents=641)
log = getLogger()
log.setLevel(DEBUG)
basicConfig(log)
#getLogger("speedcord").setLevel(WARNING)

cog_path = Path("cogs/")

for cog_path in cog_path.glob("*.py"):
    cog = str(cog_path)[5:].split(".")[0]
    client.cog_manager.register_cog(cog)

client.token = env["TOKEN"]
client.run()
