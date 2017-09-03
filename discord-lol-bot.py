import os
import json
import discord
from discord import opus
from riotwatcher import RiotWatcher
import aiohttp
from overwatch_api.core import AsyncOWAPI
from overwatch_api.constants import *
from load_opus import load_opus_lib as load_opus


with open('bot.json') as data:
    conf = json.load(data)

client = discord.Client(max_messages=100)
invoker = conf['invoker']
lol_token = conf['lol_api']


@client.event
async def on_ready():
    print('Logged in!\nName: {}\nId: {}'.format(
        client.user.name, client.user.id))
    load_opus()
    if opus.is_loaded():
        print("Opus Loaded")


@client.event
async def on_message(msg):
    if msg.author.id != client.user.id:  # ignore our own commands
        if msg.content.startswith(conf['invoker']):
            command = msg.content[len(conf['invoker']):]
            print(command)
            if command == 'help':
                g_4 = '\n' + conf['invoker']
                g_3 = '{0}{1}'.format(conf['invoker'], g_4.join(os.listdir('audio/')))
                g_3 = g_3.lower().replace(conf['fileformat'], '')
                g_2 = 'Comandos para o ' + conf['bot'] + ':\n' + \
                    g_3 + '\n'
                if not msg.channel.is_private:
                    await client.send_message(msg.channel, g_2)
            elif command.startswith('lol'):
                player_name = command.lstrip('lol ')
                watcher = RiotWatcher(lol_token)
                region = 'br1'
                player = watcher.summoner.by_name(region, player_name)
                ranked = watcher.league.positions_by_summoner(region, player['id'])
                for lists in ranked:
                    for items in ranked:
                        name = items['playerOrTeamName']
                        tier = items['tier'].lower()
                        rank = items['rank']
                        wins = str(items['wins'])
                        loss = str(items['losses'])
                        if items['queueType'] == 'RANKED_FLEX_TT':
                            fila = 'Twisted Treeline'
                        elif items['queueType'] == 'RANKED_SOLO_5x5':
                            fila = 'Summoners Rift Solo/Duo'
                        elif items['queueType'] == 'RANKED_FLEX_SR':
                            fila = 'Summoners Rift Flex'
                if player['summonerLevel'] < 30:
                        await client.send_message(msg.channel, player['name'] + ' is currently level ' + str(player['summonerLevel']))
                elif ranked == []:
                    await client.send_message(msg.channel, player['name'] + ' is not ranked.')
                else:
                    em = discord.Embed(title=fila)
                    em.add_field(name="Rank", value=tier.capitalize() + ' ' + rank, inline=True)
                    em.add_field(name="Wins", value=wins, inline=True)
                    em.add_field(name="Loss", value=loss, inline=True)
                    em.set_author(name=name, icon_url=client.user.default_avatar_url)
                    await client.send_message(msg.channel, embed=em)
                print(player)
                print(ranked)

            elif command.startswith('ow'):
                battletag = command.lstrip('ow ')
                owclient = AsyncOWAPI()
                owdata = {}
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                    owdata[PC] = await owclient.get_stats(battletag.capitalize(), session=session, platform=PC)
                    d = owdata[PC]['us']['competitive']['overall_stats']
                    em = discord.Embed(title= 'Overwatch Stats: ')
                    for k, v in d.items():
                        # if k == 'comprank':
                        em.add_field(name=k, value=v, inline=True)
                        print(k, v)
                    #await client.send_message(msg.channel, str(k) + str(v))

                    # em.set_author(name=battletag, icon_url=client.user.default_avatar_url)
                    await client.send_message(msg.channel, embed=em)


            else:
                if msg.author.voice_channel:
                    try:
                        message = msg.author.voice_channel
                        voice = await client.join_voice_channel(message)
                        player = voice.create_ffmpeg_player('audio/' + command + conf['fileformat'], use_avconv=True)
                        player.volume = 0.3
                        player.start()
                        print("sound played!")
                    except:
                        pass
                else:
                    await client.send_message(msg.channel, 'voce nao esta em um canal de voz!')
                while True:
                    try:
                        if player.is_done():
                            await voice.disconnect()
                            break
                    except:
                        break


@client.event
async def on_voice_state_update(before, after):
    msg_channel = client.get_channel('351577974870376451')
    v_channel = client.get_channel('260073676874055681')
    if after.voice_channel == v_channel and before.self_mute == after.self_mute and before.self_deaf == after.self_deaf:
        await client.send_message(msg_channel, before.name + ' entrou no canal.', tts=True)

client.run(conf['token'])