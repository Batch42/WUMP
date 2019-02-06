gold = False
prevMvs = []
walls=''
wumpusMap = [['']]
x=0; y=0;ex=0;ey=0; wType=0; nArrows=0; nWumpi=0
offset=[[0,1],[0,-1],[1,0],[-1,0]]
inv = {'N':'S','S':'N','E':'W','W':'E'}
def setParams(gameType, numArrows, numWumpi):
    global gold, prevMvs,wumpusMap,x,ey,ex,y,wType,nArrows,nWumpi,offset,inv
    wType = gameType
    nArrows = numArrows
    nWumpi = numWumpi
    gold = False
    prevMvs = []
    wumpusMap = [['']]
    x=0; y=0;ex=0;ey=0

def getMove(percept):
    global gold, walls, prevMvs,wumpusMap,x,ey,ex,y,wType,nArrows,nWumpi,offset,inv

    dir=''

    if 'U' in percept:
        bdir = back()
        if bdir == 'N' or bdir == 'S':
            wumpusMap[y] = ['U']*len(wumpusMap[0])
        else:
            for row in wumpusMap:
                row[x] = 'U'
        mapMove(bdir)
        walls += inv[bdir] #add the wall we bumped into to the list of walls
    if gold:
        if x==ex and y==ey:
            return "C"
        dir = back()
    elif 'G' in percept and 'S' not in percept:
        gold = True
        return 'G'
    elif 'S' in percept and wType==2:
        dir = back()
    elif 'B' in percept or ('S' in percept and wType==1):
        dir = back()
        if 'X' not in wumpusMap[y][x]:
            stationaryThreat()
    else:
        for ndir,ny,nx,nv in iterNeighbors():
            if 'p' in nv:
                wumpusMap[ny][nx] = wumpusMap[ny][nx].replace('p','')
            if nv=='':
                dir=ndir
        if dir == '':
            dir = back()
        else:
            prevMvs.append(dir)

    wumpusMap[y][x] = 'X'



    mapMove(dir)
    #print (percept)
    return dir

def mapMove(dir):
    global gold, prevMvs, walls,wumpusMap,x,y,ex,ey,wType,nArrows,nWumpi,offset,inv
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
            #warning, this will invalidate any coordinate data that we may store
            ey+=1
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
            ex +=1
            #warning, this will invalidate any coordinate data that we may store
            for row in wumpusMap:
                row.insert(0,'')
            x = 0
            if 'N' in walls:
                wumpusMap[-1][0] = 'U'
            if 'S' in walls:
                wumpusMap[0][0] = 'U'

def stationaryThreat():
    global gold, prevMvs,wumpusMap,x,y,wType,nArrows,nWumpi,offset,inv
    suspect = []
    clear = 0
    for dir,ny,nx,nv in iterNeighbors():#n for neighbor


        if 'X' not in nv and 'P' not in nv and 'U' not in nv:
            nv += 'p'
            suspect = [ny,nx]
        elif 'X' in nv or 'U' in nv:
            clear += 1
        if nv.count('p') == 4:
            nv = 'P'
        if clear == 3 and len(suspect)==2:
            wumpusMap[suspect[0]][suspect[1]]='P'
        wumpusMap[ny][nx] = nv

def back():
    global gold, prevMvs,wumpusMap,x,y,wType,nArrows,nWumpi,offset,inv
    if len(prevMvs) > 0:
        return inv[prevMvs.pop()]
    else:
        return 'S'

def iterNeighbors():
    global gold, prevMvs,wumpusMap,x,y,wType,nArrows,nWumpi,offset,inv
    for c in inv:#map sure our map is rendered
        mapMove(c)
        mapMove(inv[c])

    return (('N',y+1,x,wumpusMap[y+1][x]),('E',y,x+1,wumpusMap[y][x+1]),('S',y-1,x,wumpusMap[y-1][x]),('W',y,x-1,wumpusMap[y][x-1]))
