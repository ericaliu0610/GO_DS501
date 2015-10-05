__author__ = 'jarfy'
import goldsberry
import pandas as pd
from goldsberry.player._Player import *

class Get_Data(object):
    def __init__(self, from_year, to_year):
        self.from_year = from_year
        self.to_year = to_year

    #get player from 2000 to 2015
    players = dict()
    players_lst = []
    year_lst = []
    for year in range(2000, 2016):
        players_of_every_year = pd.DataFrame(goldsberry.PlayerList(year))
        # print str(year)+" "+ str(len(players_of_every_year))
        year_lst.append(players_of_every_year)
        all_players = pd.concat(year_lst)

    # print len(all_players)

    # print all_players
    for i in range(0, len(all_players.index)):
        players = dict()
        players.update(all_players.irow(i))
        players_lst.append(players)
    # print players_lst[1:4]
    # print "player_lst------------------------"

    #delete duplicate and find potential 3 grade players
    global players_distinct
    players_distinct = {}
    for i in range(0, len(players_lst)):
        if int(players_lst[i]["FROM_YEAR"]) > 2014 or int(players_lst[i]["TO_YEAR"]) - int(players_lst[i]["FROM_YEAR"])<3:
            continue
        players_distinct[players_lst[i]["PERSON_ID"]] = players_lst[i]

    # print players_distinct
    # print "players_distinct-----------------------"

    def get_player_distinct(self):    #return all distinct players information
        return players_distinct

    global all_id
    all_id = players_distinct.keys()
    # print all_id
    # print "all_id-----------------------"


    #test clear
    # print players_distinct
    # print len(players_distinct)
    # a = set(players_distinct)
    # print len(a)
    # print a

    #get everyone stats based on ID and 3rd year stats
    global stats_ls
    stats_ls = {}
    player_stats = {}  #collect stats of every player in every season
    for each_player in range(0, len(all_id)):
        player = career_stats(all_id[each_player])
        season_stats = player.season_totals_regular()
        year_3rd = {}
        for each_stats in range(0, len(season_stats)):
            if int(season_stats[each_stats]["SEASON_ID"][0:4]) \
                - int(players_distinct[all_id[each_player]]["FROM_YEAR"]) == 3:
                stats_ls[all_id[each_player]] = season_stats[each_stats]

    # print stats_ls
    # print "stats_ls--------------------"

    def get_stats_ls(self):
        return stats_ls

    #calculate Player impact estimate
    #calculation
    #(PTS + REB + AST + STL + BLK - (FGA - FGM) - (FTA - FTM) - PF)/MIN
    stats_key = stats_ls.keys()
    global player_epr #key = ID, value = epr
    player_epr = {}
    for i in range(0, len(stats_ls)):
        key = stats_key[i]
        player_epr[key] =float((stats_ls[key]["PTS"] + stats_ls[key]["REB"]\
            +stats_ls[key]["AST"] + stats_ls[key]["STL"] + stats_ls[key]["BLK"]\
            - (stats_ls[key]["FGA"] - stats_ls[key]["FGM"])\
            - (stats_ls[key]["FTA"] - stats_ls[key]["FTM"]) - stats_ls[key]["PF"])\
            / stats_ls[key]["GP"])

    # print player_epr
    # print "player_epr------------------------"




    def get_player_distinct(self):    #return all distinct players information
        return players_distinct

    def get_all_id(self):          #return all players ID
        return all_id

    def get_epr(self):              #return epr
        return player_epr

print "---------------test----------------"
