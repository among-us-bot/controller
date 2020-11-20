"""
Created by Epic at 11/20/20
"""
from custom_types import CogType, ExtendedClient
from collections import defaultdict


class Recovery(CogType):
    """
    Recover after a reboot
    """
    @CogType.event("GUILD_CREATE")
    async def recover_guild(self, data: dict, shard):
        categories = []
        channels = []
        category_counts = defaultdict(lambda: 0)

        # Link categories and voice channels
        for channel in data["channels"]:
            if channel["type"] == 4:  # Categories
                if channel["name"] == "aque-lobby":
                    categories.append(channel["id"])
            elif channel["type"] == 2:
                if "parent_id" not in channel.keys():
                    return
                channels.append(channel["parent_id"])
        # Count lobbies
        for parent_id in channels:
            if parent_id in categories:
                category_counts[parent_id] += 1
        # Count categories with no channels
        for category_id in categories:
            if category_id not in category_counts.keys():
                category_counts[category_id] = 0

        # Save
        cog = self.bot.cog_manager.cogs["queue"]
        for category_id, lobby_count in category_counts.items():
            cog.categories[data["id"]][category_id] = lobby_count
        self.logger.debug(cog.categories)
        self.logger.debug(f"Recovered guild {data['name']} with {len(category_counts.keys())} categories")






def setup(bot: ExtendedClient):
    return Recovery(bot)
