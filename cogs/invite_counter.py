import discord

from invite_manager import InviteManager
from discord.ext import commands


class InviteCounter(commands.Cog):
    def __init__(self, bot):
        self.bot: InviteManager = bot
        
    # Loading guild invites when starting the bot
    @commands.Cog.listener()
    async def on_ready(self):
        # Iterating bot guild and pushing it to the cache
        for guild in self.bot.guilds:
            try:
                self.bot.invites[guild.id] = await guild.invites()
            except Exception as exception:
                print(exception)

            print(self.bot.invites)

    # Adding a guild into the cache if bot joins it
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        self.bot.invites[guild.id] = await guild.invites()

    # Removing a guild from the cache if the bot leaves it, just to make it lighter
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if guild.id in self.bot.invites:
            del self.bot.invites[guild.id]

    # Adding an invite to the cache if created
    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        guild_id = invite.guild.id
        if guild_id in self.bot.invites:
            self.bot.invites[guild_id].append(invite)
        else:
            self.bot.invites[guild_id] = await invite.guild.invites()

    # Removing an invite from the cache if deleted
    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        guild_id = invite.guild.id
        if guild_id in self.bot.invites:
            try:
                self.bot.invites[guild_id].remove(invite)
            except KeyError:
                return

    # Fetching the inviter
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild: discord.Guild = member.guild
        is_bot = member.bot

        if guild.id not in self.bot.invites:
            self.bot.invites[guild.id] = await guild.invites()

        try:
            actual_invites = await guild.invites()
            before_invites = self.bot.invites[guild.id]
        except Exception as exception:
            print(exception)

        if actual_invites and before_invites:
            ...

def setup(bot):
    bot.add_cog(InviteCounter(bot))