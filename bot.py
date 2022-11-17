import datetime

import discord
from discord.ext import commands, tasks
from discord.utils import setup_logging

import requests
import os

# This is done by text file or json file usually, input currently for sake of user interactivity
MAIN_GUILD = input("Enter the name of the guild you want managed:")
API_KEY = input("Enter your API Key (For github purposes only)")
PREFIX = input("Enter your desired Prefix:")

r = requests.get(
    "https://api.wynncraft.com/public_api.php?action=guildStats&command=Emorians" + f"&apikey={API_KEY}").json()
guild_igns = [member['name'] for member in r['members'][0:]]
slash_commands_guilds = []  # Generally full of server ids you want added to support slash

intents = discord.Intents.all()
client = commands.Bot(command_prefix=PREFIX, intents=intents, slash_command_guilds=slash_commands_guilds)
timestep_run_BOOL = False
iteration = 0
owner_id = 377543612810133504
client.world_to_xp = {}
client.name_glitched_players = {}
client.names_and_ranks = {}
client.war_cooldown = False
client.hunter_cooldown = False
client.check_world = {}
client.ign_to_player_api = {}
client.my_dict = {}
ern_territories = []  # Import list of territories from txt or json file.
special = []  # Import list of special territories for txt or json file.

client.ign_to_diff = {}


class MyBot(commands.Bot):
    async def setup_hook(self):
        print(f"Logging in as: {self.user}")
        # Initial Cog Load
        print("Attempting load cogs. . .")
        for filename in os.listdir("./cogs"):
            if filename.endswith('.py'):
                print(f"Attempting to load {filename}")
                await client.load_extension(f'cogs.{filename[:-3]}')
                print(f"Successfully loaded cogs.{filename}")

        print(f"\n<BOTNAME PLACEHOLDER> has finally loaded and is ready to use, use with the prefix {PREFIX}\n"
              f"------------------------------------------------------------------------\nnig\n"
              f"------------------------------------------------------------------------")

    async def start_bot(self):
        setup_logging()
        with open("TOKEN.txt", 'r') as f:
            TOKEN = f.read()
        await self.start(TOKEN)


# Initialize Tasks
@tasks.loop(minutes=2)
async def update_status():
    from json import JSONDecodeError
    import requests
    r = requests.get(f"https://api.wynncraft.com/public_api.php?action=onlinePlayersSum&apikey={API_KEY}")

    try:
        json = r.json()
        await client.change_presence(activity=discord.Game(name='Watching ' + str(json['players_online']) + ' players'))
    except (JSONDecodeError, KeyError):
        await client.change_presence(activity=discord.Game(name="ERROR"))


# Misc Events
@client.event
async def on_ready():
    update_status.start()
    xp.start()


# Error Handler
@client.event
async def on_command_error(ctx, error):
    error = getattr(error, 'original', error)
    if isinstance(error, commands.MissingRequiredArgument):
        await cmd_help(ctx, ctx.command)
    elif isinstance(error, discord.errors.HTTPException):
        await ctx.send(str(error) + f" <@{owner_id}>")
        print("DISCORD HTTPEXCEPTION")
        print(error)
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    elif isinstance(error, discord.ext.commands.CommandNotFound):
        await ctx.reply("No command found with that name " + str(error))
    elif isinstance(error, discord.ext.commands.MaxConcurrencyReached):
        await ctx.reply(str(error) + " Try again later.")
    else:
        await ctx.send(str(error) + f" <@{owner_id}>")
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

# Misc Commands
@client.command(name='stop-w-task', hidden=True)
async def stoppings(ctx):
    war_pings.stop()
    print('pings stopped')
    await ctx.send('ok')


@client.command(name='start-w-task', hidden=True)
async def startpings(ctx):
    if ctx.author.id == owner_id:
        war_pings.start()
        print('pings started')
        await ctx.send('ok')
    else:
        await ctx.send("Only authorized users may reload the bot..")



# Functions (Unorganized)
async def cmd_help(ctx, cmd):
    now = datetime.datetime.utcnow()
    embed = discord.Embed(title=f"Help Command: {cmd}",
                          description=f"{help_syntax(cmd)}",
                          colour=ctx.author.colour)
    embed.add_field(name="Command Usage", value=cmd.description or "No description")
    embed.add_field(name='\u200B', value='\u200B')
    await ctx.send(embed=embed)


def help_syntax(cmd):
    cmd_and_aliases = "|".join([str(cmd), *cmd.aliases])
    params = []

    for key, value in cmd.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

    params = " ".join(params)

    return f"`{PREFIX}{cmd_and_aliases} {params}`"
