from motor import motor_asyncio as motor
from discord.ext import commands

class Mongo(commands.Cog):

    USER_DATA = {
        "user_id": None,
        "guild_id": None,
        "inviter_id": None,
        "invites": 0,
        "left": 0
    }

    def __init__(self, bot):
        self.bot = bot
        self.db = motor.AsyncIOMotorClient()["invite_manager"]

    async def get_user_data(self, user_id, guild_id):
        data = await self.db["invites"].find_one(
            {"user_id": user_id, "guild_id": guild_id})

        if not data:
            data = self.USER_DATA.copy()
            data["user_id"] = user_id
            data["guild_id"] = guild_id

        return data

    async def update_user_data(self, user_id, guild_id, query):
        await self.db["invites"].update_one(
            {"user_id": user_id, "guild_id": guild_id}, query, upsert=True)


def setup(bot):
    bot.add_cog(Mongo(bot))