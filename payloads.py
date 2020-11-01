"""
Created by Epic at 10/30/20
"""
from speedcord.http import Route


class Payloads:
    def __init__(self):
        pass

    def move_member(self, guild_id: int, user_id: int, channel_id: int):
        r = Route("PATCH", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id)
        return [r], {"json": {"channel_id": channel_id}}

    def send_message_in_channel(self, channel_id: str, guild_id: str, **kwargs):
        r = Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id,
                  guild_id=guild_id)
        return [r], {"json": kwargs}
