import discord

from invite_manager import InviteManager
from discord.ext import commands


class InviteCounter(commands.Cog):
    def __init__(self, bot):
        self.bot: InviteManager = bot
    
    # This function permits to check which invite from all invites is incremented
    def find_invite(self, before, after):
        for invite in after:
            try:
                if invite.uses > before[invite.id].uses:
                    return invite
            except KeyError as error:
                continue

        return None

    # Loading guild invites when starting the bot
    @commands.Cog.listener()
    async def on_ready(self):
        # Iterating bot guild and pushing it to the cache
        for guild in self.bot.guilds:
            try:
                self.bot.invites[guild.id] = {i.id: i for i in await guild.invites()}
            except Exception as exception:
                print(exception)

    # Adding a guild into the cache if bot joins it
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        self.bot.invites[guild.id] = {i.id: i for i in await guild.invites()}

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
            self.bot.invites[guild_id][invite.id] = invite
        else:
            self.bot.invites[guild_id] = {i.id: i for i in await invite.guild.invites()}

    # Removing an invite from the cache if deleted
    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        guild_id = invite.guild.id
        if guild_id in self.bot.invites:
            try:
                del self.bot.invites[guild_id][invite.id]
            except KeyError:
                return

    # Fetching the inviter
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild: discord.Guild = member.guild

        # If invited is a bot, cancel (Could be deleted)
        if member.bot:
            return

        try:
            before_invites = self.bot.invites[guild.id]
            actual_invites = await guild.invites()
        
        except Exception as exception:
            print(exception)

        if actual_invites and before_invites:
            # Looking for used invite
            invite = self.find_invite(before_invites, actual_invites)
            if invite:
                inviter = invite.inviter
                
                # Updating inviter's document 
                await self.bot.mongo.update_user_data(inviter.id, guild.id, {
                    "$inc": {"invites": 1}
                })

                # Adding invited to database
                await self.bot.mongo.update_user_data(member.id, guild.id, {
                    "$set": {"inviter_id": inviter.id}
                }) 

        # Reupdating invite cache 
        self.bot.invites[guild.id] = {i.id: i for i in actual_invites}

    # Updating documents to remove invite from inviter if invited leaves
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild: discord.Guild = member.guild

        # Canceling if member is a bot (Could be deleted)
        if member.bot:
            return

        member_data = await self.bot.mongo.get_user_data(guild.id, member.id)
        
        # If inviter registered, removing one invite and adding one leave
        if "inviter_id" in member_data:
            await self.bot.mongo.update_user_data(member_data["inviter_id"], guild.id, {
                "$inc": {"invites": -1, "left": 1}
            })

def setup(bot):
    bot.add_cog(InviteCounter(bot))