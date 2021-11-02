# bot.py
import os

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from riotwatcher import LolWatcher, ApiError
import LoL_api_functions as func
import JSON_controls as JC
import ast
import urllib.request
import asyncio
import random
import BetActions
import ConfigActions as C
import json
import threading

# discord bot token
TOKEN = "DISCORDTOKEN"
# setting prefix
bot = commands.Bot(command_prefix="*", case_insensitive=True)
my_region = 'EUN1'
# ew shit help command
bot.help_command = None
Placed1 = ""
Placed2 = ""
Placed3 = ""
Placed4 = ""
Placed5 = ""
OverAllPoints = []


@bot.event
async def on_ready():
    stats = json.load(open("globalStats.json"))
    try:
        stats[0]['HighestWinstreak']
    except:
        await JC.pop_dict_in_list("globalStats.json", stats[0])
        NewStats = {"W": stats[0]['W'], "L": stats[0]['L'], "OverallBets": stats[0]['OverallBets'],
                    "HighestWinstreak": 0}
        await JC.write_to_file("globalStats.json", NewStats)
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="*signup"))


# signs up the user to start using the bot!
@bot.command()
async def signup(ctx):
    if not await C.ChannelAllowed(ctx):
        await ctx.send("You can't use this command here.")
        return False
    mention = str(ctx.author.mention)
    if "!" in mention:
        mention = mention.replace("!", '')
    if await JC.look_for_value_in_file("users.json", "DiscordID", mention) != False:
        await ctx.send(mention + ", You are already signed up! You cannot sign up more than once.")
        return False
    if ctx.guild:
        await ctx.send("Your journey starts at your DMs! Good luck!")
    embed = discord.Embed(color=0xff0000)
    embed.add_field(name="WELCOME TO LOL BET BOT!",
                    value="Bet on your games with points (never real money), climb up the ranks and enjoy beating your friends in bets!",
                    inline=True)
    embed.add_field(name="The first step",
                    value="First of all, We'll need to link your LoL account. Simply enter the command *createaccount "
                          " (yourservername) (youraccountname) without the (), in one line", inline=True)
    embed.add_field(name="Problems?",
                    value="If you're unsure what region you are in, use op.gg or any other site and look for your name. For a server list use *servers . ",
                    inline=True)
    await ctx.author.send(embed=embed)


# Connect LoL account
@bot.command()
async def createaccount(ctx, region, *, name):
    if ctx.guild:
        print(await C.ChannelAllowed(ctx))
        if not await C.ChannelAllowed(ctx):
            await ctx.send("You can't use this command here.")
            return False
    print(await JC.look_for_value_in_file("users.json", "DiscordID", str(ctx.author.mention)) != False)
    if await JC.look_for_value_in_file("users.json", "DiscordID", str(ctx.author.mention)) != False:
        await ctx.send("You are already signed up! You cannot sign up more than once.")
        return False
    try:
        profile = await func.look_for_summoner_by_name(region, name)
        print(profile)
    except:
        await ctx.send("I couldn't find any profile with the name " + str(name) + " in the region " + str(
            region) + "! Is this the correct region? Did you input"
                      " your account name correctly?")
        return False
    if await JC.look_for_value_in_file("users.json", "LoL Account", name) != False:
        await ctx.send("This LoL account was linked to another Discord account.")
        return False
    if profile['profileIconId'] == 20:
        try:
            rank = \
                func.watcher.league.by_summoner(await func.get_region_by_correct_acronym(region),
                                                profile['id'])[0][
                    'tier']
        except:
            rank = "UNRANKED"
        embed = discord.Embed(title="ACCOUNT LINKED!", color=0xffa200)
        embed.add_field(name="LoL Rank", value=rank, inline=True)
        embed.add_field(name="BP (Bet points, similar to LP)", value="0", inline=False)
        embed.add_field(name="Bet Rank", value="Start in Iron! Climb your way up!", inline=False)
        embed.add_field(name="WELCOME!",
                        value="Now that your account is linked, when you get into a normal/ranked match, use *StartBet!",
                        inline=True)
        embed.set_thumbnail(url=await func.get_rank_image(rank))
        embed.add_field(name="And lastly...",
                        value="Bets will never tell you to gamethrow. In most bets, you must win. All bets reward GOOD PLAY, not trolling. "
                              "Please NEVER GAMETHROW in order to win a bet.",
                        inline=True)
        await ctx.send(embed=await GenerateTip(embed))
        values = {"DiscordID": str(ctx.author.mention), "LoL Account": profile['puuid'], "Region": region,
                  "Points": 100,
                  "Rank": "IRON", "BP": 0, "W": 0, "L": 0, "PROMO": False, "Name": str(ctx.author.name), "Rerolls": 0,
                  "Winstreak": 0}
        await JC.write_to_file("users.json", values)
    else:
        embed = discord.Embed(title="", url="https://ibb.co/3hQvHFD", color=0xff0000)
        embed.add_field(name="Account found!",
                        value="I found an account with this name. But first you must verify it is yours!",
                        inline=True)
        embed.add_field(name="Verification process",
                        value="The process is very simple. Change your account image to the image in this embed. Than trigger this command again.",
                        inline=False)
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/811654302443634760/811869890013167616/Shuriman_Pyramids_profileicon.png")
        await ctx.send(embed=await GenerateTip(embed))


# Show account info
@bot.command()
async def account(ctx, user="False"):
    await CheckUpdate(ctx)
    if not await C.ChannelAllowed(ctx):
        await ctx.send("You can't use this command here.")
        return False
    mention = str(ctx.author.mention)
    if "!" in mention:
        mention = mention.replace("!", '')
    if "!" in mention:
        mention = mention.replace("!", '')
    if user != "False":
        if "!" in user:
            CorrectUser = user.replace("!", '')
        else:
            CorrectUser = user
        user_info = await JC.look_for_value_in_file("users.json", "DiscordID", CorrectUser)
        if not user_info:
            await ctx.send("This user doesn't exist. Either he doesnt have an account or something else.")
            return
    else:
        user_info = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
    print(mention)
    LoL_info = await func.look_for_summoner(user_info[0]["Region"], user_info[0]['LoL Account'])
    if user_info == False:
        await throwErrorNoAccount(ctx)
        return False
    embed = discord.Embed(title="Account info", color=0xffa200)
    embed.add_field(name="LoL linked account", value=LoL_info['name'] + " @" + user_info[0]["Region"],
                    inline=True)
    embed.add_field(name="BP", value=user_info[0]['BP'], inline=False)
    embed.add_field(name="Bet Rank", value=user_info[0]["Rank"], inline=False)
    if user_info[0]['PROMO'] != False:
        Promos = str(user_info[0]['PROMO'])
        Promos = Promos.replace("[", '')
        Promos = Promos.replace("]", '')
        Promos = Promos.replace("L", "\u274E")
        Promos = Promos.replace("W", "\u2705")
        Promos = Promos.replace("0", '--')
        embed.add_field(name="Promo Status",
                        value=Promos, inline=False)
    embed.add_field(name="W:" + str(user_info[0]["W"]) + " L:" + str(user_info[0]["L"]),
                    value=str(percentage(user_info[0]["W"], user_info[0]["L"])) + "%"
                          + " WR", inline=False)
    embed.add_field(name="Rerolls:",
                    value=str(user_info[0]["Rerolls"]), inline=False)
    embed.add_field(name="Winstreak:",
                    value=str(user_info[0]["Winstreak"]), inline=False)
    embed.set_thumbnail(url=await func.get_rank_image(user_info[0]["Rank"]))
    await ctx.send(embed=await GenerateTip(embed))


@bot.command()
async def help(ctx, *args):
    if not await C.ChannelAllowed(ctx):
        await ctx.send("You can't use this command here.")
        return False
    if str(*args).lower() == "commands":
        embed = discord.Embed(title="Command Help", description="Case insensitive; Doesn't matter how you write the "
                                                                "commands.")
        embed.add_field(name="*servers", value="Shows a list of servers.", inline=False)
        embed.add_field(name="*StartBet", value="Start a bet. Works on loading screen.", inline=False)
        embed.add_field(name="*BetEnd", value="End a bet. After the game is over, of course!", inline=False)
        embed.add_field(name="*help", value="Guess what this one is.", inline=False)
        embed.add_field(name="*createaccount", value="Create an account (receives arguments: Region and LOL username.",
                        inline=False)
        embed.add_field(name="*account", value="Show your account info. You can mention a user to see their account.",
                        inline=False)
        embed.add_field(name="*VsBet",
                        value="Start a VsBet (recives arguments: @ the person you would like to challenge!).",
                        inline=True)
        embed.add_field(name="*VsBetEnd", value="End a Vs Bet.", inline=False)
        embed.add_field(name="*globalstats", value="Shows the bots global stats.", inline=False)
        embed.add_field(name="*patreon", value="Shows details about the bot's Patreon!.", inline=False)
        embed.add_field(name="*news", value="Shows the latest news!", inline=False)
        embed.add_field(name="*deleteaccount", value="If you're sure, delete your account.", inline=False)
        if ctx.guild:
            await ctx.send("Sent you a DM with the commands!")
        await ctx.author.send(embed=embed)
    elif str(*args).lower() == "ranks":
        embed = discord.Embed(title="RANKS HELP")
        embed.add_field(name="What are they?",
                        value="Ranks are a way to track your progress with the bot. The ranks are the same as they are in LoL: Iron, Bronze, Silver, Gold, Platinum, Diamond, Master, Grandmaster, and Challenger.",
                        inline=False)
        embed.add_field(name="How do you rank up?",
                        value="Start Bets! Depending on your real rank and your bet difficulty, You'll earn BP. When you get to 100 BP, You'll be in promos! (No divisions on Bet Bot!)",
                        inline=True)
        embed.add_field(name="What are promos?",
                        value="Promos are the way to prove that you are ready to rank up! You play up to 3 games. If you win 2, you rank up. If you lose 2, you stay in your current rank.",
                        inline=True)
        await ctx.send(embed=await GenerateTip(embed))
    else:
        embed = discord.Embed(title="You called for help?",
                              description="*help recives an argument. It can help you with many things with the bot.",
                              color=0xffa200)
        embed.add_field(name="*help commands", value="Gives a list of commands", inline=False)
        embed.add_field(name="*help ranks", value="Explains the rank system.", inline=False)
        await ctx.send(embed=await GenerateTip(embed))


# Start a bet.
@bot.command()
async def StartBet(ctx):
    await CheckUpdate(ctx)
    if not await C.ChannelAllowed(ctx):
        await ctx.send("You can't use this command here.")
        return False
    global champ_list
    mention = str(ctx.author.mention)
    if "!" in mention:
        mention = mention.replace("!", '')
    user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
    # currently in bet?
    if await JC.look_for_value_in_file("OnGoingBets.json", "DiscordAccount", mention) != False:
        await ctx.send("You're already in a bet! You can't start 2 bets.")
        return False
    print(user)
    if user == False:
        await throwErrorNoAccount(ctx)
        return False
    try:
        print(user[0]["Region"])
        user_info = await func.look_for_summoner(user[0]["Region"], user[0]["LoL Account"])
    except:
        await throwErrorWrongAccount(ctx)
        return False
    try:
        region = await func.get_region_by_correct_acronym(user[0]["Region"])
        func.watcher.spectator.by_summoner(region, user_info['id'])
    except:
        await ctx.send("Doesn't seem you're in a game. Blame Riot API if this is false.")
        return False
    else:
        region = await func.get_region_by_correct_acronym(user[0]["Region"])
        game_info = func.watcher.spectator.by_summoner(region, user_info['id'])
        game_time = await func.get_match_length(round(int(game_info['gameStartTime'] / 1000)))
        prat_id = 0
        for i in range(10):
            try:
                prats = func.get_participants_for_further_pulls_in(game_info)[i]
                if str(user_info['name']) in str(prats[i]):
                    prat_id = prats[i]
                    print(prat_id)
            except:
                break
        champ_id = prat_id["championId"]
        print(game_time)
        if int(game_time) <= 180 or int(game_time) == 0.0 or int(game_time) >= 100000:
             if game_info['gameMode'] == "CLASSIC" and game_info['gameType'] == 'MATCHED_GAME':
                pass
             else:
                await ctx.send("Can't start a game because this game isn't a ranked/draft game!")
                return
             pass
        else:
            await ctx.send("Can't start a game because it's been more than 3 minutes, or you're at loading screen, "
                           "in which i get inaccurate times. Wait for the game to start!")
            return
        champ_info = await func.look_for_champ(str(champ_id))
        if champ_info == "Invalid champ":
            champ_info = {
                'id': "http://ddragon.leagueoflegends.com/cdn/11.7.1/img/champion/MonkeyKing.png",
                'name': "Wukong, probably.",
                'title': "idk bro his api name is Monkey King"}
            print(champ_info['id'])
        rank = user[0]['Rank']
        promos = 0
        if user[0]['PROMO'] == False:
            promos = False
        else:
            promos = True
        Bet1, Bet2, Bet3 = await func.ChooseBet(rank, promos)
        print(Bet1)
        print(Bet2)
        print(Bet3)
        embed = discord.Embed(color=0xff0000)
        embed.add_field(name="Phase one: Choose your bet",
                        value="You have 3 options. Reply '1' '2' or '3' according to which one you would like. If you "
                              "dont choose in 30 seconds, I'll choose for you!",
                        inline=False)
        embed.add_field(name=Bet1['BetText'], value="Reply 1 to choose this!", inline=True)
        embed.add_field(name=Bet2['BetText'], value="Reply 2 to choose this!", inline=True)
        embed.add_field(name=Bet3['BetText'], value="Reply 3 to choose this!", inline=True)
        if user[0]['Rerolls'] >= 1:
            embed.add_field(name="REROLL AVAILABLE!",
                            value="YOU CAN REPLY WITH REROLL, YOU HAVE " + str(user[0]['Rerolls'])
                                  + " REROLLS.", inline=False)
        BetMessage = await ctx.send(embed=await GenerateTip(embed))

        def check(m):
            return m.content

        try:
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await bot.wait_for("message", check=check, timeout=30)
            print(msg.author)
            if msg.content == "1" and msg.author == ctx.author:
                BetChosen = Bet1
            elif msg.content == "2" and msg.author == ctx.author:
                BetChosen = Bet2
            elif msg.content == "3" and msg.author == ctx.author:
                BetChosen = Bet3
            elif msg.content.lower() == "reroll" and msg.author == ctx.author and user[0]['Rerolls'] >= 1:
                Bet1, Bet2, Bet3 = await func.ChooseBet(rank, promos)
                await func.RemoveReroll(user)
                new_embed = discord.Embed(color=0xff0000)
                new_embed.add_field(name="Phase one: Choose your bet",
                                    value="You have 3 options. Reply '1' '2' or '3' according to which one you would like. If you "
                                          "don't choose in 30 seconds, I'll choose for you!",
                                    inline=False)
                new_embed.add_field(name=Bet1['BetText'], value="Reply 1 to choose this!", inline=True)
                new_embed.add_field(name=Bet2['BetText'], value="Reply 2 to choose this!", inline=True)
                new_embed.add_field(name=Bet3['BetText'], value="Reply 3 to choose this!", inline=True)
                new_embed.add_field(name="This was rerolled!", value="You can't reroll this anymore.", inline=True)
                await BetMessage.edit(embed=new_embed)
                raise ValueError()
            elif msg.author == ctx.author:
                print(msg)
                await ctx.send("That is not a valid answer! I had to choose the bet for you:")
                BetChosen = random.randrange(1, 4)
                if BetChosen == 1:
                    BetChosen = Bet1
                elif BetChosen == 2:
                    BetChosen = Bet2
                elif BetChosen == 3:
                    BetChosen = Bet3
        except asyncio.TimeoutError:
            await ctx.send("You didn't answer in time! I had to choose for you:")
            BetChosen = random.randrange(1, 4)
            if BetChosen == 1:
                BetChosen = Bet1
            elif BetChosen == 2:
                BetChosen = Bet2
            elif BetChosen == 3:
                BetChosen = Bet3
        except ValueError:
            try:
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                msg = await bot.wait_for("message", check=check, timeout=30)
                print(msg.author)
                if msg.content == "1" and msg.author == ctx.author:
                    BetChosen = Bet1
                elif msg.content == "2" and msg.author == ctx.author:
                    BetChosen = Bet2
                elif msg.content == "3" and msg.author == ctx.author:
                    BetChosen = Bet3
                elif msg.author == ctx.author:
                    print(msg)
                    await ctx.send("That is not a valid answer! I had to choose the bet for you:")
                    BetChosen = random.randrange(1, 4)
                    if BetChosen == 1:
                        BetChosen = Bet1
                    elif BetChosen == 2:
                        BetChosen = Bet2
                    elif BetChosen == 3:
                        BetChosen = Bet3
            except asyncio.TimeoutError:
                await ctx.send("You didn't answer in time! I had to choose for you:")
                BetChosen = random.randrange(1, 4)
                if BetChosen == 1:
                    BetChosen = Bet1
                elif BetChosen == 2:
                    BetChosen = Bet2
                elif BetChosen == 3:
                    BetChosen = Bet3
        if champ_info['id'] == "http://ddragon.leagueoflegends.com/cdn/11.7.1/img/champion/MonkeyKing.png":
            image_url = champ_info['id']
        else:
            image_url = "http://ddragon.leagueoflegends.com/cdn/" + str(func.current_version) + "/img/champion/" + str(
                champ_info['id']) + ".png"
        print(image_url)
        embed = discord.Embed()
        embed.add_field(name="BET STARTED!", value="The bet is:", inline=False)
        embed.add_field(name=BetChosen['BetText'], value="And you're playing:", inline=True)
        embed.add_field(name=champ_info['name'], value=champ_info['title'], inline=True)
        embed.add_field(name="Good luck!", value="Use *BetEnd when you're done.", inline=False)
        embed.set_thumbnail(url=str(image_url))
        await ctx.send(embed=await GenerateTip(embed))
        BetInfo = {"DiscordAccount": user[0]['DiscordID'], "BetInfo": BetChosen, "MatchId": game_info['gameId'],
                   "Type": "Normal"}
        await JC.write_to_file("OnGoingBets.json", BetInfo)


@bot.command()
async def BetEnd(ctx):
    await CheckUpdate(ctx)
    if not await C.ChannelAllowed(ctx):
        await ctx.send("You can't use this command here.")
        return False
    mention = str(ctx.author.mention)
    if "!" in mention:
        mention = mention.replace("!", '')
    try:
        BetInfo = await JC.look_for_value_in_file("OnGoingBets.json", "DiscordAccount", mention)
        if BetInfo[0]['Type'] != "Normal":
            await ctx.send("This isn't the right type of bet! Use *VsBetEnd !")
            return
        user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
        region = await func.get_region_by_correct_acronym(user[0]['Region'])
        match = func.watcher.match.by_id(region, int(BetInfo[0]['MatchId']))
    except:
        await ctx.send("You might not be in a game, in a bet, or the game is not done, or something else happened")
        return
    Id = BetInfo[0]['BetInfo']['BetID']
    LolId = user[0]['LoL Account']
    LolAccount = func.watcher.summoner.by_puuid(region, LolId)
    print(LolAccount['id'])
    LolRank = func.watcher.league.by_summoner(region, LolAccount['id'])
    print(LolRank)
    LoLName = LolAccount['name']
    print(LoLName)
    PratId = await func.get_player_prat_id(match, LoLName)
    PratInfo = await func.get_participant_info(match, PratId)
    print("THIS " + str(PratInfo))
    print(match['gameDuration'])
    if int(match['gameDuration']) <= 240:
        await ctx.send("R E M A D E. This game was remade! Nothing happened.")
        await JC.pop_dict_in_list("OnGoingBets.json", BetInfo[0])
        return
    if await BetActions.sort_bets(Id, PratInfo, match):
        Rewarded = await func.GetRewards(BetInfo[0]['BetInfo']['BetDifficulty'], LolRank[0]['tier'], user)
        user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
        # Add win to winstreak
        await func.AddWinstreakWin(user)
        user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
        # Check if it's a new winstreak record
        stats = json.load(open("globalStats.json"))
        NewRecord = False
        if user[0]['Winstreak'] > stats[0]['HighestWinstreak']:
            await func.ChangeHighestWinstreak(stats, user[0]['Winstreak'])
            NewRecord = True
        print(Rewarded)
        if not user[0]['PROMO']:
            user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
            BPGiven = await func.CalculateBP(user, LolRank, BetInfo[0]['BetInfo']['BetDifficulty'])
            await func.AddBPAndWin(user, BPGiven)
            user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
            embed = discord.Embed(color=0xffae00)
            embed.add_field(name="!  V I C T O R Y !", value="Great job!", inline=False)
            embed.add_field(name="W:" + str(user[0]['W']) + " " + "L:" + str(user[0]['L']),
                            value=str(percentage(user[0]['W'], user[0]['L'])) + "% Winrate", inline=True)
            embed.add_field(name="The bet was: " + BetInfo[0]['BetInfo']['BetText'], value="Bet", inline=True)
            if user[0]['Rank'] != 'CHALLENGER':
                embed.add_field(name=str(BPGiven) + " BP Given!",
                                value="+" + str(BPGiven) + " | " + str(100 - user[0]['BP']) +
                                      " BP left to promotion series!",
                                inline=True)
            else:
                embed.add_field(name=str(BPGiven) + " BP Given!",
                                value="+" + str(BPGiven) + " | You're too strong for promos! You have " +
                                      str(user[0]['BP'])
                                      + " BP!",
                                inline=True)
            if Rewarded:
                embed.add_field(name="You found something on the battlefield...",
                                value="You found a Reroll!")
            if user[0]['Winstreak'] > 1:
                embed.add_field(name="WINSTREAK!",
                                value="You're on a " + str(user[0]['Winstreak']) + " winstreak, you were awarded "
                                      + str(user[0]['Winstreak'] * 2) + " bonus BP!")
            if NewRecord:
                embed.add_field(name="WOW! HIGHEST WINSTREAK EVER!",
                                value="YOU HAVE SET A NEW WINSTREAK GLOBAL RECORD OF " + str(user[0]['Winstreak']) +
                                      " WINS!!")
            embed.add_field(name="Rank:", value=user[0]['Rank'], inline=True)
            await ctx.send(embed=await GenerateTip(embed))
        else:
            user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
            await func.AddWinToPromos(user)
            user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
            Promos = str(user[0]['PROMO'])
            Promos = Promos.replace("[", '')
            Promos = Promos.replace("]", '')
            Promos = Promos.replace("L", "\u274E")
            Promos = Promos.replace("W", "\u2705")
            Promos = Promos.replace("0", '--')
            embed = discord.Embed(color=0xffae00)
            embed.add_field(name="! V I C T O R Y ! PROMO GAME WON!", value="Great job! You're on your way!",
                            inline=False)
            embed.add_field(name="W:" + str(user[0]['W']) + " " + "L:" + str(user[0]['L']),
                            value=str(percentage(user[0]['W'], user[0]['L'])) + "% Winrate", inline=True)
            embed.add_field(name="The bet was: " + BetInfo[0]['BetInfo']['BetText'], value="Bet", inline=True)
            embed.add_field(name="PROMO STATUS", value=Promos,
                            inline=True)
            embed.add_field(name="Rank:", value=user[0]['Rank'], inline=True)
            if Rewarded:
                embed.add_field(name="You found something on the battlefield...",
                                value="You found a Reroll!", inline=True)
            await ctx.send(embed=await GenerateTip(embed))
            if str(user[0]['PROMO']).count("W") >= 2:
                await func.SetBP(user, 25)
                user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
                await func.StopPromos(user)
                RankLadder = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER',
                              'CHALLENGER']
                NewRank = RankLadder.index(user[0]['Rank']) + 1
                user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
                await func.ChangeRank(user, str(RankLadder[NewRank]))
                embed = discord.Embed(color=0xffae00)
                embed.add_field(name="PREMOTED TO " + RankLadder[NewRank] + "!",
                                value="CONGRATS!!! YOU WERE PREMOTED TO " + RankLadder[NewRank] + "!", inline=False)
                embed.set_thumbnail(url=str(await func.get_rank_image(RankLadder[NewRank])))
                await ctx.send(embed=await GenerateTip(embed))
    else:
        await func.AddResetWinstreak(user)
        user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
        if not user[0]['PROMO']:
            await func.LoseBPAndLoss(user, 10)
            user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
            embed = discord.Embed(color=0xffae00)
            embed.add_field(name=". D E F E A T .", value="Better luck next time!", inline=False)
            embed.add_field(name="W:" + str(user[0]['W']) + " " + "L:" + str(user[0]['L']),
                            value=str(percentage(user[0]['W'], user[0]['L'])) + "% Winrate", inline=True)
            embed.add_field(name="The bet was: " + BetInfo[0]['BetInfo']['BetText'], value="Bet", inline=True)
            embed.add_field(name="10 BP lost:",
                            value="-10" + " | " + str(100 - user[0]['BP']) + " BP left to promotion series!",
                            inline=True)
            embed.add_field(name="Rank:", value=user[0]['Rank'], inline=True)
            await ctx.send(embed=await GenerateTip(embed))
            if int(user[0]["BP"]) <= 0:
                embed = discord.Embed()
                RankLadder = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER',
                              'CHALLENGER']
                if user[0]['Rank'] == 'IRON':
                    await func.SetBP(user, 0)
                    await ctx.send("You're Iron and cannot demote. You have been set to 0 BP.")
                else:
                    RankIndex = RankLadder.index(user[0]['Rank']) - 1
                    user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
                    await func.ChangeRank(user, RankLadder[RankIndex])
                    user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
                    await func.SetBP(user, 75)
                    embed.add_field(name="DEFEAT - DEMOTED TO " + str(RankLadder[RankIndex]) + ".",
                                    value="You got to 0 BP and was demoted to " + str(RankLadder[RankIndex]) + ".",
                                    inline=False)
                    await ctx.send(embed=await GenerateTip(embed))
        else:
            user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
            await func.AddLossToPromos(user)
            user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
            if str(user[0]['PROMO']).count("L") >= 2:
                await func.SetBP(user, 75)
                user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
                await func.StopPromos(user)
                embed = discord.Embed()
                embed.add_field(name="PROMOS LOST.",
                                value="You have lost your promos. You are now placed in " + user[0]['Rank'] + " 75 BP",
                                inline=False)
                await ctx.send(embed=await GenerateTip(embed))
            else:
                Promos = str(user[0]['PROMO'])
                Promos = Promos.replace("[", '')
                Promos = Promos.replace("]", '')
                Promos = Promos.replace("L", "\u274E")
                Promos = Promos.replace("W", "\u2705")
                Promos = Promos.replace("0", '--')
                embed = discord.Embed(color=0xffae00)
                embed.add_field(name=". D E F E A T . PROMO GAME LOST", value="Better Luck Next Time!",
                                inline=False)
                embed.add_field(name="W:" + str(user[0]['W']) + " " + "L:" + str(user[0]['L']),
                                value=str(percentage(user[0]['W'], user[0]['L'])) + "% Winrate", inline=True)
                embed.add_field(name="The bet was: " + BetInfo[0]['BetInfo']['BetText'], value="Bet", inline=True)
                embed.add_field(name="PROMO STATUS", value=Promos,
                                inline=True)
                embed.add_field(name="To Challenger!",
                                value=str(900 - user[0]['BP']) + " BP Left to go for CHALLENGER!",
                                inline=True)
                embed.add_field(name="Rank:", value=user[0]['Rank'], inline=True)
                await ctx.send(embed=await GenerateTip(embed))
    RankLadder = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
    if user[0]['BP'] >= 100 and not user[0]['PROMO'] and user[0]['Rank'] != 'CHALLENGER':
        user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
        RankIndex = int(RankLadder.index(user[0]['Rank'])) + 1
        print(RankLadder[RankIndex])
        embed = discord.Embed(title="Series Update", color=0xffae00)
        embed.add_field(name="PROMOS TO " + str(RankLadder[RankIndex]), value="--, --, --", inline=True)
        embed.add_field(name="Congrats!",
                        value="Now, You must show skill! Out of the next 3 games, YOU WONT EARN BP. To Rank up, you "
                              "must win TWO of the THREE games. Good luck!",
                        inline=True)
        await ctx.send(embed=await GenerateTip(embed))
        await func.StartPromos(user)
    BetInfo = await JC.look_for_value_in_file("OnGoingBets.json", "DiscordAccount", mention)
    await JC.pop_dict_in_list("OnGoingBets.json", BetInfo[0])


@bot.command()
async def servers(ctx):
    if ctx.guild:
        await ctx.send("You can only use this at DMs")
    else:
        await ctx.send("Here you go!")
        embed = discord.Embed(color=0xff0000)
        embed.add_field(name="LoL server list", value="Only offical Riot Servers!", inline=True)
        embed.add_field(name='BR', value="Brazil", inline=False)
        embed.add_field(name='EUNE', value="Europe Nordic & East", inline=False)
        embed.add_field(name='EUW', value="Europe West", inline=True)
        embed.add_field(name='LAN', value="Latin America North", inline=False)
        embed.add_field(name='LAS', value="Latin America South", inline=True)
        embed.add_field(name='NA', value="North America", inline=False)
        embed.add_field(name='OCE', value="Oceania", inline=False)
        embed.add_field(name='RU', value="Russia", inline=False)
        embed.add_field(name='TR', value="Turkey", inline=False)
        embed.add_field(name='JP', value="Japan", inline=True)
        embed.add_field(name='KR', value="Korea", inline=False)
        await ctx.send(embed=await GenerateTip(embed))


@bot.command()
@has_permissions(administrator=True)
async def config(ctx, args1="N", args2="A"):
    if not await JC.look_for_value_in_file("Servers.json", "Server", str(ctx.guild.id)):
        await ctx.send("This server doesn't have a config yet! use createconfig to create one!")
    else:
        ServerInfo = await JC.look_for_value_in_file("Servers.json", "Server", str(ctx.guild.id))
        AllowedChannels = ServerInfo[0]['AllowedChannels']
        if not AllowedChannels:
            AllowedChannels = "All"
        embed = discord.Embed(title="Config",
                              description="You can currently set the channels allowed to bet in.")
        embed.add_field(name="Channels Allowed", value=str(AllowedChannels) + "; Use *config 1 (channel) to change",
                        inline=False)
        await ctx.send(embed=await GenerateTip(embed))
        if args1 == "1":
            if args2 == "A":
                await ctx.send("Usage: *config 1 #channel. You can also use wipe.")
            else:
                ServerInfo = await JC.look_for_value_in_file("Servers.json", "Server", str(ctx.guild.id))
                await C.change_config(1, str(args2), ServerInfo)
                if args2 == "wipe":
                    await ctx.send("Wiped all command-specific channels.")
                    return
                if len(ServerInfo[0]['AllowedChannels']) == 1:
                    await ctx.send("Now only allowed on channel " + args2)
                else:
                    await ctx.send("Now also allowed on channel " + args2)


@bot.command()
async def VsBet(ctx, *args):
    await CheckUpdate(ctx)
    if not await C.ChannelAllowed(ctx):
        await ctx.send("You can't use this command here.")
        return False
    if '!' in str(*args):
        CorrectArgs = str(*args).replace('!', '')
    else:
        CorrectArgs = str(*args)
    if CorrectArgs == str(ctx.author.mention):
        await ctx.send("You cannot duel yourself!")
        return
    CurrentUser = 0
    if '!' in str(ctx.author.mention):
        CorrectUser = str(ctx.author.mention).replace('!', '')
    else:
        CorrectUser = ctx.author.mention
    if not await JC.look_for_value_in_file("users.json", 'DiscordID', CorrectArgs):
        await ctx.send("This user doesn't have an account! ):")
        return

    CommandUserInfo = await JC.look_for_value_in_file("users.json", "DiscordID", CorrectUser)
    InvitedUserInfo = await JC.look_for_value_in_file("users.json", "DiscordID", CorrectArgs)
    try:
        LoLUserInfo = func.watcher.summoner.by_puuid(
            await func.get_region_by_correct_acronym(CommandUserInfo[0]['Region']),
            CommandUserInfo[0]['LoL Account'])
        game_info = func.watcher.spectator.by_summoner(
            await func.get_region_by_correct_acronym(CommandUserInfo[0]['Region']),
            LoLUserInfo['id'])
    except:
        await ctx.send("Something went wrong. Are you in a game?")
        return
    LoLInvitedInfo = func.watcher.summoner.by_puuid(
        await func.get_region_by_correct_acronym(InvitedUserInfo[0]['Region']),
        InvitedUserInfo[0]['LoL Account'])
    print(game_info)
    if not str(LoLInvitedInfo['name']) in str(game_info):
        await ctx.send("You're not in the same game!")
        return

    await ctx.send(
        CorrectArgs + " , You are invited to duel by " + ctx.author.mention + "! Reply 'Yes' or 'No' To accept!")

    def check(m):
        return m.content

    try:
        def check(m):
            return str(m.author.mention).replace("!", '') == CorrectArgs and m.channel == ctx.channel

        msg = await bot.wait_for("message", check=check, timeout=30)
        print(msg.content)
        if msg.content.lower() == "yes" and str(msg.author.mention).replace("!", '') == CorrectArgs:
            Bet = random.sample(func.VsBets, 1)
            embed = discord.Embed(title="Vs Bet Started!",
                                  description="If one of you wins the bet, the one that won it wins. If both of you "
                                              "lose "
                                              ", it's a draw. If both of you win, it's a draw. But VS Bets are not "
                                              "always... VS.")
            embed.add_field(name=str(ctx.author.name) + "  -- VS -- " + str(msg.author.name), value="\u200b",
                            inline=False)
            embed.add_field(name=str(Bet[0]['BetText']), value="Fight for glory in this bet!", inline=True)
            if Bet[0]['BetDifficulty'] == 'Tag Team':
                embed.add_field(name="A Tag Team bet!", value="This will put a spin on things! Now you must work "
                                                              "together!", inline=True)
            BetInfo = {"DiscordAccount1": CommandUserInfo[0]['DiscordID'],
                       "DiscordAccount2": InvitedUserInfo[0]['DiscordID'],
                       "BetInfo": Bet, "MatchId": game_info['gameId'],
                       "Type": "VsBet"}
            await JC.write_to_file("OnGoingVsBets.json", BetInfo)
            await ctx.send(embed=await GenerateTip(embed))
        else:
            await ctx.send("You answered 'no' or an invalid response!")
            return
    except asyncio.TimeoutError:
        await ctx.send("Request timed out!")


@bot.command()
async def VsBetEnd(ctx):
    await CheckUpdate(ctx)
    if not await C.ChannelAllowed(ctx):
        await ctx.send("You can't use this command here.")
        return False
    if '!' in str(ctx.author.mention):
        CorrectUser = str(ctx.author.mention).replace('!', '')
    else:
        CorrectUser = ctx.author.mention
        mention = str(ctx.author.mention)
    if "!" in mention:
        mention = mention.replace("!", '')
    try:
        BetInfo = await JC.look_for_value_in_file("OnGoingVsBets.json", "DiscordAccount1", mention)
        if BetInfo[0]['Type'] != "VsBet":
            await ctx.send("This isn't the right type of bet! Use *BetEnd !")
            return
        user = await JC.look_for_value_in_file("users.json", "DiscordID", mention)
        region = await func.get_region_by_correct_acronym(user[0]['Region'])
        match = func.watcher.match.by_id(region, int(BetInfo[0]['MatchId']))
    except:
        await ctx.send("This game isn't done / You are not in a bet / You don't have an account")
        return
    user2 = await JC.look_for_value_in_file("users.json", "DiscordID", BetInfo[0]['DiscordAccount2'])
    if not user2:
        await throwErrorWrongAccount()
        return
    Id = BetInfo[0]['BetInfo']
    print(BetInfo)
    LolId1 = user[0]['LoL Account']
    LolId2 = user2[0]['LoL Account']
    LolAccount1 = func.watcher.summoner.by_puuid(region, LolId1)
    LolAccount2 = func.watcher.summoner.by_puuid(region, LolId2)
    LoLName1 = LolAccount1['name']
    LoLName2 = LolAccount2['name']
    PratId1 = await func.get_player_prat_id(match, LoLName1)
    PratId2 = await func.get_player_prat_id(match, LoLName2)
    PratInfo1 = await func.get_participant_info(match, PratId1)
    PratInfo2 = await func.get_participant_info(match, PratId2)
    print("THIS " + str(PratInfo1))
    print(match['gameDuration'])
    if int(match['gameDuration']) <= 240:
        await ctx.send("R E M A D E. This game was remade! Nothing happened.")
        await JC.pop_dict_in_list("OnGoingVsBets.json.json", BetInfo[0])
        return
    WinStatus = await BetActions.sort_bets_vs(Id[0]['BetID'], PratInfo1, PratInfo2, match)
    print(WinStatus)
    if WinStatus == 10:
        embed = discord.Embed(title=str(LoLName1).capitalize() + " WINS!", color=0xff0000)
        embed.add_field(name=str(LoLName1) + " has won the bet, defeating " + str(LoLName2) + "!", value="\u200b",
                        inline=False)
        embed.add_field(name="The Bet Was: " + str(BetInfo[0]['BetInfo'][0]['BetText']), value=str(LoLName1) + " wins!",
                        inline=True)
        await ctx.send(embed=await GenerateTip(embed))
    elif WinStatus == 2:
        embed = discord.Embed(title=str(LoLName2).capitalize() + " WINS!", color=0xff0000)
        embed.add_field(name=str(LoLName2) + " has won the bet, defeating " + str(LoLName1) + "!", value="\u200b",
                        inline=False)
        embed.add_field(name="The Bet Was: " + str(BetInfo[0]['BetInfo'][0]['BetText']), value=str(LoLName2) + " wins!",
                        inline=True)
        await ctx.send(embed=await GenerateTip(embed))
    elif WinStatus == -1:
        embed = discord.Embed(title="DRAW", color=0xff0000)
        embed.add_field(name=str(LoLName1) + " Matched " + str(LoLName2), value="\u200b", inline=False)
        embed.add_field(name="The Bet Was: " + str(BetInfo[0]['BetInfo'][0]['BetText']), value="Drawn!", inline=True)
        await ctx.send(embed=await GenerateTip(embed))
    elif WinStatus == True:
        embed = discord.Embed(title="DUO WIN!", color=0xff0000)
        embed.add_field(name=str(LoLName1) + " And " + str(LoLName2) + " Won a Tag Team Bet!", value="\u200b",
                        inline=False)
        embed.add_field(name="The Bet Was: " + str(BetInfo[0]['BetInfo'][0]['BetText']), value="Both win!", inline=True)
        await ctx.send(embed=await GenerateTip(embed))
    elif WinStatus == False:
        embed = discord.Embed(title="DUO LOSE.", color=0xff0000)
        embed.add_field(name=str(LoLName1) + " And " + str(LoLName2) + " Lost a Tag Team Bet.", value="\u200b",
                        inline=False)
        embed.add_field(name="The Bet Was: " + str(BetInfo[0]['BetInfo'][0]['BetText']), value="Both lose.",
                        inline=True)
        await ctx.send(embed=await GenerateTip(embed))
    await JC.pop_dict_in_list("OnGoingVsBets.json", BetInfo[0])


@bot.command()
async def Patreon(ctx):
    embed = discord.Embed(title="Patreon", color=0xff424d)
    embed.add_field(name="Why does the bot need Patreon?",
                    value="I don't earn money from the bot itself. The only way I can upkeep the server that keeps the bot running is Patreon. ",
                    inline=False)
    embed.add_field(name="Will LoL Bet Bot stay free?",
                    value="Of course! You will always be able to rank up and bet normally for free. That won't change. There may be some Patreon only features, but right now that's not here yet.",
                    inline=True)
    embed.add_field(name="What will I get for being a Patreon?",
                    value="You will get Patreon only posts and votes, a cool role in the Discord server, and a more direct way to offer bets and updates to me.",
                    inline=True)
    embed.add_field(name="\u200b", value="Join Patreon Here: https://www.patreon.com/lolbetbot", inline=True)
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/757147593280192592/827215073331249162/Digital-Patreon-Logo_FieryCoral.png")
    embed.set_image(
        url="https://cdn.discordapp.com/attachments/757147593280192592/827215004830400522/Digital-Patreon-Wordmark_WhiteOnFieryCoral-Sm.jpg")
    await ctx.send(embed=await GenerateTip(embed))


@bot.command()
@has_permissions(administrator=True)
async def createconfig(ctx):
    if not await JC.look_for_value_in_file("Servers.json", "Server", str(ctx.guild.id)):
        Value = {"Server": str(ctx.guild.id), "AllowedChannels": [], "AllowGifs": True}
        await JC.write_to_file("Servers.json", Value)
        embed = discord.Embed(title="Config created!",
                              description="You can currently set the channels allowed to bet in, or to allow gifs.")
        embed.add_field(name="Channels Allowed", value="All", inline=False)
        embed.add_field(name="Allow Gifs", value="True", inline=True)
        await ctx.send(embed=await GenerateTip(embed))
    else:
        await ctx.send("This server already has a config! Use *config to change it!")


@bot.command()
async def ping(ctx):
    await CheckUpdate(ctx)
    if not await C.ChannelAllowed(ctx):
        await ctx.send("You can't use this command here.")
        return False
    users = json.load(open("users.json"))
    await ctx.send(
        'Pong! Coming at you at blazing speeds of {0} seconds!'.format(round(bot.latency, 1)) + " Fun Fact: Did you"
                                                                                                " know we have "
        + str(len(users)) + " total users?")


# Shows the server's global stats!
@bot.command()
async def globalstats(ctx):
    OnGoing = json.load(open("OnGoingBets.json"))
    Globals = json.load(open("globalStats.json"))
    await CheckUpdate(ctx)
    if not await C.ChannelAllowed(ctx):
        await ctx.send("You can't use this command here.")
        return False
    users = json.load(open("users.json"))
    embed = discord.Embed(title="Global Stats", description="These are the global stats of the bot!")
    embed.add_field(name=str(len(users)) + " users!", value="\u200b", inline=False)
    embed.add_field(name="Bets Won: " + str(Globals[0]['W']) + " Bets Lost: " + str(Globals[0]['L']),
                    value="Thats " + str(Globals[0]['OverallBets']) + " overall! | "
                          + str(percentage(Globals[0]['W'], Globals[0]['L'])) + "%"
                          + " WR", inline=True)
    embed.add_field(name="Highest ever winstreak:", value=Globals[0]['HighestWinstreak'], inline=False)
    embed.add_field(name="Ongoing bets: " + str(len(OnGoing)), value="\u200b", inline=False)
    await ctx.send(embed=await GenerateTip(embed))


# Shows the latest news.
@bot.command()
async def news(ctx, *args):
    allNews = json.load(open("news.json"))
    overAllNews = len(allNews)
    try:
        if str(*args) == "":
            raise ValueError("get me out of this try statement!")
        RealArgs = int(*args)
        if RealArgs > overAllNews:
            raise ValueError("get me out of this try statement!")
        elif RealArgs <= 0:
            raise ValueError("get me out of this try statement!")
    except:
        await SendNewsMessage(ctx, allNews[overAllNews - 1], overAllNews)
    else:
        await SendNewsMessage(ctx, allNews[RealArgs - 1], RealArgs)


# Sends a news message.
async def SendNewsMessage(ctx, newsObject, newsNum):
    allNews = json.load(open("news.json"))
    OverAllNews = len(allNews)
    embed = discord.Embed(title="News",
                          description="News number " + str(newsNum) + "/" + str(OverAllNews) +
                                      ". Use news (number) to choose what news to display!",
                          color=0x4bb8fb)
    embed.add_field(name="--------------------------------------------", value="\u200b", inline=False)
    embed.add_field(name=newsObject['Title'], value=newsObject['Desc'], inline=False)
    if newsObject['Image'] != "":
        embed.set_image(url=newsObject['Image'])
    await ctx.send(embed=await GenerateTip(embed))


# Check if account is updated.
async def CheckUpdate(ctx):
    if '!' in str(ctx.author.mention):
        CorrectUser = str(ctx.author.mention).replace('!', '')
    else:
        CorrectUser = ctx.author.mention
    userinfo = await JC.look_for_value_in_file("users.json", "DiscordID", CorrectUser)
    # Winstreak update
    if not userinfo:
        return
    try:
        userinfo[0]["Winstreak"]
    except:
        await func.AddResetWinstreak(userinfo)


# Delete a user's account
@bot.command()
async def DeleteAccount(ctx):
    if '!' in str(ctx.author.mention):
        CorrectUser = str(ctx.author.mention).replace('!', '')
    else:
        CorrectUser = ctx.author.mention
    userInfo = await JC.look_for_value_in_file("users.json", "DiscordID", CorrectUser)
    await ctx.send("ARE YOU SURE? I don't disable inactive accounts! Deleting your account will WIPE ALL PROGRESS! "
                   "respond with yes or no.")

    def check(m):
        return m.content

    try:
        def check(m):
            return str(m.author.mention).replace("!", '') == CorrectUser and m.channel == ctx.channel

        msg = await bot.wait_for("message", check=check, timeout=30)
        print(msg.content)
        if msg.content.lower() == "yes" and str(msg.author.mention).replace("!", '') == CorrectUser:
            await ctx.send("Ok... Ill see you around, " + str(ctx.author.name) + ".")
            await func.DeleteUser(userInfo)
        else:
            await ctx.send("You answered 'no' or an invalid response!")
            return
    except asyncio.TimeoutError:
        await ctx.send("Request timed out!")


# Show the discord server info
@bot.command()
async def Discord(ctx):
    embed = discord.Embed(title="Discord Server", description="Want to join the discord?", color=0x7289da)
    embed.add_field(name="Join the discord here!", value="https://discord.com/invite/QTNwVRgJnj", inline=False)
    await ctx.send(embed=await GenerateTip(embed))


# Generate a tip for embeds
async def GenerateTip(embed):
    tips = json.load(open("Tips.json"))
    currentAmount = len(tips)
    print(str(currentAmount) + " Tips")
    tipchosen = random.randint(0, currentAmount) - 1
    print(tipchosen)
    embed.set_footer(text="Did you know? " + str(tips[tipchosen]['Desc']))
    return embed


# No Account in bot error.
async def throwErrorNoAccount(ctx):
    await ctx.send(
        "Some kind of error occurred. Do you have an account? If you do than this is on my end. Sorry! -> "
        "File users.json may be corrupted!")


# Special error where the JSON file has wrong details. Hopefully no one ever sees this; If this gets sent something
# has gone VERY wrong.
async def throwErrorWrongAccount(ctx):
    await ctx.send("https://cdn.discordapp.com/attachments/811654302443634760/812670670579564544/maxresdefault.jpg")
    await ctx.send(
        "You just made me very confused. WTF happened? Please send me a report of this! -> Account in "
        "JSON file doesn't exist!")


def percentage(part, whole):
    try:
        return round(part / (part + whole) * 100, 0)
    except:
        return "N/A"


bot.run(TOKEN)
