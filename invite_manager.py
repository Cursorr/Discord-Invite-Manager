import discord
import json
import os

from discord.ext import commands
from cogs.mongo import Mongo


class InviteManager(commands.Bot):
    def __init__(self):

        # Loading config file
        self._config = json.load(open("config.json", "r"))

        super().__init__(
            command_prefix=self._config["prefix"],
            intents=discord.Intents.all()
        )

        self.color = int(self._config["color"], 16) + 0x200
        
        # Declaring a dict where invites will be stored
        self.invites = {}

        # Loading all cogs
        error = False
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{file[:-3]}")
                except commands.NoEntryPointError as exception:
                    error = True
                    print(exception)
        
        print("[Invite-Manager] - {}".format("Failed to load a cog." if error else "All cogs were loaded."))

    # Adding a Mongo proprety to acces db functions
    @property
    def mongo(self) -> Mongo:
        return self.get_cog("Mongo")

    async def on_ready(self):
        print("[Invite-Manager] - Connected")

    def launch(self):
        self.run(self._config["token"])


invite_manager = InviteManager()
invite_manager.launch()