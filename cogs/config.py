"""
Created by Epic at 10/31/20
"""
from custom_types import CogType, ExtendedClient


class Config(CogType):
    pass


def setup(bot: ExtendedClient):
    Config(bot)
