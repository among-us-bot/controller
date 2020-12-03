"""
Created by Epic at 9/5/20
"""
from custom_types import ExtendedClient

from os import environ as env
from logging import getLogger, DEBUG, WARNING, ERROR
from color_format import basicConfig
from pathlib import Path
from os import environ as env
from sentry_sdk import init as init_sentry
from sentry_sdk.integrations.logging import LoggingIntegration

client = ExtendedClient(default_prefix="/", intents=641)
log = getLogger()
log.setLevel(DEBUG)
basicConfig(log)
if bool(env["SPEEDCORD_MUTE_LOGGING"]):
    getLogger("speedcord").setLevel(WARNING)

cog_path = Path("cogs/")

for cog_path in cog_path.glob("*.py"):
    cog = str(cog_path)[5:].split(".")[0]
    client.cog_manager.register_cog(cog)

logging_integration = LoggingIntegration(level=ERROR)
init_sentry(env["SENTRY_DSN"], integrations=[logging_integration])

client.token = env["TOKEN"]
client.run()
