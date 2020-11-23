import sys, math, random
import pygame
import pygame.draw
import numpy as np
from random import randint 

_screenSize = (800 , 800) 
_forestSize = (600, 600)
_cellSize = 10
_gridDim = tuple(map(lambda x: int(x / _cellSize), _forestSize))
_water = 15 #points d'eau 

#dans l'ordre : espace vide, arbre, arbre en feu, arbre coriace, arbre coriace affaibli, eau  
_colors = [(255, 255, 255), (0, 255, 0), (255, 0, 0), (0,100,0), (0,100,0), (0,191,255)]

playRect = pygame.Rect(_forestSize[0]+20, 60, 50, 30)
stopRect = pygame.Rect(_forestSize[0]+80, 60, 50, 30)
density3Rect = pygame.Rect(_forestSize[0]+20, 20, 40, 30)
density5Rect = pygame.Rect(_forestSize[0]+70, 20, 40, 30)
density7Rect = pygame.Rect(_forestSize[0]+120, 20, 40, 30)

gg_width, gg_height = 60, 60

def getColorCell(n):
    return _colors[n]

class Grid:
    _grid= None
    _gridbis = None
    _indexVoisins = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    def __init__(self, density):
        print("Creating a grid of dimensions " + str(_gridDim))
        glidergun = self.initGlidergun(density)
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
    
    def initGlidergun(self, density):
        #taille du glidergun
        glidergun=[[0]*gg_width for i in range(gg_height)]
        #on remplit le terrain avec des arbres en fonction de la densité
        cpt = 0 #compteur d'arbres
        print(density)
        max = (gg_width * gg_height * density) #nombre d'arbres crées (avant le feu)
        print(max)
        #0 > pas d'arbre - 1 > présence d'un arbre - 2 > présence d'un feufeu
        for i in range(100):
               glidergun[randint(0,gg_height-1)][randint(0,gg_width-1)] = 3
        for i in range(_water):
               x = randint(0,gg_height-2)
               y = randint(0,gg_width-2)    
               glidergun[x][y] = 5
        while (cpt <= max) :
            if glidergun[randint(0,gg_height-1)][randint(0,gg_width-1)] == 0 :
                glidergun[randint(0,gg_height-1)][randint(0,gg_width-1)] = 1
                cpt = cpt + 1           
        return glidergun
        
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
    _nbTrees = 0

    def __init__(self, density):
        pygame.init()
        self._density = density
        self._screen = pygame.display.set_mode(_screenSize)
        self._font = pygame.font.SysFont('Arial',18)
        self._grid = Grid(self._density)
        self._max = (gg_width * gg_height * self._density)
        self._nbTrees = 0

    #drawText permet d'afficher du texte sur la scene
    def drawText(self, text, position, color):
        self._screen.blit(self._font.render(text,1,color),position)
        
    #drawButton permet de créer un bouton avec un titre, sa position (x, y), sa taille (w, h), et sa couleur active et normale
    def drawButton(self, title, rect, color1, color2):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if rect[0]+rect[2] > mouse[0] > rect[0] and rect[1]+rect[3] > mouse[1] > rect[1]:
            pygame.draw.rect(self._screen, color1, (rect[0], rect[1], rect[2], rect[3]))
        else:
            pygame.draw.rect(self._screen, color2, (rect[0], rect[1], rect[2], rect[3]))  
        
        self.drawText(title, ((rect[0]+(rect[2]/2)-10), (rect[1]+(rect[3]/2)-10)), (0,0,0))
        

    def countLeftTrees(self):
        self._nbTrees = 0 
        for i in range(len(self._grid._grid)):
            for j in range(len(self._grid._grid)):
                if self._grid._grid[i,j] == 1 or self._grid._grid[i,j] == 3 : 
                    self._nbTrees = self._nbTrees + 1
        return self._nbTrees
    
    def countDestroyedTrees(self):
        return (self._max - self._nbTrees)

    #drawMe remplit l'écran, dessine des rectangles
    def drawMe(self):
        if self._grid._grid is None:
            return
        self._screen.fill((255,255,255))
        for x in range(gg_width):
            for y in range(gg_height):
                pygame.draw.rect(self._screen, (255,255,255), (x*_cellSize + 1, y*_cellSize + 1, _cellSize-2, _cellSize-2))
                pygame.draw.rect(self._screen, getColorCell(self._grid._grid.item((x,y))), (x*_cellSize + 1, y*_cellSize + 1, _cellSize-2, _cellSize-2))
        
        #cadrage de la scène
        points = [(0,0), (_forestSize[0],0), (_forestSize[0],_forestSize[0]), (0,_forestSize[0])]
        pygame.draw.lines(self._screen, (0,0,0), True, points, 2)
        
        self.drawButton("0.3", density3Rect, (0, 255, 0), (0, 195, 0))
        self.drawButton("0.5", density5Rect, (0, 155, 0), (0, 95, 0))
        self.drawButton("0.7", density7Rect, (0, 95, 0), (0, 55, 0))
        self.drawButton("Play", playRect, (200, 200, 200), (100, 100, 100))
        self.drawButton("Stop", stopRect, (200, 200, 200), (100, 100, 100))
        
        #affichage de la densité de la forêt
        self.drawText("- Densite de la foret : " + str(self._density), (20,_forestSize[0]+20), (0,0,0))
        #nombre d'arbres restants
        self.drawText("- Nombre d'arbres restants : " + str(self.countLeftTrees()), (20,_forestSize[0]+50), (0,0,0))
        #nombre d'arbres détruits
        self.drawText("- Nombre d'arbres detruits : " + str(self.countDestroyedTrees()), (20,_forestSize[0]+80), (0,0,0))
        #pourcentage d'arbres détruits 
        self.drawText("- Pourcentage d'arbres detruits : " + str(round(self.countDestroyedTrees()/self._max,2)), (20,_forestSize[0]+110), (0,0,0))
    

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
    scene = Scene(0.7)
    done = False
    start = False
    clock = pygame.time.Clock()
    while done == False:
        scene.drawMe()
        if start == True:
            scene.update()
        pygame.display.flip()
        clock.tick(5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                print("Exiting")
                done=True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse = pygame.mouse.get_pos()
                    if(playRect.collidepoint(mouse)):
                        start = True
                    if(stopRect.collidepoint(mouse)):
                        start = False
                    if(density3Rect.collidepoint(mouse)):
                        scene = Scene(0.3)
                    if(density5Rect.collidepoint(mouse)):
                        scene = Scene(0.5)
                    if(density7Rect.collidepoint(mouse)):
                        scene = Scene(0.7)
                            
    pygame.quit()

if not sys.flags.interactive: main()
