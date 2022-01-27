from random import randint
import discord

from math import ceil
from discord.ext import commands
from invite_manager import InviteManager


DEV_GUILD_ID = [928043393798529045]


async def format_invites(data):
    invites = data["invites"] if "invites" in data else 0
    left = data["left"] if "left" in data else 0
    total = invites + left
    return invites, left, total


async def create_page(data, page, color):
    sharded_data = data[page * 10 : page * 10 + 10]
    message = []
    for user in sharded_data:
        invites, left, total = await format_invites(user)
        message.append(f"**`{data.index(user) + 1}.`** <@{user['user_id']}> **~ {invites}** invite{'s' if invites > 1 else ''} "\
                       f"(**{total}** total, **{left}** left)\n")
    
    return discord.Embed(title="Invites Leaderboard", color=color, description="".join(message))


class InviteLeaderBoard(discord.ui.View):
    def __init__(self, bot, data):
        super().__init__()
        
        self.bot = bot
        self.data = data
        self.page = 0
        self.color = self.bot.color

    @discord.ui.button(label="Top", style=discord.ButtonStyle.blurple)
    async def _top(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page = 0
        self._page.label = f"Page | {self.page + 1}"
        self._previous.disabled = True

        if self._next.disabled:
            self._next.disabled = False

        embed: discord.Embed = await create_page(self.data, self.page, self.color)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.red, disabled=True)
    async def _previous(self, button: discord.ui.Button, interaction: discord.Interaction):        
        if self.page <= 1:
            button.disabled = True
            
        self.page -= 1
        self._page.label = f"Page | {self.page + 1}"
        if self._next.disabled:
            self._next.disabled = False

        embed = await create_page(self.data, self.page, self.color)
        await interaction.response.edit_message(embed=embed, view=self)    
    
    @discord.ui.button(label='Page | 1', style=discord.ButtonStyle.gray, disabled=True)
    async def _page(self, button: discord.ui.Button, interaction: discord.Interaction):    
        ...
    
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green)
    async def _next(self, button: discord.ui.Button, interaction: discord.Interaction):
        print("next")
        if len(self.data) <= 10:
            button.disabled = True
            self._previous.disabled = True
            return
        
        if self.page + 2 >= ceil(len(self.data) / 10):
            button.disabled = True  
                    
        self.page += 1
        if self.page >= 1 or self._previous.disabled:
            self._previous.disabled = False

        self._page.label = f"Page | {self.page + 1}"
        print(self.page)
        embed = await create_page(self.data, self.page, self.color)
        await interaction.response.edit_message(embed=embed, view=self)    
        
    @discord.ui.button(label='Bottom', style=discord.ButtonStyle.blurple)
    async def _bottom(self, button: discord.ui.Button, interaction: discord.Interaction):    
        self.page = ceil(len(self.data) / 10) - 1
        self._page.label = f"Page | {self.page + 1}"
        self._next.disabled = True
        if self._previous.disabled:
            self._previous.disabled = False
            
        embed = await create_page(self.data, self.page, self.color)
        await interaction.response.edit_message(embed=embed, view=self) 


class Leaderboard(discord.SlashCommand, guild_ids=DEV_GUILD_ID):
    """ Shows the invites leaderboard of the server """

    def __init__(self, cog):
        self.cog: InvitesCog = cog
        self.bot = self.cog.bot

    async def callback(self, response:discord.SlashCommandResponse):
        data = await self.cog.bot.mongo.get_user_data(response.guild_id)
        data = [doc async for doc in data.sort("invites", -1)]
        
        embed = await create_page(data, 0, self.bot.color)
        await response.send_message(embed=embed, view=InviteLeaderBoard(self.bot, data))

class InvitesCog(commands.Cog):
    def __init__(self, bot):
        self.bot: InviteManager = bot
        self.add_application_command(Leaderboard(self))

    @commands.command()
    async def add(self, ctx, user_id):
        user = await self.bot.fetch_user(int(user_id))
        await self.bot.mongo.update_user_data(int(user_id), ctx.guild.id, {
            "$inc": {"invites": randint(3, 30), "left": randint(3, 10)}
        })


def setup(bot):
    bot.add_cog(InvitesCog(bot))