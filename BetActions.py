import LoL_api_functions as func


# Launch bet function
async def sort_bets(ID, PlayerDetails, match):
    switcher = {
        '0': await Bet0(PlayerDetails, match),
        '1': await Bet1(PlayerDetails, match),
        '2': await Bet2(PlayerDetails, match),
        '4': await Bet4(PlayerDetails, match),
        '5': await Bet5(PlayerDetails, match),
        '6': await Bet6(PlayerDetails, match),
        '7': await Bet7(PlayerDetails, match),
        '8': await Bet8(PlayerDetails, match),
        '10': await Bet10(PlayerDetails, match),
        '11': await Bet11(PlayerDetails, match),
        '12': await Bet12(PlayerDetails, match),
        #'13': await Bet13(PlayerDetails, match),
        '14': await Bet14(PlayerDetails, match),
    }
    result = switcher.get(str(ID))
    return result


# Launch vs bets.
async def sort_bets_vs(ID, PlayerDetails1, PlayerDetails2, match):
    switcher = {
        'Vs1': await Vs1(PlayerDetails1, PlayerDetails2, match),
        'Vs2': await Vs2(PlayerDetails1, PlayerDetails2, match),
        'Vs3': await Vs3(PlayerDetails1, PlayerDetails2, match),
        'Vs4': await Vs4(PlayerDetails1, PlayerDetails2, match),
        'Vs5': await Vs5(PlayerDetails1, PlayerDetails2, match),
        'Vs6': await Vs6(PlayerDetails1, PlayerDetails2, match),
        'Vs7': await Vs7(PlayerDetails1, PlayerDetails2, match),
        'Vs8': await Vs8(PlayerDetails1, PlayerDetails2, match),
    }
    result = switcher.get(str(ID))
    return result


async def Bet0(PlayerDetails, match):
    return PlayerDetails['win']


async def Bet1(PlayerDetails, match):
    if (PlayerDetails['firstBloodKill'] or PlayerDetails['firstBloodAssist']) and PlayerDetails['win']:
        return True
    else:
        return False


async def Bet2(PlayerDetails, match):
    TeamId = 0
    OtherTeam = 0
    if PlayerDetails['participantId'] < 5:
        TeamId = 100
        OtherTeam = 200
    else:
        TeamId = 200
        OtherTeam = 100
    DrakesAlly = list(filter(lambda x: x['teamId'] == TeamId, match['teams']))[0]['dragonKills']
    DrakesEnemy = list(filter(lambda x: x['teamId'] == OtherTeam, match['teams']))[0]['dragonKills']
    if DrakesAlly >= DrakesEnemy:
        if PlayerDetails['win']:
            return True
        else:
            return False
    else:
        return False


async def Bet3(PlayerDetails, match):
    if PlayerDetails['tripleKills'] >= 1 or PlayerDetails['quadraKills'] >= 1 or PlayerDetails['pentaKills'] >= 1:
        return True
    else:
        return False


async def Bet4(PlayerDetails, match):
    list_of_damage = []
    TeamWon = await Bet0(PlayerDetails, match)
    for i in range(10):
        prat = await func.get_participant_info(match, i)
        if prat['win'] == TeamWon:
            list_of_damage.append(int(prat['totalDamageDealtToChampions']))
    print(sorted(list_of_damage, reverse=True))
    if (sorted(list_of_damage, reverse=True)[0] == int(PlayerDetails['totalDamageDealtToChampions']) and PlayerDetails[
        'win']) \
            or sorted(list_of_damage, reverse=True)[1] == int(
        PlayerDetails['totalDamageDealtToChampions']) and PlayerDetails['win']:
        return True
    else:
        print(str(sorted(list_of_damage, reverse=True)[0]) + "," + str(
            sorted(list_of_damage, reverse=True)[1]) + " " + str(
            int(PlayerDetails['totalDamageDealtToChampions'])) + " " + str(PlayerDetails['win']))
        return False


async def Bet5(PlayerDetails, match):
    TeamId = 0
    OtherTeam = 0
    if PlayerDetails['participantId'] < 5:
        TeamId = 100
        OtherTeam = 200
    else:
        TeamId = 200
        OtherTeam = 100
    RiftAlly = list(filter(lambda x: x['teamId'] == TeamId, match['teams']))[0]['riftHeraldKills']
    RiftEnemy = list(filter(lambda x: x['teamId'] == OtherTeam, match['teams']))[0]['riftHeraldKills']
    if RiftAlly >= RiftEnemy:
        if PlayerDetails['win']:
            return True
        else:
            return False
    else:
        return False


async def Bet6(PlayerDetails, match):
    TeamId = 0
    OtherTeam = 0
    if PlayerDetails['participantId'] < 5:
        TeamId = 100
        OtherTeam = 200
    else:
        TeamId = 200
        OtherTeam = 100
    DrakesAlly = list(filter(lambda x: x['teamId'] == TeamId, match['teams']))[0]['dragonKills']
    DrakesEnemy = list(filter(lambda x: x['teamId'] == OtherTeam, match['teams']))[0]['dragonKills']
    RiftAlly = list(filter(lambda x: x['teamId'] == TeamId, match['teams']))[0]['riftHeraldKills']
    RiftEnemy = list(filter(lambda x: x['teamId'] == OtherTeam, match['teams']))[0]['riftHeraldKills']
    if RiftAlly >= RiftEnemy and DrakesAlly >= DrakesEnemy:
        if PlayerDetails['win']:
            return True
        else:
            return False
    else:
        return False


async def Bet7(PlayerDetails, match):
    if PlayerDetails['timeCCingOthers'] >= 40:
        return True
    else:
        return False


async def Bet8(PlayerDetails, match):
    if PlayerDetails['largestCriticalStrike'] >= 1000:
        return True
    else:
        return False


async def Bet10(PlayerDetails, match):
    if round(int(PlayerDetails['totalMinionsKilled']) / 60) >= 8:
        return True
    else:
        return False


async def Bet11(PlayerDetails, match):
    if PlayerDetails['kills'] >= 10:
        return True
    else:
        return False


async def Bet12(PlayerDetails, match):
    VisionScore = PlayerDetails['visionScore']
    GameTime = int(match['gameDuration'] / 60)
    if int(VisionScore * 1.5) >= GameTime and PlayerDetails['assists'] >= 10:
        return True
    else:
        return False


#async def Bet13(PlayerDetails, match):
#    if PlayerDetails['firstTowerKill'] or PlayerDetails['firstTowerAssist']:
#        return True
#    else:
#        return False


async def Bet14(PlayerDetails, match):
    if PlayerDetails['inhibitorKills'] >= 1:
        return True
    else:
        return False


async def Vs1(PlayerDetails1, PlayerDetails2, match):
    if PlayerDetails1['firstBloodKill']:
        return 10
    elif PlayerDetails2['firstBloodKill']:
        return 2
    else:
        return -1


async def Vs2(PlayerDetails1, PlayerDetails2, match):
    if PlayerDetails1['pentaKills'] >= 1 and PlayerDetails2['pentaKills'] == 0:
        return 10
    elif PlayerDetails2['pentaKills'] >= 1:
        return 2
    else:
        return -1


async def Vs3(PlayerDetails1, PlayerDetails2, match):
    DamageP1 = PlayerDetails1['totalDamageDealtToChampions']
    DamageP2 = PlayerDetails2['totalDamageDealtToChampions']
    if DamageP1 > DamageP2:
        return 10
    elif DamageP2 < DamageP1:
        return 2
    else:
        return -1


async def Vs4(PlayerDetails1, PlayerDetails2, match):
    CC1 = PlayerDetails1['timeCCingOthers']
    CC2 = PlayerDetails2['timeCCingOthers']
    if CC1 > CC2:
        return 10
    elif CC2 < CC1:
        return 2
    else:
        return -1


async def Vs5(PlayerDetails1, PlayerDetails2, match):
    Kills1 = PlayerDetails1['kills']
    Kills2 = PlayerDetails2['kills']
    print("Player1 " + str(Kills1) + " Player2 " + str(Kills2))
    if Kills1 > Kills2:
        return 10
    elif Kills2 > Kills1:
        return 2
    else:
        return -1


async def Vs6(PlayerDetails1, PlayerDetails2, match):
    TakeDowns1 = PlayerDetails1['assists'] + PlayerDetails1['kills']
    TakeDowns2 = PlayerDetails2['assists'] + PlayerDetails2['kills']
    if TakeDowns1 + TakeDowns2 >= 40:
        return True
    else:
        return False


async def Vs7(PlayerDetails1, PlayerDetails2, match):
    Towers1 = PlayerDetails1['turretKills']
    Towers2 = PlayerDetails2['turretKills']
    if Towers1 + Towers2 >= 5:
        return True
    else:
        return False


async def Vs8(PlayerDetails1, PlayerDetails2, match):
    CC1 = PlayerDetails1['timeCCingOthers']
    CC2 = PlayerDetails2['timeCCingOthers']
    if CC1 + CC2 >= 40:
        return True
    else:
        return False


async def Error():
    raise ValueError("Unknown Bet!")
