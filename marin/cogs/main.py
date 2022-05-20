from datetime import timedelta, datetime
from nextcord import Interaction, SlashOption, Colour, Embed
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
        fields = {}
        for command in self.bot.get_all_application_commands():
            name = '/' + command.name
            for opt in command.options.keys():
                name += f' <{command.options[opt].name}>'
            fields[name] = command.description

        for field in fields.keys():
            em.add_field(name=field, value=fields[field], inline=False)

        await inter.edit_original_message(embed=em, file=nextcord.File('./assets/emotes/happy-2.png'))

    @nextcord.slash_command('remind', 'Ping you in specific channel after specific amount of time', GUILDS)
    async def cmd_remind(self, inter: Interaction, time: str = SlashOption('remind_in', 'Time in format MM-HH-DD', True), message: str = SlashOption('message', 'I will send this message with ping!', False)):
        await inter.response.defer()
        global reminds
        time = time.split('-')

        if not all([len(t) == 2 for t in time]) or len(time) > 3:
            em = nextcord.Embed(
                title="Wrong time format", description="Correct time format is MM-HH-DD. If you think something is wrong with me, tell about that to my devs!", colour=Colour.brand_red())
            em.set_thumbnail(url='attachment://sad-2.gif')
            await inter.edit_original_message(embed=em, file=nextcord.File('./assets/emotes/sad-2.gif'))
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
        tm = f"{td[0]}:{td[1] if len(td) > 1 else '00'}:{td[2] if len(td) > 2 else '00'}"
        em = Embed(title="Got you!",
                   description=f"Now just wait! I will ping you in this channel in {tm} (MM:HH:DD)", colour=Colour.purple())
        em.set_thumbnail(url='attachment://happy-4.png')
        await inter.edit_original_message(embed=em, file=nextcord.File('./assets/emotes/happy-4.png'))

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
            await inter.edit_original_message(embed=em, file=nextcord.File('./assets/emotes/sad.gif'))
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
        await inter.edit_original_message(embed=em, file=nextcord.File('./assets/emotes/happy-5.gif'))

    @nextcord.slash_command('mass_voice', 'Mute/unmute/deafen/undeafen all users in voicechannel', GUILDS)
    async def cmd_mass_voice(self, inter: Interaction, action: str = SlashOption('action', required=True, choices=['mute', 'deafen']), toggle: bool = SlashOption('toggle', required=True)):
        await inter.response.defer()

        # checking permissions
        if (action == 'mute' and inter.user.guild_permissions.mute_members is False) or (action == 'deafen' and inter.user.guild_permissions.deafen_members is False):
            em = Embed(title="No permissions",
                       description="You don't have enough permissions to execute that command!", colour=Colour.brand_red())
            em.set_thumbnail(url='attachment://sad-3.png')
            await inter.edit_original_message(embed=em, file=nextcord.File('./assets/emotes/sad-3.gif'))
            return

        # checking voice channel
        if inter.user.voice is None:
            em = Embed(title='You are not in VC!',
                       description='You need to join some VC to do that!', colour=Colour.brand_red())
            em.set_thumbnail(url='attachment://sad-3.png')
            await inter.edit_original_message(embed=em, file=nextcord.File('./assets/emotes/sad-3.png'))
            return

        em = Embed(
            title='Gotcha!', description=f'I will apply action {action}:{toggle} to all users in VC!', colour=Colour.purple())
        em.set_thumbnail(url='attachment://happy-5.gif')
        em.set_author(name=inter.user.name,
                      icon_url=inter.user.avatar.url if inter.user.avatar is not None else None)
        await inter.edit_original_message(embed=em, file=nextcord.File('./assets/emotes/happy-5.gif'))

        for user in inter.user.voice.channel.members:
            if action == 'mute':
                await user.edit(mute=toggle)
            else:
                await user.edit(deafen=toggle)

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
