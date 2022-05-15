from pprint import pprint
import re
import requests
from nextcord import *
from nextcord import Interaction, SlashOption, Colour, Embed
import nextcord
from nextcord.ext import commands

from marin import GUILDS


JIKAN = 'https://api.jikan.moe/v4'
WAIFUPICS = 'https://api.waifu.pics'
WAIFU_CATEGORIES = ['waifu', 'neko', 'shinobu', 'megumin', 'bully', 'cuddle', 'cry', 'hug', 'awoo', 'kiss', 'lick', 'pat', 'smug', 'bonk', 'yeet', 'blush', 'smile',
                    'wave', 'highfive', 'handhold', 'nom', 'bite', 'glomp', 'slap', 'kill', 'kick', 'happy', 'wink', 'poke', 'dance', 'cringe', 'waifu', 'neko', 'trap', 'blowjob']


def findAnimeByName(name: str) -> list[dict]:
    params = {
        'page': 1,
        'limit': 5,
        'q': name,
        'order_by': 'title',
    }
    resp = requests.get(JIKAN + '/anime', params=params)
    return resp.json()


def findMangaByName(name: str) -> list[dict]:
    params = {
        'page': 1,
        'limit': 5,
        'q': name,
        'order_by': 'title',
    }
    resp = requests.get(JIKAN + '/manga', params=params)
    return resp.json()


class sel_SelectAnime(nextcord.ui.Select):
    def __init__(self, data):
        self.data = data
        titles = []
        for item in data:
            if item['title'] not in titles:
                titles.append(item['title'])
        options = [nextcord.SelectOption(label=title) for title in titles]
        super().__init__(placeholder="Select anime",
                         max_values=1, min_values=1, options=options)

    async def callback(self, inter: Interaction):
        await inter.response.defer()
        data = nextcord.utils.find(
            lambda x: x['title'] == self.values[0], self.data)
        em = Embed(title=data['title'], description=data['synopsis'])
        em.set_image(url=data['images']['jpg']['image_url'])
        em.set_thumbnail(url='attachment://happy-1.png')
        if data['trailer']['url'] is not None:
            em.set_author(name='Watch trailer', url=data['trailer']['url'])
        fields = {
            'Rating': data['rating'],
            'Episodes': data['episodes'],
            'Genres': ', '.join([g['name'] for g in data['genres']]),
            'Themes': ', '.join([t['name'] for t in data['themes']]),
            'Status': data['status'],
        }
        [em.add_field(name=n, value=fields[n], inline=False)
         for n in fields.keys()]
        await inter.edit_original_message(embed=em)


class SelectAnime(nextcord.ui.View):
    def __init__(self, data, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(sel_SelectAnime(data))


class sel_SelectManga(nextcord.ui.Select):
    def __init__(self, data):
        self.data = data
        titles = []
        for item in data:
            if item['title'] not in titles:
                titles.append(item['title'])
        options = [nextcord.SelectOption(label=title) for title in titles]
        super().__init__(placeholder="Select manga",
                         max_values=1, min_values=1, options=options)

    async def callback(self, inter: Interaction):
        await inter.response.defer()
        data = nextcord.utils.find(
            lambda x: x['title'] == self.values[0], self.data)

        em = Embed(title=data['title'], description=data['synopsis'])
        em.set_image(url=data['images']['jpg']['image_url'])
        em.set_thumbnail(url='attachment://happy-1.png')
        fields = {
            'Rating': data['rating'] if 'rating' in data else '?',
            'Chapters': data['chapters'] if 'chapters' in data else '?',
            'Volumes': data['volumes'] if 'volumes' in data else '?',
            'Genres': ', '.join([g['name'] for g in data['genres']]) if data['genres'] != [] else '?',
            'Themes': ', '.join([t['name'] for t in data['themes']]) if data['themes'] != [] else '?',
            'Status': data['status'] if 'status' in data else '?',
        }
        [em.add_field(name=n, value=fields[n], inline=False)
         for n in fields.keys()]
        await inter.edit_original_message(embed=em)


class SelectManga(nextcord.ui.View):
    def __init__(self, data, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(sel_SelectManga(data))


class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command('search', 'Search manga/anime', GUILDS)
    async def cmd_search(self, inter: Interaction, qType: str = SlashOption('type', 'Anime/Manga', True, ['Anime', 'Manga']), name: str = SlashOption('title', 'Anime/manga title you searching for')):
        await inter.response.defer()

        em = Embed(title='Searching...',
                   description='Please be patient :>', colour=Colour.purple())
        em.set_thumbnail(url='attachment://thinking.png')
        await inter.edit_original_message(embed=em, files=[nextcord.File('./assets/thinking.png')])
        if qType == 'Anime':
            data = findAnimeByName(name)['data']

            if len(data) == 0:
                em.colour = Colour.brand_red()
                em.title = "I can't find it!"
                em.description = "Maybe you made a typo?"
                em.set_thumbnail(url='attachment://sad.gif')
                await inter.edit_original_message(embed=em, files=[nextcord.File('./assets/sad.gif')])
                return

            em.title = 'Choose anime'
            em.description = 'I found it!'
            em.colour = Colour.from_rgb(168, 93, 151)
            em.set_thumbnail(url='attachment://happy-1.png')
            await inter.edit_original_message(embed=em, files=[nextcord.File('./assets/happy-1.png')], view=SelectAnime(data))

        if qType == 'Manga':
            data = findMangaByName(name)['data']

            if len(data) == 0:
                em.colour = Colour.brand_red()
                em.title = "I can't find it!"
                em.description = "Maybe you made a typo?"
                em.set_thumbnail(url='attachment://sad.gif')
                await inter.edit_original_message(embed=em, files=[nextcord.File('./assets/sad.gif')])
                return

            em.title = 'Choose manga'
            em.description = 'I found it!'
            em.colour = Colour.from_rgb(168, 93, 151)
            em.set_thumbnail(url='attachment://happy-1.png')
            await inter.edit_original_message(embed=em, files=[nextcord.File('./assets/happy-1.png')], view=SelectManga(data))

    @nextcord.slash_command('waifu', 'Get random image of some waifu! [waifu.pics api]')
    async def cmd_waifu(self, inter: Interaction, cType: str = SlashOption('type', 'Should picture be SFW or NSFW?', True, ['sfw', 'nsfw']), category=SlashOption('category', 'Image category (leave empty for full list)', False)):
        await inter.response.defer()

        if category is None:
            em = nextcord.Embed(title='/waifu categories',
                                colour=Colour.from_rgb(196, 93, 212))
            em.add_field(name='SFW', value='waifu neko shinobu megumin bully cuddle cry hug awoo kiss lick pat smug bonk yeet blush smile wave highfive handhold nom bite glomp slap kill kick happy wink poke dance cringe')
            em.add_field(name='NSFW', value='waifu neko trap blowjob')
            em.set_thumbnail(url='attachment://happy-3.png')
            await inter.edit_original_message(embed=em, file=nextcord.File('./assets/happy-3.png'))
            return

        fail = False
        if category not in WAIFU_CATEGORIES:
            fail = True
        if cType == 'nsfw' and category not in ['waifu', 'neko', 'trap', 'blowjob']:
            fail = True

        if fail:
            em = Embed(title='Something wrong with arguments!', description='If you think something is wrong with me, tell about that to my devs!',
                       colour=Colour.brand_red())
            em.set_thumbnail(url='attachment://sad-2.gif')
            await inter.edit_original_message(embed=em, file=nextcord.File('./assets/sad-2.gif'))
            return

        if cType == 'nsfw':
            if inter.channel.nsfw == False:
                em = Embed(title="You can't do that here!",
                           description="Command available only in NSFW channels!", colour=Colour.brand_red())
                em.set_thumbnail(url='attachment://what.png')
                em.set_author(
                    name=inter.user.name, icon_url=inter.user.avatar.url if inter.user.avatar is not None else None)
                await inter.edit_original_message(embed=em, file=nextcord.File('./assets/what.png'))
                return

        resp = requests.get(WAIFUPICS + f'/{cType}/{category}')

        if resp.status_code != 200:
            em = Embed(title='Error occurred!',
                       description='Im so sorry! Please contact my developers!', colour=Colour.dark_blue())
            em.set_thumbnail(url='attachment://sad.gif')
            em.set_footer(
                text=f'CODE: {resp.status_code} | JSON: {resp.json()}')
            await inter.edit_original_message(embed=em, file=nextcord.File('./assets/sad.gif'))
            return

        em = Embed(title="Enjoy :>", colour=Colour.from_rgb(255, 0, 153))
        em.set_author(name=inter.user.name,
                      icon_url=inter.user.avatar.url if inter.user.avatar is not None else None)
        em.set_author(
            name=inter.user.name, icon_url=inter.user.avatar.url if inter.user.avatar is not None else None)
        em.set_image(url=resp.json()['url'])
        await inter.edit_original_message(embed=em)


def setup(bot):
    bot.add_cog(Anime(bot))
