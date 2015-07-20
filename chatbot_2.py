#!/usr/bin/env python3


"""
Example Client for irclib

Copyright (C) 2014, 2015 Tyler Philbrick
All Rights Reserved
For license information, see COPYING
"""

from irclib.baseclient import BaseClient
import forums
import string
import plotdata.plotmap as plotmap
import mcuuid
#import json
#import urllib.request

class MyIRC(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmdchar = ","
        self.mcserverlist = ['OREBuild', 'ORESchool', 'ORESurvival']
        self.mcplayerlist = {}
        self.mcplayerdata = {}
       
    def handle_JOIN(self, line):
        if self.nick == line.nick:
            self.printing = True
            self.getplayerlist()


    def mc_handle_MCPLAYERLIST(self, line, *args):
        if args[0] == 0:
            self.mcplayerlist[line.nick] = []
        else:
            self.mcplayerlist[line.nick] = args[1]

    def mc_handle_PLAYERLEFT(self, line, *args):
        if args[0] in self.mcplayerlist[line.nick]:
            self.mcplayerlist[line.nick].remove(args[0])
    
    def mc_handle_PLAYERJOINED(self, line, *args):
        #print('adding %s to server %s' % (line.mcparams, line.nick,))
        if not args[0] in self.mcplayerlist[line.nick]:
            self.mcplayerlist[line.nick].append(args[0])

    def cmd_HELP(self, line, *args):
        self.respond(line, '{}list: Gives list of players on all servers'.format(self.cmdchar))
        self.respond(line, '{}search: Searches forums'.format(self.cmdchar))
        self.respond(line, 'Syntax: {}search <search term>'.format(self.cmdchar))
        self.respond(line, '{}plot: gets you the plotdata of old build'.format(self.cmdchar))
        self.respond(line, 'Syntax: {c}plot <player name> OR {c}plot <x coords> <y coords>'.format(c = self.cmdchar))

    def cmd_TEST(self, line, *args):
        self.respond(line, 'Werkin\'')

    def cmd_REFRESHLIST(self, line, *args):
        self.respond(line, "Refreshing player list")
        self.getplayerlist()
    
            
    def cmd_LIST(self, line, *args):
        if self.mcplayerlist is None:
            return
        self.respond(line, 'Player list:')
        for mcserver in self.mcplayerlist:
            #print(self.mcplayerlist[mcserver])
            send = '{}: {}'.format(mcserver, ', '.join(self.mcplayerlist[mcserver]))
            self.respond(line, send)

    def cmd_SEARCH(self, line, *args):
        print('executing search command')
        if len(args[1]) < 1:
            self.respond('Please put in something to search.')
            return 
        searchTerm = args[1][1]
        searchParams = self.searchParams(searchTerm)
        results = forum.search(searchParams)
        if results is None:
            self.respond(line, 'Cooldown period has not yet expired. Please wait.')
            return
        self.mcplayerdata[args[0]] = {'searchResults': results[0:5]}
        i=1
        for result in results[0:5]:
            self.respond(line, '{}: {}'.format(i, result[1]))
            i += 1
        self.respond(line, 'Use the {}result command to view the links.'.format(self.cmdchar))

    def cmd_RESULT(self, line, *args):
        try:
            data = self.mcplayerdata[line.params[0]]['searchResults']
        except KeyError:
            self.respond(line, 'No data found. Before using this command, please use the {}search command.'.format(self.cmdchar))
            return
        s_number = args[1][1][0]
        if s_number in string.digits:
            index = int(s_number)-1
            if 0 <= index <= 4:
                try:
                    self.respond(line, 'http://{}/{}'.format(forum.ip, data[index][0]))
                    return
                except IndexError:
                    self.respond(line, 'No data found.')
                    return
        self.respond(line, 'Please enter a number between 1 and 5')

    def cmd_TIME(self, line, *args):
        self.respond(line, "It's time to go fuck yourself.")

    def cmd_PLOT(self, line, *args):
        i = len(args[1])
        if i == 1:
            self.respond(line, 'Please input a nickname or plot coordinates')
        elif i == 2:
            playerName = args[1][1]
            plotList = plotdb.getPlotsByName(playerName)
            if len(plotList) == 0:
                uuid = mcuuid.getUuidByCurrentName(playerName)
                print(uuid)
                if uuid is None:
                    self.respond(line, 'No player found')
                    return
                else:
                    plotList = plotdb.getPlotsByUuid(uuid)
            if len(plotList) == 0:
                self.respond(line, 'No plots found with owner {}'.format(playerName))
            else:
                self.respond(line, 'Plots owned by {}'.format(playerName))
                for plot in plotList:
                    xcoord = plot[0] * 256 + 128
                    ycoord = plot[1] * 256 + 128
                    self.respond(line, 'X:{}, Y:{}, coordinates: {}, {}'.format(plot[0], plot[1], xcoord, ycoord))
        elif i == 3:
            try:
                xcoord = int(words[1])
                ycoord = int(words[2])
            except ValueError:
                self.respond(line, 'Please input valid coordinates.')
                return
            owner = plotdb.getOwnerByPlayerCoords(xcoord, ycoord)
            if owner is None:
                self.respond(line, 'Plot has no owner.')
            else:
                self.respond(line, 'Plot owned by {}'.format(owner[0]))

            

            

    #def mc_cmd_UUID(self, line):
    #    param = line.mcparams[-1].split()[1]
    #    self.mcprivmsg(line, self.getUuid(param))


        
    def getplayerlist(self):
        try:
            #print(self.mcserverlist)
            for mcserver in self.mcserverlist:
                #print(mcserver)
                self.privmsg(".list", target = mcserver)
                self.mcplayerlist[mcserver] = []
        except NameError:
            pass

    def searchParams(self, searchTerm):
        return {'submit':      'Search',
                  'sortordr':    'desc',
                  'sortby':      'lastpost',
                  'showresults': 'threads',
                  'postthread':  '1',
                  'postdate':    '0',
                  'pddir':       '1',
                  'keywords': searchTerm,
                  'forum[]': '10',
                  'findthreadst': '1',
                  'action': 'do_search' }
        

if __name__ == "__main__":
    print("launching chatbot v2")
    forum = forums.open('forum.openredstone.org', ssl = True)
    plotdb = plotmap.plotmap('plot map.sqlite')
    plotdb.connect()
    #forum.open()
    irc = MyIRC(
        ("irc.openredstone.org", 6667),
        ("usern", "hostn", "realn"),
        "BotteryV2",
        "#openredstone",
        printing = True
    )

    irc.run()
