# Zachary Taylor & Steven Proctor
# WumpusAgent.py
# Feb 11, 2019
# AI 2019, WumpusWorld
# The Wumpinator Agent. Gets the gold (almost) every time!
from collections import defaultdict as dd
import sys
c=dd()#our coordinates c['k'][0] is x
gold = False
prevMvs = []
walls=''
last = 'N'
wumpusMap = [['']]#wumpusMap[y][x] is a dynamic map
x=0; y=0; wType=0; nArrows=0; nWumpi=0
inv = {'N':'S','S':'N','E':'W','W':'E'}
count=0

#sets up global parameters for this game
def setParams(gameType, numArrows, numWumpi):
    global gold, prevMvs,wumpusMap,x,c,y,wType,nArrows,nWumpi,inv,walls,count
    if gameType != 1 and gameType != 2:
        print("Invalid Game Type: ", gameType)
        sys.exit()
    if numWumpi >198 or numWumpi<0: #this is the largest number the game can accept without breaking
        print("Invalid Number of Wumpi: ",numWumpi)
        sys.exit()
    if numArrows<0:
        print("Invalid Number of numArrows: ",numArrows)
        sys.exit()
    wType = gameType
    nArrows = numArrows
    nWumpi = numWumpi
    gold = False
    prevMvs = []
    last = 'N'
    wumpusMap = [['']]
    x=0; y=0;c['e']=[0,0]
    walls=''
    count=0

#gets the agent's next move given a string of percepts
def getMove(percept):
    global gold, walls, prevMvs,wumpusMap,x,c,y,wType,nArrows,nWumpi,inv,last,count
    count+=1
    if count>100000:#safety valve
        return 'C'


    dir=''
    if 'C' in percept:
        nWumpi-=1
    if 'U' in percept:
        if 'fb' not in c:
            prevMvs.pop()
        bdir = inv[last]
        if bdir == 'N' or bdir == 'S':
            wumpusMap[y] = ['U']*len(wumpusMap[0])
        else:
            for row in wumpusMap:
                row[x] = 'U'
        mapMove(bdir)
        walls += last #add the wall we bumped into to the list of walls

    if gold:
        if x==c['e'][0] and y==c['e'][1]:
            return "C"
        dir = back()
    elif 'G' in percept and 'S' not in percept:
        gold = True
        return 'G'
    elif 'S' in percept and wType==2 and nArrows>0:
        #1/3th chance to hit
        nArrows-=1
        return 'S' + last
    elif 'B' in percept or ('S' in percept and wType==1):
        if  wumpusMap[y][x] not in 'Xs':
            stationaryThreat()
    else:
        for ndir,ny,nx,nv in iterNeighbors():
            if 'p' in nv or nv=='':
                wumpusMap[ny][nx] = 's'
    if dir == '':
        dir = roam()
        if dir == "":
            prevMvs.clear()
            dir = fallback()
    wumpusMap[y][x] = 'X'
    mapMove(dir)
    last = dir

    return dir

#get the next move in a systematic sweep of all the cells on the map, returns a direction or a blank
def roam():
    global gold, walls, prevMvs,wumpusMap,x,c,y,wType,nArrows,nWumpi,inv
    dir=''
    for ndir,ny,nx,nv in iterNeighbors():
        if nv == 's':
            dir=ndir
            if 'fb' in c:
                c.pop('fb')
    if dir == '':
        dir = back()
    else:
        prevMvs.append(dir)
    return dir

#adjust the coordinates of our dynamic internal map for a given move, returns nothing
def mapMove(dir):
    global gold, prevMvs, walls,wumpusMap,x,y,c,wType,nArrows,nWumpi,inv
    if dir == 'N':
        y += 1
        if y == len(wumpusMap):
            wumpusMap.append(['']*len(wumpusMap[0]))
            if 'E' in walls:
                wumpusMap[-1][-1] = 'U'
            if 'W' in walls:
                wumpusMap[-1][0] = 'U'
    elif dir =='S':
        y-=1
        if y == -1:
            for k in c:
                if c[k] is not None:
                    c[k][1]+=1
            wumpusMap.insert(0,['']*len(wumpusMap[0]))
            y = 0
            if 'E' in walls:
                wumpusMap[0][-1] = 'U'
            if 'W' in walls:
                wumpusMap[0][0] = 'U'
    elif dir == 'E':
        x += 1
        if x == len(wumpusMap[0]):
            for row in wumpusMap:
                row.append('')
            if 'N' in walls:
                wumpusMap[-1][-1] = 'U'
            if 'S' in walls:
                wumpusMap[0][-1] = 'U'
    elif dir =='W':
        x -= 1
        if x == -1:
            for k in c:
                if c[k] is not None:
                    c[k][0]+=1
            for row in wumpusMap:
                row.insert(0,'')
            x = 0
            if 'N' in walls:
                wumpusMap[-1][0] = 'U'
            if 'S' in walls:
                wumpusMap[0][0] = 'U'

#attempts to discern more information about the pit or immobile wumpus nearby, returns nothing
def stationaryThreat():
    global gold, prevMvs,wumpusMap,x,y,wType,nArrows,nWumpi,inv
    suspect = []
    clear = 0
    for dir,ny,nx,nv in iterNeighbors():#n for neighbor


        if nv not in 'XUsP':
            nv += 'p'
            suspect = [ny,nx]
        elif nv in 'XUs':
            clear += 1
        if nv.count('p') == 4:
            nv = 'P'
        if clear == 3 and len(suspect)==2:
            wumpusMap[suspect[0]][suspect[1]]='P'
        wumpusMap[ny][nx] = nv

#When the systematic sweep has failed find a way to new targets, returns a direction
def fallback():
    global gold, prevMvs,wumpusMap,x,y,wType,nArrows,nWumpi,inv,c,walls

    if 'fb' in c:
        if c['fb'][0]==x and c['fb'][1]==y:
            c.pop('fb')
    if 'fb' not in c:
        best = None
        pmin=4
        dmin=999
        i=0
        for row in wumpusMap:
            j=0
            for v in row:
                if v in 'ps'and not (i==y and j==x):
                    if v.count('p')<pmin:
                        best = [j,i]
                        pmin = v.count('p')
                        dmin = abs(x-j)+abs(y-i)
                    elif v.count('p') == pmin and abs(x-j)+abs(y-i)<dmin:
                        best = [j,i]
                        pmin = v.count('p')
                        dmin = abs(x-j)+abs(y-i)
                j+=1
            i+=1


        if best is None:
            walls=''
            prevMvs=''
            wumpusMap=[['']]
            return 'N'
        else:
            c['fb']=best

    return moveTowards(c['fb'])

#move back to the nearest open point while searching, returns a direction or a blank
def back():
    global gold, prevMvs,wumpusMap,x,y,wType,nArrows,nWumpi,inv,c

    if len(prevMvs) > 0:
        return inv[prevMvs.pop()]
    else:
        return ''

#finds direct route to some destination on the internal map
def moveTowards(dest):
    global x,y,c
    if x>dest[0]:
        return 'W'
    if x<dest[0]:
        return 'E'
    if y>dest[1]:
        return 'S'
    if y<dest[1]:
        return 'N'
        return ''

#handy utility for cycling through the players 4 neighbors.
def iterNeighbors():
    global gold, prevMvs,wumpusMap,x,y,wType,nArrows,nWumpi,inv
    for c in inv:#map sure our map is rendered
        mapMove(c)
        mapMove(inv[c])

    return (('N',y+1,x,wumpusMap[y+1][x]),('E',y,x+1,wumpusMap[y][x+1]),('S',y-1,x,wumpusMap[y-1][x]),('W',y,x-1,wumpusMap[y][x-1]))
