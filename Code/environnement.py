import logging
import math
import os
import random
import time

import numpy as np

from .obstacle import Obstacle
from .robot import Robot

if not os.path.isdir('Code/Logs'):
    os.mkdir("Code/Logs/")
logging.basicConfig(filename='Code/Logs/logs.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s') # niveaux : DEBUG INFO WARNING ERROR CRITICAL

class Environnement:
    
    def __init__(self, width, length, scale): 
        
        """ Initialise l'environnement où l'on va se placer, où on considère que l'environnement dans lequel évolue le robot est un rectangle
            :param width: largeur de l'environnement
            :param length: longueur de l'environnement
            :param scale: l'échelle qui permet de passer de l'environnement à la matrice, c'est la correspondance de la taille d'un côté d'une case de la matrice dans le rectangle
            :returns: ne retourne rien, fait juste l'initialisation
        """
        
        self.width=width
        self.length=length
        self.robots = []
        self.robotSelect = 0 # robot selectionné pour bouger
        self.scale = scale #echelle en int positif 
        self.last_refresh = 0 # initialise la dernière fois où l'environnement a été rafraîchi à 0 pour savoir quand on le fait pour la première fois
        self.listeObs =[]
        self.initMatrice()

    def initMatrice(self):
        """
        Initialise la matrice avec des 0, ainsi que ses bords avec 2 (obstacles)
        :returns: rien, initialise juste la matrice comme il faut
        """
        self.matrice = np.zeros([int(self.length/self.scale), int(self.width/self.scale)], dtype=int) # Création d'une matrice int(width/scale)*int(length/scale) grâce à np.empty
        self.matrice[0] = 2
        self.matrice[-1] = 2
        self.matrice[:, 0] = 2
        self.matrice[:, -1] = 2

    def addRobotSelect(self, n):
        """
        Change l'indice du robot sélectionné (lui ajoute n)
        :returns: rien, ajoute n à la valeur de sélection du robot
        """
        self.robotSelect = (self.robotSelect + n)% len(self.robots)
    

    def addObstacle(self,nom, lstPoints):
        """ Ajout d'un obstacle dans la matrice, l'obstacle est représenté par '2' dans la matrice
            :param nom: nom de l'obstacle
            :param lstPoints: liste des points (x,y) qui définissent la forme de l'obstacle 
            :returns: ne retourne rien, place juste un obstacle aléatoirement dans la matrice
        """
        self.listeObs.append(Obstacle(nom,lstPoints))
        if any(x > self.width or x < 0 or y > self.length or y < 0 for (x, y) in lstPoints):
            return print("Obstacle hors environnement")


        # Placement des bordures de l'obstacle dans l'environnement
        for i in range(len(lstPoints)): # Parcours la liste des points
            x1, y1 = lstPoints[i]
            x2, y2 = lstPoints[(i+1)%len(lstPoints)] # Cas où i est le dernier indice de la liste - Point d'arrivée

            self.matrice[int(y1/self.scale)][int(x1/self.scale)] = 2 # Place le pt de départ dans la matrice
            #print('\nOBJECTIF :', x2, y2)

            while (round(x1), round(y1)) != (round(x2), round(y2)):
                long = math.sqrt((x2-x1)**2 + (y2-y1)**2) # Longueur du vect dir
                dir = ((x2-x1)/long ,(y2-y1)/long) # Vect dir normalisé
                
                x1,y1 = ((x1+dir[0]), (y1+dir[1]))

                self.matrice[int(y1/self.scale)][int(x1/self.scale)] = 2 # Update la matrice
                try:
                    self.matrice[int(y1/self.scale)][int(x1/self.scale)+1] = 2 # Deuxieme couche pour aucun pb de hitbox
                    self.matrice[int(y1/self.scale)+1][int(x1/self.scale)] = 2
                except:
                    pass

            #print('Arrivé en :', x1, y1)
        #time.sleep(1)

    def print_matrix(self):
        for row in self.matrice:
            print(' '.join(str(item) for item in row))

    def setRobot(self, robot, couleur):

        """ Crée un robot et l'ajoute à notre environnement
            :param nom: nom du robot
            :param x: la coordonnée x où on veut placer le robot au départ
            :param y: la coordonnée y où on veut placer le robot au départ
            :param width: la largeur du robot
            :param length: la longueur du robot
            :param rayonRoue: le rayon des roues 
            :returns: rien, on crée juste un robot qu'on ajoute a la liste des robots de l'environnement
        """
        robot.couleur = couleur
        self.robots.append(robot)
        #self.matrice[int(x/self.scale)][int(y/self.scale)] = 1 # Ajoute le robot représenté par le chiffre 1 dans la matrice

    def addRobot(self, rob) :

        """ Ajoute le robot rob à l'environnement et le place dans la matrice
            :param rob: le robot qu'on veut ajouter à l'environnement
            :returns: ne retourne rien
        """

        self.robots.append(rob)
        self.matrice[int(rob.x/self.scale)][int(rob.y/self.scale)] = 1 # Ajoute à la matrice le robot grâce a sa position en le représentant par un 1

    # def addObstacle(self,nom):

    #     """ Ajout d'un obstacle dans la matrice, l'obstacle est représenté par '2' dans la matrice
    #         :param nom: nom de l'obstacle
    #         :returns: ne retourne rien, place juste un obstacle aléatoirement dans la matrice
    #     """

    #     obs_place = False
    #     while( obs_place == False ) :
    #         random_x = random.randrange(0,self.width) #prend des coordonnees aleatoires pour l'obstacle
    #         random_y = random.randrange(0,self.length)
    #         x = int(random_x/self.scale)
    #         y = int(random_y/self.scale)
    #         if ( self.matrice[x][y] != 1 | self.matrice[x][y] != 2) :
    #             Obstacle(nom, x, y)
    #             self.matrice[x][y] = 2 #  Ajoute l'obstacle représenté par le chiffre 2 dans la matrice
    #             obs_place = True

    # def detect_obs(self, rob) :

    #     """ Détection d'un obstacle autour du robot
    #         :param rob: le robot autour duquel on veut vérifier s'il y a un obstacle
    #         :returns: true si un obstacle est détecté, false sinon
    #     """

    #     # Detecte si il y a un obstacle devant
    #     if ( self.matrice[int(rob.x/self.scale)+1][int(rob.y/self.scale)] == 2 ) :
    #         return True
    #     # Detecte si il y a un obstacle derriere
    #     if ( self.matrice[int(rob.x/self.scale)-1][int(rob.y/self.scale)] == 2 ) :
    #         return True
    #     # Detecte si il y a un obstacle à droite
    #     if ( self.matrice[int(rob.x/self.scale)][int(rob.y/self.scale)+1] == 2 ) :
    #         return True
    #     # Detecte si il y a un obstacle à gauche
    #     if ( self.matrice[int(rob.x/self.scale)][int(rob.y/self.scale)-1] == 2 ) :
    #         return True

    #     return False
    
    def refresh_env(self) :

        """ Pour rafraichir l'environnement et faire updater tous les robots qui le composent.
            :returns: ne retourne rien, fait juste la mise à jour de tous les éléments
        """
        temps = time.time()

        if self.last_refresh == 0 : # donc si c'est la première fois qu'on fait le rafraichissement
            self.last_refresh = temps

        for rob in self.robots : # on fait avancer tous les robots de l'environnement
            if (not(self.collision2(rob))): # S'il n'y a pas collision
                duree = temps - self.last_refresh
                #rob.refresh(duree, canv)
                rob.refresh(duree)

        self.last_refresh = temps # on met à jour l'heure du dernier rafraichissement 

    def collision(self, rob) :
        """
            Vérifie si le robot rob est en collision avec un obstacle ou avec les bords de l'environnement
            :param rob: le robot pour lequel on veut vérifier s'il est en collision
            :returns: true si le robot est en collision, false sinon
        """
        newPosRob = (rob.x + rob.direction[0], rob.y + rob.direction[1]) # position du robot après un déplacement
        # renvoie true si le robot est en collision avec un obstacle ou avec les bords de l'environnement
        return ((newPosRob[0] <= 0) | (newPosRob[0] >= self.width/self.scale) | (newPosRob[1] <= 0) | (newPosRob[1] >= self.length/self.scale) | self.matrice[int(newPosRob[0]/self.scale)][int(newPosRob[1]/self.scale)] == 2)


    def collision2(self, rob):
        """
        Vérifie si le prochain mouvement du robot va le faire rentrer en collision avec un obstacle (2)
        :param rob: robot pour lequel on veut tester la collision prochaine
        :returns: true si robot en collision prochaine, false sinon"""

        # liste des 4 points du robot après mouvement (liste de 4couples): HG HD BD BG
        lstPoints = [(rob.x-(rob.width/2)+rob.direction[0],rob.y+(rob.length/2)+rob.direction[1]), (rob.x+(rob.width/2)+rob.direction[0],rob.y+(rob.length/2)+rob.direction[1]), (rob.x+(rob.width/2)+rob.direction[0],rob.y-(rob.length/2)+rob.direction[1]), (rob.x-(rob.width/2)+rob.direction[0],rob.y-(rob.length/2)+rob.direction[1])]

        for i in range(len(lstPoints)):
            x1, y1 = lstPoints[i] #départ
            x2, y2 = lstPoints[(i+1)%len(lstPoints)] #arrivée

            while (round(x1), round(y1)) != (round(x2), round(y2)):
                if (self.matrice[int(y1/self.scale)][int(x1/self.scale)]==2): # teste si le point est sur un obstacle
                    print("Collision de", rob.nom, "! Obstacle en (", str(x1),",",str(y1),")")
                    return True
                # print('aaa')
                long = math.sqrt((x2-x1)**2 + (y2-y1)**2) # Longueur du vect dir
                dir = ((x2-x1)/long ,(y2-y1)/long) # Vect dir normalisé
                x1,y1 = ((x1+dir[0]), (y1+dir[1])) #nv point
            
        return False # Après le parcours de tout le contour, si pas d'obstacle rencontré -> False


    def affiche(self):
        #methodes pour affichage avec tkinter
        pass

