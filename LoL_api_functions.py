import random

from riotwatcher import LolWatcher, ApiError
import time
import urllib
import JSON_controls as JC
import json
from numpy.random import choice

api_key = "RIOTTOKEN"
watcher = LolWatcher(api_key)
# current version
with urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json") as url:
    current_version = JC.json.loads(url.read().decode())[0]
    print(current_version)

# get champ list
with urllib.request.urlopen(
        "https://ddragon.leagueoflegends.com/cdn/" + str(current_version) + "/data/en_US/champion.json") as url:
    champ_list = JC.json.loads(url.read().decode())

# Bet list.
VsBets = json.load(open("VsBets.json"))
AllBets = json.load(open("EasyBets.json"))
EasyBets = json.load(open(("EasyBets.json")))
MediumBets = json.load(open(("MedBets.json")))
HardBets = json.load(open(("HardBets.json")))
InsaneBets = json.load(open(("InsaneBets.json")))
# List of current difficulties
Difficulties = ['Easy', 'Medium', 'Hard', 'Insane']

# The rank ladder.
RankLadder = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']


# theres probably a better way to do this boys, but i think this function is unused.
async def look_by_name_in_all_regions(*args):
    try:
        watcher.summoner.by_name("EUN1", *args)
    except:
        try:
            watcher.summoner.by_name("BR1", *args)
        except:
            try:
                watcher.summoner.by_name("LA1", *args)
            except:
                try:
                    watcher.summoner.by_name("LA2", *args)
                except:
                    try:
                        watcher.summoner.by_name("NA1", *args)
                    except:
                        try:
                            watcher.summoner.by_name("OC1", *args)
                        except:
                            try:
                                watcher.summoner.by_name("RU1", *args)
                            except:
                                try:
                                    watcher.summoner.by_name("JP1", *args)
                                except:
                                    raise ValueError("Region doesn't exist!")
                                else:
                                    return "JP"
                            else:
                                return "RU"
                        else:
                            return "OCE"
                    else:
                        return "NA"
                else:
                    return "LA2"
            else:
                return "LA1"
        else:
            return "BR1"
    else:
        return "EUN1"


# gets summoner by info, returns error if not found
async def look_for_summoner(region, name):
    try:
        return watcher.summoner.by_puuid(await get_region_by_correct_acronym(region), str(name))
    except:
        raise ValueError("Didn't find summoner!")


# gets summoner by name, dont use this unless you cant find uuid.
async def look_for_summoner_by_name(region, name):
    try:
        return watcher.summoner.by_name(await get_region_by_correct_acronym(region), name)
    except:
        raise ValueError("Didn't find summoner!")


# gets ID, returns info about champ.
async def look_for_champ(key):
    return next((x for x in champ_list['data'].values() if x['key'] == key), "Invalid champ")


# get region by its Riot API name - EUNE is EUN1
async def get_region_by_correct_acronym(region):
    switcher = {
        'BR': 'BR1',
        'EUNE': 'EUN1',
        'EUW': 'EUW1',
        'LAN': 'LA1',
        'LAS': 'LA2',
        'NA': 'NA1',
        'OCE': 'OC1',
        'RU': 'RU1',
        'TR': 'TR1',
        'JP': 'JP1'
    }
    return switcher.get(region, "invalid server!")


# get rank image based on text
async def get_rank_image(rank):
    switcher = {
        'IRON': 'https://cdn.discordapp.com/attachments/811654302443634760/811940293565743184/Emblem_Iron.png',
        'BRONZE': 'https://cdn.discordapp.com/attachments/811654302443634760/811940287878135819/Emblem_Bronze.png',
        'SILVER': 'https://cdn.discordapp.com/attachments/811654302443634760/811940288418807808/Emblem_Silver.png',
        'GOLD': 'https://cdn.discordapp.com/attachments/811654302443634760/811940294043369482/Emblem_Gold.png',
        'PLATINUM': 'https://cdn.discordapp.com/attachments/811654302443634760/811940289321107466/Emblem_Platinum.png',
        'DIAMOND': 'https://cdn.discordapp.com/attachments/811654302443634760/811940295410581544/Emblem_Diamond.png',
        'MASTER': 'https://cdn.discordapp.com/attachments/811654302443634760/811940286908989440/Emblem_Master.png',
        'GRANDMASTER': 'https://cdn.discordapp.com/attachments/811654302443634760/811940294886948884/Emblem_Grandmaster.png',
        'CHALLENGER': 'https://cdn.discordapp.com/attachments/811654302443634760/811940295703920670/Emblem_Challenger.png',
    }
    return switcher.get(rank,
                        "https://cdn.discordapp.com/attachments/811654302443634760/812297067107057704/Unranked.png")


# get ongoing match info. Returns 'false' if not in match.
async def game_info(region, profile):
    print(profile)
    try:
        print(watcher.spectator.by_summoner(region, profile['id']))
    except:
        return False


# Is gameLength returning you some useless shit? Use this.
async def get_match_length(match_epoch_time):
    current_time = int(time.time())
    return current_time - match_epoch_time


# get list of all participants FOR AFTER MATCH!!
def get_participants_for_further_pulls_after(match):
    """ This function takes a riot api 'match' and returns only selected
        participant information. You may add to the returned information
        if you want.
        The return value is a list of dictionaries, one for each
        participant in the match. """
    participants = [{} for i in range(len(match['participants']))]
    for i, p in enumerate(match['participants']):
        participants[i]['summonerId'] = match['participantIdentities'][p['participantId'] - 1]
    return participants


# get list of all participants FOR IN MATCH!!
def get_participants_for_further_pulls_in(match):
    """ This function takes a riot api 'match' and returns only selected
        participant information. You may add to the returned information
        if you want.
        The return value is a list of dictionaries, one for each
        participant in the match. """
    participants = [{} for i in range(len(match['participants']))]
    for i, p in enumerate(match['participants']):
        participants[i] = match['participants']
    return participants


# return champ info from key
def champ_info(key):
    return next((x for x in champ_list['data'].values() if x['key'] == str(key)), "Invalid champ")


# get participant id for player
async def get_player_prat_id(match, name):
    for i in range(10):
        if str(name) in str(get_participants_for_further_pulls_after(match)[i]):
            return i
    raise ValueError("Didn't find summoner in this game!")


# get info post match of a participant
async def get_participant_info(match, par):
    try:
        return match['participants'][par]['stats']
    except:
        raise ValueError("Not valid participant stats!")


# get k/d/a from participant info // lol useless btw
async def get_kda_from_participant(par):
    try:
        return str(par['kills']) + "/" + str(par['deaths']) + "/" + str(par['assists'])
    except:
        raise ValueError("Not valid participant stats!")


# how much BP to give
async def CalculateBP(user, LolAccount, difficulty):
    CurrentBP = 15
    if difficulty == 'Easy':
        CurrentBP -= 2
    elif difficulty == 'Medium':
        CurrentBP += 2
    elif difficulty == 'Hard':
        CurrentBP += 5
    elif difficulty == 'Insane':
        CurrentBP += 20
    RankLadder = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
    BetRankIndex = RankLadder.index(user[0]['Rank'])
    RealRankIndex = RankLadder.index(LolAccount[0]['tier'])
    print(RealRankIndex)
    if BetRankIndex > RealRankIndex:
        CurrentBP -= BetRankIndex - RealRankIndex
    elif BetRankIndex < RealRankIndex:
        CurrentBP += (RealRankIndex - BetRankIndex) * 4
    if LolAccount[0]['hotStreak']:
        CurrentBP += 7
    if BetRankIndex < 4:
        CurrentBP += 10
    elif BetRankIndex < 6:
        CurrentBP += 5
    if user[0]['Winstreak'] > 1:
        CurrentBP += user[0]['Winstreak'] * 2
    return CurrentBP


# add win to player
async def AddWin(user):
    WinCount = user[0]["W"] + 1
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": user[0]['BP'], "W": WinCount, "L": user[0]['L'],
               "PROMO": user[0]['PROMO'], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)


# add lose to player
async def AddLose(user):
    GlobalStats = json.load(open("globalStats.json"))
    LoseCount = user[0]["L"] + 1
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": user[0]['BP'], "W": user[0]['W'], "L": LoseCount,
               "PROMO": user[0]['PROMO'], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)
    await JC.pop_dict_in_list("globalStats.json", GlobalStats[0])
    NewGlobalList = {"W": GlobalStats[0]['W'], "L": GlobalStats[0]['L'] + 1,
                     "OverallBets": GlobalStats[0]['OverallBets'] + 1,
                     "HighestWinstreak": GlobalStats[0]['HighestWinstreak']}
    await JC.write_to_file("globalStats.json", NewGlobalList)


# Add BP to user
async def AddBP(user, amt):
    BPCount = user[0]["BP"] + amt
    print(user[0])
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": BPCount, "W": user[0]['W'], "L": user[0]['L'],
               "PROMO": user[0]['PROMO'], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)


async def AddBPAndWin(user, amt):
    GlobalStats = json.load(open("globalStats.json"))
    print(GlobalStats)
    BPCount = user[0]["BP"] + amt
    WinCount = user[0]["W"] + 1
    print("This: " + str(user[0]))
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": BPCount, "W": WinCount, "L": user[0]['L'],
               "PROMO": user[0]['PROMO'], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak']}
    print("THIS 2 " + str(GlobalStats))
    await JC.write_to_file("users.json", NewList)
    await JC.pop_dict_in_list("globalStats.json", GlobalStats[0])
    NewGlobalList = {"W": GlobalStats[0]['W'] + 1, "L": GlobalStats[0]['L'],
                     "OverallBets": GlobalStats[0]['OverallBets'] + 1,
                     "HighestWinstreak": GlobalStats[0]['HighestWinstreak']}
    await JC.write_to_file("globalStats.json", NewGlobalList)
    print(GlobalStats)


async def LoseBPAndLoss(user, amt):
    GlobalStats = json.load(open("globalStats.json"))
    BPCount = user[0]["BP"] - amt
    LoseCount = user[0]["L"] + 1
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": BPCount, "W": user[0]['W'], "L": LoseCount,
               "PROMO": user[0]['PROMO'], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)
    await JC.pop_dict_in_list("globalStats.json", GlobalStats[0])
    NewGlobalList = {"W": GlobalStats[0]['W'], "L": GlobalStats[0]['L'] + 1,
                     "OverallBets": GlobalStats[0]['OverallBets'] + 1,
                     "HighestWinstreak": GlobalStats[0]['HighestWinstreak']}
    await JC.write_to_file("globalStats.json", NewGlobalList)


# Start promos of user
async def StartPromos(user):
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": user[0]['BP'], "W": user[0]['W'], "L": user[0]['L'],
               "PROMO": [0, 0, 0], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)


# Add win to promos
async def AddWinToPromos(user):
    print(user)
    GlobalStats = json.load(open("globalStats.json"))
    Promos = user[0]['PROMO']
    Wins = user[0]['W'] + 1
    updatedResults = []
    if Promos[0] == 0:
        updatedResults = ['W', 0, 0]
    elif Promos[1] == 0:
        updatedResults = [Promos[0], "W", 0]
    elif Promos[2] == 0:
        updatedResults = [Promos[0], Promos[1], "W"]
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": user[0]['BP'], "W": Wins, "L": user[0]['L'],
               "PROMO": updatedResults, "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)
    await JC.pop_dict_in_list("globalStats.json", GlobalStats[0])
    NewGlobalList = {"W": GlobalStats[0]['W'] + 1, "L": GlobalStats[0]['L'],
                     "OverallBets": GlobalStats[0]['OverallBets'] + 1,
                     "HighestWinstreak": GlobalStats[0]['HighestWinstreak']}
    await JC.write_to_file("globalStats.json", NewGlobalList)


# Add loss to promos
async def AddLossToPromos(user):
    GlobalStats = json.load(open("globalStats.json"))
    Promos = user[0]['PROMO']
    Losses = user[0]['L'] + 1
    updatedResults = []
    if Promos[0] == 0:
        updatedResults = ['L', 0, 0]
    elif Promos[1] == 0:
        updatedResults = [Promos[0], "L", 0]
    elif Promos[2] == 0:
        updatedResults = [Promos[0], Promos[1], "L"]
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": user[0]['BP'], "W": user[0]['W'], "L": Losses,
               "PROMO": updatedResults, "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)
    await JC.pop_dict_in_list("globalStats.json", GlobalStats[0])
    NewGlobalList = {"W": GlobalStats[0]['W'] + 1, "L": GlobalStats[0]['L'],
                     "OverallBets": GlobalStats[0]['OverallBets'] + 1,
                     "HighestWinstreak": GlobalStats[0]['HighestWinstreak']}
    await JC.write_to_file("globalStats.json", NewGlobalList)


# Set BP of user
async def SetBP(user, amt):
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": amt, "W": user[0]['W'], "L": user[0]['L'],
               "PROMO": user[0]['PROMO'], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)


# Stop Promos of user
async def StopPromos(user):
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": user[0]['BP'], "W": user[0]['W'], "L": user[0]['L'],
               "PROMO": False, "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)


# Change Rank Of Player.
async def ChangeRank(user, rank):
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": rank, "BP": user[0]['BP'], "W": user[0]['W'], "L": user[0]['L'],
               "PROMO": user[0]['PROMO'], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)


# Choose a bet for a player.
async def ChooseBet(rank, promos):
    global EasyBets, MediumBets, HardBets, InsaneBets, RankLadder
    Bet1 = "this is a bug"
    Bet2 = "this is a bug"
    Bet3 = "this is a bug"
    RankIndex = RankLadder.index(rank)
    print(RankIndex)
    if not promos:
        if RankIndex < 4:
            Bet1, Bet2 = random.sample(EasyBets, 2)
            Bet3 = random.sample(MediumBets, 1)[0]
        elif RankIndex < 6:
            Bet1 = random.sample(EasyBets, 1)
            Bet2 = random.sample(MediumBets, 1)[0]
            Bet3 = "this is a bug"
            if random.randrange(0, 2) == 0:
                Bet3 = random.sample(HardBets, 1)[0]
            else:
                Bet3 = random.sample(InsaneBets, 1)[0]
        else:
            Bet1 = random.sample(MediumBets, 1)[0]
            Bet2 = random.sample(HardBets, 1)[0]
            Bet3 = random.sample(InsaneBets, 1)[0]
    else:
        if RankIndex < 4:
            Bet1, Bet2, Bet3 = random.sample(EasyBets, 3)
        elif RankIndex < 6:
            Bet1, Bet2, Bet3 = random.sample(MediumBets, 3)
        else:
            Bet1, Bet2, Bet3 = random.sample(HardBets, 3)
    return Bet1, Bet2, Bet3


async def GetRewards(Difficulty, Rank, user):
    DifficultyIndex = Difficulties.index(Difficulty) + 1
    RankIndex = RankLadder.index(Rank) + 1
    print("This 2: " + str(RankIndex) + " " + str(Rank))
    DropRate = DifficultyIndex * 10 + RankIndex * 10
    if DropRate > 70:
        DropRate = 70
    options = [True, False]
    prob = [DropRate / 100, (100 - DropRate) / 100]
    print("DropRate = " + str(DropRate) + " True Prob: " + str(DropRate / 100) + " False Prob: " + str((100 - DropRate)
                                                                                                       / 100))
    if choice(options, p=prob):
        await GiveRewards("Rerolls", user)
        return True
    return False


async def RemoveReroll(user):
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": user[0]['BP'], "W": user[0]['W'], "L": user[0]['L'],
               "PROMO": user[0]['PROMO'], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'] - 1,
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)


async def GiveRewards(rewards, user):
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": user[0]['BP'], "W": user[0]['W'], "L": user[0]['L'],
               "PROMO": user[0]['PROMO'], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'] + 1,
               "Winstreak": user[0]['Winstreak']}
    await JC.write_to_file("users.json", NewList)


# Add (or reset) Winstreak
async def AddResetWinstreak(user):
    await JC.pop_dict_in_list("users.json", user[0])
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": user[0]['BP'], "W": user[0]['W'], "L": user[0]['L'],
               "PROMO": user[0]['PROMO'], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'], "Winstreak": 0}
    await JC.write_to_file("users.json", NewList)


# Add 1 to winstreak of user
async def AddWinstreakWin(user):
    await JC.pop_dict_in_list("users.json", user[0])
    print("WINSTREAK CHANGE")
    NewList = {"DiscordID": user[0]['DiscordID'], "LoL Account": user[0]['LoL Account'], "Region": user[0]['Region'],
               "Points": user[0]['Points'],
               "Rank": user[0]['Rank'], "BP": user[0]['BP'], "W": user[0]['W'], "L": user[0]['L'],
               "PROMO": user[0]['PROMO'], "Name": user[0]['Name'], "Rerolls": user[0]['Rerolls'],
               "Winstreak": user[0]['Winstreak'] + 1}
    await JC.write_to_file("users.json", NewList)


# change HighestWinstreak to updated one
async def ChangeHighestWinstreak(stats, newWinstreak):
    await JC.pop_dict_in_list("globalStats.json", stats[0])
    NewStats = {"W": stats[0]['W'], "L": stats[0]['L'], "OverallBets": stats[0]['OverallBets'],
                "HighestWinstreak": newWinstreak}
    await JC.write_to_file("globalStats.json", NewStats)


# Delete a user's account.
async def DeleteUser(user):
    await JC.pop_dict_in_list("users.json", user[0])


# Calculate GLOBAL (ELO) points with a rank and BP
async def CalculateGlobal(rank, BP):
    RankIndex = RankLadder.index(rank)
    RankPoints = RankIndex * 100
    return RankPoints + BP
