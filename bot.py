import json
import os
import asyncio
from datetime import datetime, timedelta
from pytz import timezone 

import discord
from discord.ext import commands, tasks

from gtts import gTTS
from mutagen.mp3 import MP3

TOKEN = 'MTA0MTk5NjQyODU5MzA3MDA5MA.G7DmK7.C-eGS6tlPwyvTfRn2Vl2dsmAydNH-Jarg2CRiE'
ALERT_FILE_LOCATION = "./bin/alert.mp3"
MP3_FILE_LOCATION = "./bin/test.mp3"

intents = discord.Intents.all()
intents.members = True
intents.typing = True
intents.presences = True
intents.messages = True

client = commands.Bot(command_prefix="!", intents=intents)

BOSS_RESPAWN_TIMERS = None
BOSS_CONFIG_PATH = "./bosses.json"
with open(BOSS_CONFIG_PATH, "r") as fp:
    BOSS_RESPAWN_TIMERS = json.loads(fp.read())

RECORDED_BOSS_TIMES = {}
VOICE_CHANNEL = None

def audio_len(path):
    return MP3(path).info.length

# --------------- Event listeners --------------- #
@client.event
async def on_ready():
    reminder.start()
    print(f'{client.user} has connected to Discord!')


# --------------- Custom Commands --------------- #
@client.command(pass_context=True)
async def ι¦ι (ctx):
    intro = "==========================\nπ δ»₯δΈζ―ζζζζηι¦ι εη¨± π\n==========================\n"
    list_of_boss_names = [f"{x} ---- {BOSS_RESPAWN_TIMERS[x]}H" for x in BOSS_RESPAWN_TIMERS if x != "test"]
    boss_name_str = "\n".join(list_of_boss_names)
    await ctx.send(intro + boss_name_str)


@client.command(pass_context=True)
async def ζ°ε’ι¦ι (ctx):
    # Sanitize lsit of inputs
    args = ctx.message.content.split(" ")[1:]
    args = [x for x in args if x]  
    if len(args) < 2:
        await ctx.send("π η‘ζ³ζ°ε’ι¦ι εη¨± -- θ«η’ΊθͺθΌΈε₯ηθ³ζζ―ζ­£η’Ίη ( !ζ°ε’ι¦ι  <ι¦ι εη¨±> <ι¦ι ιηζι> ) π")
        return

    boss_name = args[0]
    boss_respawn_time = int(args[1])

    # Save in memory 
    BOSS_RESPAWN_TIMERS[boss_name] = boss_respawn_time
    # Save on disk
    with open(BOSS_CONFIG_PATH, "w") as fp:
        json.dump(BOSS_RESPAWN_TIMERS, fp, indent=6)
    
    await ctx.send(f"π€πΌ π€πΌ ζεζ°ε’δΊζ°ι¦ι εη¨±! -- γ{boss_name}γ θ¨­ε?ζ―{boss_respawn_time}ε°ζζιη")


@client.command(pass_context=True)
async def εͺι€(ctx):
    args = ctx.message.content.split(" ")[1:]
    if len(args) < 1:
        await ctx.send("π η‘ζ³η΄ιι¦ι ζ­»δΊ‘ζι -- θ«η’ΊθͺθΌΈε₯ηθ³ζζ―ζ­£η’Ίη π")
        return

    res_time = args[0]
    RECORDED_BOSS_TIMES.pop(res_time)


@client.command(pass_context=True)
async def η΄ι(ctx):
    # Sanitize lsit of inputs
    args = ctx.message.content.split(" ")[1:]
    args = [x for x in args if x]  
    if len(args) < 1:
        await ctx.send("π η‘ζ³η΄ιι¦ι ζ­»δΊ‘ζι -- θ«η’ΊθͺθΌΈε₯ηθ³ζζ―ζ­£η’Ίη π")
        return

    boss_name = args[0]
    if boss_name not in BOSS_RESPAWN_TIMERS:
        await ctx.send(f"π η‘ζ³η΄ιι¦ι ζ­»δΊ‘ζι -- ζΎδΈε°ι¦ι εη¨± γ{boss_name}γπ")
        return

    if len(args) > 1:
        current_time = datetime.strptime(args[1], '%H:%M')
    else:
        current_time = datetime.now(timezone("Asia/Taipei"))

    # Get the boss's respawn timer
    boss_res_timer = BOSS_RESPAWN_TIMERS[boss_name]
    # Calculate the future time
    new_res_time = current_time + timedelta(hours=boss_res_timer)
    if boss_name == "test":
        new_res_time = current_time + timedelta(minutes=11)

    # Formate the date time to be human-readable
    new_res_time_str = new_res_time.strftime('%H:%M')

    # Update the entry:
    RECORDED_BOSS_TIMES[new_res_time_str] = {
        "boss": boss_name,
        "created_by": ctx.message.author.nick
    }

    await ctx.send(f"π ζεη΄ιδΊηζ­»δΊ‘ζι! -- ε°ζε¨ {new_res_time_str} ηεειεζιε€§ε?Άγ{boss_name}γηιη π")


@client.command(pass_context=True)
async def ζζη΄ι(ctx):
    if not RECORDED_BOSS_TIMES:
        await ctx.send(f"η?εζ²ζδ»»δ½η΄ι")
        return

    intro = "==========================\nβ οΈ η?εδ»₯θ¨ιηι¦ι ιηζι β οΈ\n=========================="
    await ctx.send(intro)

    str_record_times = ""
    # sort based on earliest respawn time
    for time in sorted(RECORDED_BOSS_TIMES):
        boss_name = RECORDED_BOSS_TIMES[time]["boss"]
        created_by = RECORDED_BOSS_TIMES[time]["created_by"]
        str_record_times += f"{time} - {boss_name}            η΄ιθ: {created_by}\n" 

    await ctx.send(str_record_times)


@client.command(pass_context=True)
async def ε ε₯(ctx):
    global VOICE_CHANNEL
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        VOICE_CHANNEL = await channel.connect()
    else:
        await ctx.send("ζ¨η?εδΈ¦ζ²ζε¨θͺι³ι »ιθ£‘ι’")


@client.command(pass_context=True)
async def ιεΊ(ctx):
    global VOICE_CHANNEL
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        VOICE_CHANNEL = None
    else:
        await ctx.send("ζ¨η?εδΈ¦ζ²ζε¨θͺι³ι »ιθ£‘ι’")


@tasks.loop(seconds=1.0)
async def reminder():
    # Grab the channel to send message
    channel = client.get_channel(1044858675623383060)

    # Get current time in Taiwan + 10 minutes in the future
    new_res_time_plus_ten = datetime.now(timezone("Asia/Taipei")) + timedelta(minutes=10)
    new_res_time_plus_ten_str = new_res_time_plus_ten.strftime('%H:%M')
    if new_res_time_plus_ten_str in RECORDED_BOSS_TIMES:
        boss_name = RECORDED_BOSS_TIMES[new_res_time_plus_ten_str]["boss"]
        reminder_str = f"@here η±εΏζι, {boss_name} ε¨εειδΉεΎ ({new_res_time_plus_ten_str}) ε³ε°ιη!"

        # Send notification to text channel
        await channel.send(reminder_str)

        if VOICE_CHANNEL:
            speech = gTTS(text=f"η±εΏζι, {boss_name} ε¨εειδΉεΎ ({new_res_time_plus_ten_str}) ε³ε°ιη!", lang="zh-CN", slow=False)
            speech.save(MP3_FILE_LOCATION)
            # Play first alert sound
            VOICE_CHANNEL.play(discord.FFmpegPCMAudio(source=ALERT_FILE_LOCATION))
            
            # Wait for it to finish
            counter = 0
            duration = audio_len(ALERT_FILE_LOCATION)
            while not counter >= duration:
                await asyncio.sleep(1)
                counter += 1

            # Play reminder message
            VOICE_CHANNEL.play(discord.FFmpegPCMAudio(source=MP3_FILE_LOCATION))

        # pop it after successfully reminded
        RECORDED_BOSS_TIMES.pop(new_res_time_plus_ten_str)


client.run(TOKEN)
