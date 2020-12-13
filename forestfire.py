import sys, math, random
import pygame
import pygame.draw
import numpy as np
from random import randint 
from matplotlib import pyplot as plt
import pandas as pd

_screenSize = (800 , 800) 
_forestSize = (600, 600)
_cellSize = 10
_gridDim = tuple(map(lambda x: int(x / _cellSize), _forestSize))
_water = 15 #points d'eau 

#dans l'ordre : espace vide, arbre normale, arbre en feu, arbre fort, arbre très fort, eau  
_colors = [(255, 255, 255), (0, 255, 0), (255, 0, 0), (0,150,0), (0,100,0), (0,191,255)]

playRect = pygame.Rect(_forestSize[0]+20, 100, 50, 30)
stopRect = pygame.Rect(_forestSize[0]+80, 100, 50, 30)
density3Rect = pygame.Rect(_forestSize[0]+20, 20, 50, 30)
density5Rect = pygame.Rect(_forestSize[0]+80, 20, 50, 30)
density7Rect = pygame.Rect(_forestSize[0]+20, 60, 50, 30)
density9Rect = pygame.Rect(_forestSize[0]+80, 60, 50, 30)

gg_width, gg_height = 60, 60

def getColorCell(n):
    return _colors[n]

class Grid:
    _grid= None
    _gridbis = None
    _indexVoisins = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    def __init__(self, density, age):
        print("Creating a grid of dimensions " + str(_gridDim))
        glidergun = self.initGlidergun(density, age)
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
    
    def initGlidergun(self, density, age):
        #taille du glidergun
        glidergun=[[0]*gg_width for i in range(gg_height)]
        
        #on remplit le terrain avec des arbres en fonction de la densité
        max = (gg_width * gg_height * round(density,1)) #nombre d'arbres crées (avant le feu)

        for i in range(_water):
            x = randint(0,gg_height-1)
            y = randint(0,gg_width-1)
            if glidergun[x][y] == 0 :
               glidergun[x][y] = 5
               
        #le pourcentage d'arbres de différentes forces n'est pas le même suivant la densité que l'on fixe
        #on part également du principe que plus une forêt est dense, plus elle contient d'arbres ancients et donc plus résistants
        if(age == 5): 
            d0 = 0.7 #pourcentage d'arbres normaux
            d1 = 0.2 #pourcentage d'arbres forts et donc plus difficiles à brûler
            d2 = 0.1 #pourcentage d'arbres encore plus forts 
        elif(age == 10):
            d0 = 0.5
            d1 = 0.4
            d2 = 0.1
        elif(age == 15): 
            d0 = 0.5
            d1 = 0.3
            d2 = 0.2
        elif(age == 20):
            d0 = 0.4
            d1 = 0.3
            d2 = 0.3
        
        cpt0 = 0 #compteur d'arbres normaux
        cpt1 = 0 #compteur d'arbres plus forts
        cpt2 = 0 #compteur d'arbres encore plus forts
        
        while cpt0 < d0 * max : 
            x = randint(0,gg_height-1)
            y = randint(0,gg_width-1)
            if glidergun[x][y] == 0 :
               glidergun[x][y] = 1
               cpt0 = cpt0 + 1
        
        while cpt1 < d1 * max : 
            x = randint(0,gg_height-1)
            y = randint(0,gg_width-1)
            if glidergun[x][y] == 0 :
               glidergun[x][y] = 3
               cpt1 = cpt1 + 1
        
        while cpt2 < d2 * max : 
            x = randint(0,gg_height-1)
            y = randint(0,gg_width-1)
            if glidergun[x][y] == 0 :
               glidergun[x][y] = 4
               cpt2 = cpt2 + 1 
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

    def __init__(self, density, age):
        pygame.init()
        self._density = density
        self._age = age
        self._screen = pygame.display.set_mode(_screenSize)
        self._font = pygame.font.SysFont('Arial',18)
        self._grid = Grid(self._density, self._age)
        self._max = gg_width * gg_height * round(self._density,1)

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
        self._leftTrees = 0 
        for i in range(len(self._grid._grid)):
            for j in range(len(self._grid._grid)):
                if self._grid._grid[i,j] == 1 or self._grid._grid[i,j] == 3 or self._grid._grid[i,j] == 4 :
                    self._leftTrees = self._leftTrees + 1
        return self._leftTrees
    
    def countDestroyedTrees(self):
        return (self._max - self.countLeftTrees())
    
    def countDestroyedTreesPourcent(self):
        return self.countDestroyedTrees()/self._max

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
        
        self.drawButton("5 ans", density3Rect, (0, 255, 0), (0, 195, 0))
        self.drawButton("10 ans", density5Rect, (0, 155, 0), (0, 95, 0))
        self.drawButton("15 ans", density7Rect, (0, 95, 0), (0, 55, 0))
        self.drawButton("20 ans", density9Rect, (0, 95, 0), (0, 55, 0))
        self.drawButton("Play", playRect, (200, 200, 200), (100, 100, 100))
        self.drawButton("Stop", stopRect, (200, 200, 200), (100, 100, 100))
        
        #affichage de la densité de la forêt
        self.drawText("- Densite de la foret : " + str(self._density), (20,_forestSize[0]+20), (0,0,0))
        #nombre d'arbres restants
        self.drawText("- Nombre d'arbres restants : " + str(self.countLeftTrees()), (20,_forestSize[0]+50), (0,0,0))
        #nombre d'arbres détruits
        self.drawText("- Nombre d'arbres detruits : " + str(self.countDestroyedTrees()), (20,_forestSize[0]+80), (0,0,0))
        #pourcentage d'arbres détruits 
        self.drawText("- Pourcentage d'arbres detruits : " + str(round(self.countDestroyedTreesPourcent(), 2)), (20,_forestSize[0]+110), (0,0,0))
    

    def update(self):
        for c, s in self._grid.sumEnumerate():
            #si arbre n'est pas en feu 
            if self._grid._grid[c[0], c[1]] == 1 : 
                #si arbre a un voisin en feu 
                if self._grid.voisinFeu(c[0],c[1]) :  
                    self._grid._gridbis[c[0], c[1]] = 2
                else : self._grid._gridbis[c[0], c[1]] = 1 
            
            #si arbre fort et pas de voisin en feu, il ne change pas
            elif self._grid._grid[c[0], c[1]] == 3 : 
                #si arbre a un voisin en feu 
                if self._grid.voisinFeu(c[0],c[1]) :  
                    self._grid._gridbis[c[0], c[1]] = 1
                else : self._grid._gridbis[c[0], c[1]] = 3
            
            #si arbre très fort, il perd un peu de force
            elif self._grid._grid[c[0], c[1]] == 4 : 
                #si arbre a un voisin en feu 
                if self._grid.voisinFeu(c[0],c[1]) :  
                    self._grid._gridbis[c[0], c[1]] = 3
                else : self._grid._gridbis[c[0], c[1]] = 4

            #points d'eau, résistant au feu 
            elif self._grid._grid[c[0], c[1]] == 5 : 
                self._grid._gridbis[c[0], c[1]] = 5

            #vide - pas d'arbres
            elif self._grid._grid[c[0], c[1]] == 0 : 
                self._grid._gridbis[c[0], c[1]] = 0    

            #si arbre en feu
            elif (self._grid._grid[c[0],c[1]]==2) :
                #l'arbre en feu est détruit 
                self._grid._gridbis[c[0],c[1]]=0
                #tous les arbres voisins prennent feu
                voisins = self._grid.indiceVoisins(c[0],c[1])
                for i in range (len(voisins)):
                    #les arbres normaux sont brûlés lorsqu'ils existent (==1)
                    if (self._grid._grid[voisins[i][0], voisins[i][1]] == 1) :
                        self._grid._gridbis[voisins[i][0], voisins[i][1]] = 2
                    #si arbre fort, il est affaibli 
                    elif self._grid._grid[voisins[i][0], voisins[i][1]] ==3 :
                        self._grid._gridbis[voisins[i][0], voisins[i][1]]=1 
                    #si arbre très fort, il s'affaibli un peu mais reste un peu fort
                    elif self._grid._grid[voisins[i][0], voisins[i][1]]== 4 :
                        self._grid._gridbis[voisins[i][0], voisins[i][1]]=3 
            
        self._grid._grid = np.copy(self._grid._gridbis)
        
class Simulation:
    def __init__(self):
        self._densities = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65,
                             0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
        self._age = [5, 10, 15, 20]
        self._destroyedTrees = []

    def simulate(self):
        for j in range(len(self._age)):
            self._destroyedTrees.append([])
            for i in range(len(self._densities)):
                print(self._densities[i])
                scene = Scene(self._densities[i], self._age[j])
                done = False
                countDestroyedTrees = scene.countDestroyedTreesPourcent()
                while done == False:
                    scene.update()
                    if(countDestroyedTrees == scene.countDestroyedTreesPourcent()):
                        countDestroyedTrees = scene.countDestroyedTreesPourcent()
                        done = True
                    else:
                        countDestroyedTrees = scene.countDestroyedTreesPourcent()
                self._destroyedTrees[j].append(round(countDestroyedTrees, 4))
            print(self._densities)
            print(self._destroyedtTrees)
        
        
        df = pd.DataFrame({'x': self._densities, 'y1': self._leftTrees[0], 'y2': self._leftTrees[1], 'y3': self._leftTrees[2], 'y4': self._leftTrees[3]})
        
        plt.subplot(111)
        plt.plot('x', 'y1', data=df, marker='o', markerfacecolor="green", color="green", label="5 ans")
        plt.plot('x', 'y2', data=df, marker='o', markerfacecolor="blue", color="blue", label="10 ans")
        plt.plot('x', 'y3', data=df, marker='o', markerfacecolor="red", color="red", label="15 ans")
        plt.plot('x', 'y4', data=df, marker='o', markerfacecolor="grey", color="grey", label="20 ans")
        plt.legend()
        plt.xlabel("Densite")
        plt.ylabel("Pourcentage d'arbres detruits")
        plt.show()
    
def main():
    Simulation().simulate()
    scene = Scene(0.4, 5)
    done = False
    start = False
    clock = pygame.time.Clock()
    while done == False:
        scene.drawMe()
        if start == True:
            scene.update()
        pygame.display.flip()
        clock.tick(15)
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
                        scene = Scene(0.4, 5)
                        start = False
                    if(density5Rect.collidepoint(mouse)):
                        scene = Scene(0.5, 10)
                        start = False
                    if(density7Rect.collidepoint(mouse)):
                        scene = Scene(0.6, 15)
                        start = False
                    if(density9Rect.collidepoint(mouse)):
                        scene = Scene(0.7, 20)
                        start = False
                            
    pygame.quit()

if not sys.flags.interactive: main()
