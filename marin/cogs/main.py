from datetime import timedelta, datetime
from nextcord import *
from nextcord import Interaction, SlashOption, Colour
import nextcord
from nextcord.ext import commands, tasks
import requests

from marin import GUILDS


RANDOM_JOKE_URL = 'https://v2.jokeapi.dev/joke/Pun?blacklistFlags=nsfw,religious,racist'
BOREDAPI_URL = 'http://www.boredapi.com/api'


reminds = {}


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.remind_loop.start()

    @nextcord.slash_command('help', 'List all commands', GUILDS)
    async def cmd_help(self, inter: Interaction):
        await inter.response.defer()
        em = nextcord.Embed(title="Marin's commands",
                            description="List of all Marin's commands with description", colour=Colour.from_rgb(186, 82, 235))
        em.set_thumbnail(url='attachment://happy-2.png')
        fields = {
            '/search <type> <query>': 'Search for anime/manga.',
            '/waifu <type> [category]': 'Get random waifu image!',
            '/remind <time> [message]': 'I will ping you in this channel in <time>',
            '/joke': 'Get some random joke',
            '/im_bored': 'Ideas for things to do'
        }

        for field in fields.keys():
            em.add_field(name=field, value=fields[field], inline=False)

        await inter.edit_original_message(embed=em, file=nextcord.File('./assets/happy-2.png'))

    @nextcord.slash_command('remind', 'Ping you in specific channel after specific amount of time', GUILDS)
    async def cmd_remind(self, inter: Interaction, time: str = SlashOption('remind_in', 'Time in format MM-HH-DD', True), message: str = SlashOption('message', 'I will send this message with ping!', False)):
        await inter.response.defer()
        global reminds
        time = time.split('-')

        if not all([len(t) == 2 for t in time]) or len(time) > 3:
            em = nextcord.Embed(
                title="Wrong time format", description="Correct time format is MM-HH-DD. If you think something is wrong with me, tell about that to my devs!", colour=Colour.brand_red())
            em.set_thumbnail(url='attachment://sad-2.gif')
            await inter.edit_original_message(embed=em, file=nextcord.File('./assets/sad-2.gif'))
            return

        if len(time) == 1:
            td = timedelta(minutes=int(time[0]))
        elif len(time) == 2:
            td = timedelta(minutes=int(time[0]), hours=int(time[1]))
        else:
            td = timedelta(minutes=int(time[0]), hours=int(
                time[1]), days=int(time[2]))

        rem_time = (datetime.now() + td).strftime('%d-%H-%M')

        reminds[rem_time] = (inter.channel, inter.user, message)
        em = Embed(title="I've got you!",
                   description=f"Now just wait! I will ping you in this channel in {':'.join(time)} MM:HH:DD", colour=Colour.purple())
        em.set_thumbnail(url='attachment://happy-4.png')
        await inter.edit_original_message(embed=em, file=nextcord.File('./assets/happy-4.png'))

    @nextcord.slash_command('joke', 'I will tell you random joke!', GUILDS)
    async def cmd_joke(self, inter: Interaction):
        await inter.response.defer()
        resp = requests.get(RANDOM_JOKE_URL)

        if resp.status_code != 200:
            em = Embed(title='Error occurred!',
                       description='Im so sorry! Please contact my developers!', colour=Colour.dark_blue())
            em.set_thumbnail(url='attachment://sad.gif')
            em.set_footer(
                text=f'CODE: {resp.status_code} | JSON: {resp.json()}')
            await inter.edit_original_message(embed=em, file=nextcord.File('./assets/sad.gif'))
            return

        joke = resp.json()
        await inter.edit_original_message(content=f'There you go 💖!\n{joke["setup"]} ||{joke["delivery"]}||')

    @nextcord.slash_command('im_bored', 'I will give you some random stuff to do!', GUILDS)
    async def cmd_bored(self, inter: Interaction):
        await inter.response.defer()
        resp = requests.get(BOREDAPI_URL + '/activity/')

        if resp.status_code != 200:
            em = Embed(title='Error occurred!',
                       description='Im so sorry! Please contact my developers!', colour=Colour.dark_blue())
            em.set_thumbnail(url='attachment://sad.gif')
            em.set_footer(
                text=f'CODE: {resp.status_code} | JSON: {resp.json()}')
            await inter.edit_original_message(embed=em, file=nextcord.File('./asse ts/sad.gif'))
            return

        em = Embed(title='What about this?', description=resp.json()[
                   'activity'], colour=Colour.from_rgb(217, 59, 161))
        em.set_author(name=inter.user.name,
                      icon_url=inter.user.avatar.url if inter.user.avatar is not None else None)
        em.set_thumbnail(url='attachment://happy-5.gif')
        await inter.edit_original_message(embed=em, file=nextcord.File('./assets/happy-5.gif'))

    @tasks.loop(minutes=1)
    async def remind_loop(self):
        global reminds
        rms = []
        for rem in reminds.keys():
            if datetime.now().strftime('%d-%H-%M') == rem:
                await reminds[rem][0].send(f'💖 Hey, {reminds[rem][1].mention}{f", {reminds[rem][2]}" if reminds[rem][2] != None else ""}')
                rms.append(rem)
        [reminds.pop(r) for r in rms]


def setup(bot):
    bot.add_cog(Main(bot))
