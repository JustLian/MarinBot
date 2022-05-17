from nextcord import *
from nextcord import Interaction, SlashOption, Colour
import nextcord
from nextcord.ext import commands, tasks
import requests
from mojang import MojangAPI

from marin import GUILDS


SKIN_RENDER_URL = 'https://mineskin.eu/'


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command('minecraft', 'Get UUID, name history, skin render and skin download link', GUILDS)
    async def cmd_minecraft(self, inter: Interaction, name: str = SlashOption('name', 'Minecraft account name', True)):
        await inter.response.defer()

        uuid = MojangAPI.get_uuid(name)

        if uuid is None:
            em = Embed(title="Minecraft account doesn't exists",
                       description='You can take that name!', colour=Colour.brand_red())
            em.set_thumbnail(url='attachment://thinking.png')
            await inter.edit_original_message(embed=em, file=nextcord.File('./assets/thinking.png'))
            return

        profile = MojangAPI.get_profile(uuid)

        em = Embed(title=f"{name}'s Minecraft account",
                   colour=Colour.dark_purple())
        em.set_thumbnail(url=SKIN_RENDER_URL + f'armor/bust/{name}')
        em.set_author(name=name, icon_url=SKIN_RENDER_URL + f'helm/{name}')
        fields = {
            'UUID': uuid,
            'Skin': profile.skin_url,
            'Cape': profile.cape_url,
            'Names': ', '.join([x['name'] for x in MojangAPI.get_name_history(uuid)])
        }
        for field in fields.keys():
            em.add_field(name=field, value=fields[field], inline=False)
        await inter.edit_original_message(embed=em)


def setup(bot):
    bot.add_cog(Stats(bot))
