import traceback
from marin import db, draw, GUILDS
from nextcord import *
from nextcord import Interaction, SlashOption, Colour
import nextcord
from nextcord.ext import commands, tasks
from io import BytesIO
import asyncio


class WelcomeCard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(member: nextcord.Member):
        pass

    @nextcord.slash_command('setup_cards', 'Setup welcome cards', GUILDS)
    async def cmd_setup_cards(self, inter: Interaction, card_type: str = SlashOption('card_type', 'Leave empty to list all types', False, ['username', 'text_center']), bg: str = SlashOption('background', 'Card background image (Leave empty if you want set BG Colour)', False, ['1', '2', '3']), bg_col: str = SlashOption('background_colour', 'Card background colour - R, G, B (Leave empty if you set BG Image)', False), accent: str = SlashOption('avatar_circle', 'Colour of circle around users avatar - R, G, B', False), text: str = SlashOption('card_text', 'Text below username. Works only with text_center type', False)):
        await inter.response.defer()

        if card_type is None:
            pics = []
            for x in draw.layouts.keys():
                arr = BytesIO()
                draw.draw_welcome_card(x, ('1'), (66, 135, 245), inter.user.name,
                                       inter.user.display_avatar.url, 'Hello world!').save(arr, format='PNG')
                arr.seek(0)
                pics.append(nextcord.File(arr, f'{x}.png'))
            await inter.edit_original_message(embed=Embed(title='Layouts list', description=f'Available layouts: {", ".join(draw.layouts.keys())}\n(Background: 1, avatar_circle: (66, 135, 245))', colour=Colour.purple()), files=pics)


def setup(bot):
    bot.add_cog(WelcomeCard(bot))
