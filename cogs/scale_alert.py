"""
Created by Epic at 10/31/20
"""
from custom_types import CogType, ExtendedClient

from asyncio import sleep


class About(CogType):
    async def process_scaled_bot(self, guild_id: str):
        guild_config = self.bot.get_config(guild_id)
        if guild_config.get("alerts-channel") is None:
            return
        prefix = guild_config.get('prefix', self.bot.default_prefix)
        message = f"**Warning** @everyone\n" \
                  f"Please check {prefix}debug to invite the missing bots or "
        args, kwargs = self.bot.payloads.send_message_in_channel(guild_config["alerts-channel"], guild_id,
                                                                 content=message,
                                                                 allowed_mentions=[])
        await self.bot.http.request(*args, **kwargs)

    @CogType.event("READY")
    async def handle_scale_alerts(self, data, shard):
        await sleep(10)  # Good delay for all workers to connect
        for guild_id, worker_count in self.bot.workers.worker_counts.items():
            has_scale_changed = self.bot.has_scale_changed(guild_id, worker_count)
            if has_scale_changed:
                await self.process_scaled_bot(guild_id)


def setup(bot: ExtendedClient):
    About(bot)
