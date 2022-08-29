import asyncio
from datetime import datetime
from marin import GUILDS
from ossapi import *
from nextcord.ext import commands
import nextcord
from nextcord import Embed, Colour, Interaction, SlashOption


with open('./secrets/client_id') as f:
    _client_id = f.read().strip()
with open('./secrets/client_secret') as f:
    _client_secret = f.read().strip()
api = OssapiV2(_client_id, _client_secret)
RANKS = {'XH': '<:osuXH:987231160679669840>', 'X': '<:osuX:987231156942557204>', 'SH': '<:osuSH:987231152576270346>', 'S': '<:osuS:987231149287956480>',
         'D': '<:osuD:987231145617928262>', 'C': '<:osuC:987231143654985740>', 'B': '<:osuB:987231142522527754>', 'A': '<:osuA:987231137766191104>'}
EMOJIS = {'star': '<:osuStar:987233994582151198>', 'fruits': '<:modeFruits:987236124743327794>',
          'mania': '<:modeMania:987236126328774736> ', 'osu': '<:modeOsu:987236127545126973>', 'takio': '<:modeTakio:987236129424150569>', 'supporter': '<:osuSupporter:987252490909134858>'}


def score_embed(score: Score):
    user = score.user()
    em = Embed(title=f'{score.beatmapset.artist} - {score.beatmapset.title} {EMOJIS[score.mode.value]} | {RANKS[score.rank.value]}', description=f'{score.beatmap.difficulty_rating}{EMOJIS["star"]} | Modes: {score.mods}', colour=Colour.blurple(
    ), timestamp=score.created_at, url=f'https://osu.ppy.sh/beatmapsets/{score.beatmapset.id}')
    em.set_thumbnail(url=score.beatmapset.covers.list)
    em.set_footer(text=f'{user.username}', icon_url=user.avatar_url)
    em.add_field(name='Score', value=score.score)
    em.add_field(name='Accuracy', value=round(score.accuracy * 100, 2))
    em.add_field(name='Max combo', value=score.max_combo)
    em.add_field(name='pp', value=round(score.pp)
                 if score.pp is not None else 'N/A')
    em.add_field(name='Global ranking',
                 value=score.rank_global if score.rank_global is not None else 'N/A')
    em.add_field(
        name='Country ranking', value=score.rank_country if score.rank_country is not None else 'N/A')
    return em


async def user_search(bot, inter, ign):
    res = api.search(SearchMode.USERS, ign)

    if res.users.total == 0:
        await inter.edit_original_message(embed=Embed(title='Nothing found', description=f'osu!api returned empty response.', colour=Colour.brand_red()))
        return

    if res.users.total == 1:
        return res.users.data[0]

    else:
        def check(m):
            try:
                n = int(m.content)
            except:
                return False
            return 0 < n <= res.users.total and m.channel == inter.channel and m.author.id == inter.user.id

        em = Embed(title='Choose user',
                   description=f'Found {res.users.total} results. Enter number from 1 to {res.users.total}', colour=Colour.greyple())
        for u in enumerate(res.users.data):
            em.add_field(name=u[0] + 1, value=u[1].username)
        await inter.edit_original_message(embed=em)
        mg = await bot.wait_for('message', check=check)
        await mg.delete()
        return res.users.data[int(mg.content) - 1]


class Osu(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @nextcord.slash_command('osu', guild_ids=GUILDS)
    async def osu(self, inter: nextcord.Integration):
        pass

    @osu.subcommand('last_score', 'Last play of user', GUILDS)
    async def last_score(self, inter: nextcord.Interaction, ign: str = SlashOption('player', 'Name of player to search', True)):
        await inter.response.defer()
        user: UserCompact = await user_search(self.bot, inter, ign)

        if user is None:
            return

        score = api.user_scores(user.id, ScoreType.RECENT, False, limit=1)
        if len(score) == 0:
            await inter.edit_original_message(embed=Embed(title='No info', description='osu!api returned empty response', colour=Colour.brand_red()))
            return
        score = score[0]
        await inter.edit_original_message(embed=score_embed(score))

    @osu.subcommand('user', 'Get user\'s profile', GUILDS)
    async def get_user(self, inter: Interaction, ign: str = SlashOption('player', 'Name of player to search', True)):
        await inter.response.defer()
        user: UserCompact = (await user_search(self.bot, inter, ign))

        if user is None:
            return
        user = user.expand()

        em = Embed(
            title=f'{user.username}\' osu! profile {EMOJIS["supporter"] if user.is_supporter else ""}', description=f"{user.statistics.grade_counts.a}{RANKS['A']} | {user.statistics.grade_counts.sh}{RANKS['SH']} | {user.statistics.grade_counts.s}{RANKS['S']} | {user.statistics.grade_counts.ss}{RANKS['X']} | {user.statistics.grade_counts.ssh}{RANKS['XH']}", colour=Colour.greyple(), url=f'https://osu.ppy.sh/users/{user.id}', timestamp=user.join_date)
        em.set_thumbnail(url=user.avatar_url)
        em.set_footer(text='Account created',
                      icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Osu%21_Logo_2016.svg/1024px-Osu%21_Logo_2016.svg.png')
        em.add_field(name='Global ranking',
                     value=f'#{user.statistics.global_rank}')
        em.add_field(name='Country ranking',
                     value=f'#{user.statistics.country_rank}')
        em.add_field(name='Country', value=user.country.name, inline=False)
        em.add_field(name='pp', value=round(user.statistics.pp))
        em.add_field(name='Level', value=user.statistics.level.current)
        em.add_field(name='Playcount', value=user.statistics.play_count)
        em.add_field(name='Total score', value=user.statistics.total_score)
        em.add_field(name='Max combo', value=user.statistics.maximum_combo)
        em.add_field(name='Total achievements',
                     value=len(user.user_achievements))
        em.add_field(name='Playmode', value=user.playmode, inline=False)
        if user.interests is not None:
            em.add_field(name='Interests', value=user.interests)

        await inter.edit_original_message(embed=em)


def setup(bot):
    bot.add_cog(Osu(bot))
