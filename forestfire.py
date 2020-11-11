import sys, math, random
import pygame
import pygame.draw
import numpy as np
from random import randint 

_screenSize = (600 , 600) 
_cellSize = 10
_gridDim = tuple(map(lambda x: int(x / _cellSize), _screenSize))
_density = 0.7 #densité de la forêt 
_water = 15 #points d'eau 

#dans l'ordre : espace vide, arbre, arbre en feu, arbre coriace, arbre coriace affaibli, eau  
_colors = [(255, 255, 255), (0, 255, 0), (255, 0, 0), (0,100,0), (0,100,0), (0,191,255)]

#taille du glidergun
gg_width, gg_height = 60, 60
glidergun=[[0]*gg_width for i in range(gg_height)]
#on remplit le terrain avec des arbres en fonction de la densité
cpt = 0 #nombre d'arbres
#le nombre d'arbres ne doit pas dépasser le nombre de case * la densité
max = (gg_width * gg_height * _density)


#0 > pas d'arbre - 1 > présence d'un arbre - 2 > présence d'un feufeu
for i in range(100):
       glidergun[randint(0,gg_height-1)][randint(0,gg_width-1)] = 3
while (cpt < max) :
    if glidergun[randint(0,gg_height-1)][randint(0,gg_width-1)] == 0 :
        glidergun[randint(0,gg_height-1)][randint(0,gg_width-1)] = 1
        cpt = cpt + 1 
for i in range(_water):
       x = randint(0,gg_height-2)
       y = randint(0,gg_width-2)    
       #un point d'eau sera plus grand (4 carreaux au lieu d'un)
       glidergun[x][y] = 5
       glidergun[x+1][y] = 5
       glidergun[x][y+1] = 5
       glidergun[x+1][y+1] = 5
def getColorCell(n):
    return _colors[n]


class Grid:
    _grid= None
    _gridbis = None
    _indexVoisins = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    def __init__(self):
        print("Creating a grid of dimensions " + str(_gridDim))
        self._grid = np.zeros(_gridDim, dtype='int8')
        self._gridbis = np.zeros(_gridDim, dtype='int8')
        #On initialise avec le glidergun 
        a = np.fliplr(np.rot90(np.array(glidergun),3))
        nx, ny = _gridDim
        mx, my = a.shape
        self._grid[nx//2-mx//2:nx//2+mx//2, ny//2-my//2:ny//2+my//2] = a

        #feu au centre
        self._grid[nx//2,ny//2] = 2
        self._grid[nx//2+1,ny//2] = 2
        self._grid[nx//2,ny//2+1] = 2
        self._grid[nx//2+1,ny//2+1] = 2
        
    def indiceVoisins(self, x,y):
        return [(dx+x,dy+y) for (dx,dy) in self._indexVoisins if dx+x >=0 and dx+x < _gridDim[0] and dy+y>=0 and dy+y < _gridDim[1]] 

    def voisins(self,x,y):
        return [self._grid[vx,vy] for (vx,vy) in self.indiceVoisins(x,y)]
   
    def voisinFeu(self, x, y):
        indice = self.indiceVoisins(x, y)
        feu = False 
        for i in range(len(indice)) :
            if self._grid[indice[i][0], indice[i][1]] == 2 :
                feu = True
        return feu

    def sommeVoisins(self, x, y):
        return sum(self.voisins(x,y))        

    def sumEnumerate(self):
        return [(c, self.sommeVoisins(c[0], c[1])) for c, _ in np.ndenumerate(self._grid)]

    def drawMe(self):
        pass

class Scene:
    _grid = None
    _font = None

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode(_screenSize)
        self._font = pygame.font.SysFont('Arial',25)
        self._grid = Grid()

    #drawMe remplit l'écran, dessine des rectangles
    def drawMe(self):
        if self._grid._grid is None:
            return
        self._screen.fill((255,255,255))
        for x in range(gg_width):
            for y in range(gg_height):
                pygame.draw.rect(self._screen, 
                        getColorCell(self._grid._grid.item((x,y))),
                        (x*_cellSize + 1, y*_cellSize + 1, _cellSize-2, _cellSize-2))

    def update(self):
        for c, s in self._grid.sumEnumerate():
            #si arbre n'est pas en feu 
            if self._grid._grid[c[0], c[1]] == 1 : 
                #si arbre a un voisin en feu 
                if self._grid.voisinFeu(c[0],c[1]) :  
                    self._grid._gridbis[c[0], c[1]] = 2
                else : self._grid._gridbis[c[0], c[1]] = 1 
            
            #si arbre coriace et pas de voisin en feu, il ne change pas
            elif self._grid._grid[c[0], c[1]] == 3 : 
                #si arbre a un voisin en feu 
                if self._grid.voisinFeu(c[0],c[1]) :  
                    self._grid._gridbis[c[0], c[1]] = 4
                else : self._grid._gridbis[c[0], c[1]] = 3
            
            #si arbre affaibli mais pas de voisin en feu, il ne change pas
            elif self._grid._grid[c[0], c[1]] == 4 : 
                #si arbre a un voisin en feu 
                if self._grid.voisinFeu(c[0],c[1]) :  
                    self._grid._gridbis[c[0], c[1]] = 2
                else : self._grid._gridbis[c[0], c[1]] = 4

            #points d'eau, résistant au feu 
            elif self._grid._grid[c[0], c[1]] == 5 : 
                self._grid._gridbis[c[0], c[1]] = 5

            #vide - pas d'arbres
            elif self._grid._grid[c[0], c[1]] == 0 : self._grid._gridbis[c[0], c[1]] = 0    

            #si arbre en feu
            elif (self._grid._grid[c[0],c[1]]==2) :
                #l'arbre en feu est détruit 
                self._grid._gridbis[c[0],c[1]]=0
                #tous les arbres voisins prennent feu
                voisins = self._grid.indiceVoisins(c[0],c[1])
                for i in range (len(voisins)):
                    #les arbres sont brûlés lorsqu'ils existent (==1)
                    if (self._grid._grid[voisins[i][0], voisins[i][1]] == 1) :
                        self._grid._gridbis[voisins[i][0], voisins[i][1]] = 2
                    #si arbre coriace, il est affaibli 
                    elif self._grid._grid[voisins[i][0], voisins[i][1]] ==3 :
                        self._grid._gridbis[voisins[i][0], voisins[i][1]]=4 
                    #si arbre affaibli, il prend feu 
                    elif self._grid._grid[voisins[i][0], voisins[i][1]]==4 :
                        self._grid._gridbis[voisins[i][0], voisins[i][1]]=2 
            
            
        self._grid._grid = np.copy(self._grid._gridbis)

def main():
    scene = Scene()
    done = False
    clock = pygame.time.Clock()
    while done == False:
        scene.drawMe()
        scene.update()
        pygame.display.flip()
        clock.tick(5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                print("Exiting")
                done=True

    pygame.quit()

if not sys.flags.interactive: main()
