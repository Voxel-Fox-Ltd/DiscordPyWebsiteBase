import logging
from urllib.parse import urlencode

import discord
import toml
from discord.ext import commands


class CustomBot(commands.AutoShardedBot):
    """A child of discord.ext.commands.AutoShardedBot to make things a little easier when
    doing my own stuff"""

    def __init__(self, config_file:str='config/config.toml', logger:logging.Logger=None, *args, **kwargs):
        """The initialiser for the bot object
        Note that we load the config before running the original method"""

        # Store the config file for later
        self.config = None
        self.config_file = config_file
        self.logger = logger or logging.getLogger("bot")
        self.reload_config()

        # Run original
        super().__init__(command_prefix="!", *args, **kwargs)

    def get_invite_link(self, *, scope:str='bot', response_type:str=None, redirect_uri:str=None, guild_id:int=None, **kwargs):
        """Gets the invite link for the bot, with permissions all set properly"""

        permissions = discord.Permissions()
        for name, value in kwargs.items():
            setattr(permissions, name, value)
        data = {
            'client_id': self.config.get('oauth', {}).get('client_id', None) or self.user.id,
            'scope': scope,
            'permissions': permissions.value
        }
        if redirect_uri:
            data['redirect_uri'] = redirect_uri
        if guild_id:
            data['guild_id'] = guild_id
        if response_type:
            data['response_type'] = response_type
        return 'https://discordapp.com/oauth2/authorize?' + urlencode(data)

    def reload_config(self):
        """Re-reads the config file into cache"""

        self.logger.info("Reloading config")
        try:
            with open(self.config_file) as a:
                self.config = toml.load(a)
        except Exception as e:
            self.logger.critical(f"Couldn't read config file - {e}")
            exit(1)

    async def login(self, token:str=None, *args, **kwargs):
        """The original login method with optional token"""

        await super().login(token or self.config['authorization_tokens']['bot'], *args, **kwargs)

    async def start(self, token:str=None, *args, **kwargs):
        """Start the bot with the given token, create the startup method task"""

        self.logger.info("Running original D.py start method")
        await super().start(token or self.config['authorization_tokens']['bot'], *args, **kwargs)

    async def close(self, *args, **kwargs):
        """The original bot close method, but with the addition of closing the
        aiohttp ClientSession that was opened on bot creation"""

        self.logger.debug("Running original D.py logout method")
        await super().close(*args, **kwargs)
