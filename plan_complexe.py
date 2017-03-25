# -*- coding: utf-8 -*-
#! /usr/bin/python2

import pygame
import sys

class repere:
    '''
    Classe repère: trace un repère orthonormé sur une Surface
    '''
    def __init__(self,
                 Surface,
                 n_pixels_par_unite = 50, # Nombre de pixels par unité
                 couleur_axes = (0,0,0),
                 epaisseur_axes = 1):

        self.Surface = Surface
        self.largeur = Surface.get_width()
        self.hauteur = Surface.get_height()

        # Position de l'origine en pixels depuis le coin haut gauche
        # Au centre, par défaut
        self.x_origine = self.largeur / 2 
        self.y_origine = self.hauteur / 2

        self.n_pixels_par_unite = n_pixels_par_unite
        
        self.couleur_axes = couleur_axes
        self.epaisseur_axes = epaisseur_axes
        
    # Un exemple de mutateur, c'est beau
    def muter_origine(self, x_origine_nouveau, y_origine_nouveau):
        self.x_origine = x_origine_nouveau
        self.y_origine = y_origine_nouveau
        
    def tracer(self):
        # Axe des abscisses
        pygame.draw.line(self.Surface, self.couleur_axes, (0, self.y_origine), (self.largeur, self.y_origine), self.epaisseur_axes)
        # Axe des ordonnées
        pygame.draw.line(self.Surface, self.couleur_axes, (self.x_origine, 0), (self.x_origine,  self.hauteur), self.epaisseur_axes)
        self.tracer_tirets()

    # Donnent les coordonnées d'un pixel, en pixels,
    # par rapport à l'origine de repère, avec les conventions ordinaires:
    #              
    #          ^ y
    #          |
    #          |____> x   <---- ASCII art
    #
    # ===================================================================
    def x_repere(self, x):
        return x - self.x_origine
    def y_repere(self, y):
        return self.y_origine - y

    # Donnent les coordonnées en unités du repère en fonction des coordonnées en pixels
    # Entrée: abscisse d'un pixel
    # Sortie: abscisse dans le repère
    def X(self, x):
        return float(x - self.x_origine) / self.n_pixels_par_unite
    def Y(self, y):
        return float(self.y_origine - y) / self.n_pixels_par_unite

    # Donnent les coordonnées en pixels, en fonction des coorodonnées en unités du repère
    # Entrées: coordonnées dans le repère
    # Sorties: coordonnées en pixels
    def x(self, X):
        return int(X * self.n_pixels_par_unite) + self.x_origine 
    def y(self, Y):
        return -int(Y * self.n_pixels_par_unite) + self.y_origine 

    # Trace les tirets des axes
    # Todo: ajouter des flèches
    def tracer_tirets(self):
        # Tirets du demi-axe des ordonnées du haut
        x = self.x_origine
        y = self.y_origine
        while(y < self.hauteur): y += self.n_pixels_par_unite
        while(y > 0):
            pygame.draw.line(self.Surface,
                             self.couleur_axes,
                             (x - 2 * self.epaisseur_axes, y),
                             (x + 2 * self.epaisseur_axes, y),
                             self.epaisseur_axes)
            y -= self.n_pixels_par_unite
        # Tirets du demi-axe des abscsses de gauche
        y = self.y_origine
        while(x < self.largeur): x += self.n_pixels_par_unite
        while(x > 0):
            pygame.draw.line(self.Surface,
                             self.couleur_axes,
                             (x, y - 2 * self.epaisseur_axes),
                             (x, y + 2 * self.epaisseur_axes),
                             self.epaisseur_axes)
            x -= self.n_pixels_par_unite

# Catalogue de deux fonctions:
# Entrées: partie réelle X et partie imaginaire Y

# Un polynome dont les racines sont 0, +i, -i, +1, -1
# z' = z(z**4 -1)
def X_polynome_exemple(X, Y):
    # return X**5 - 10 * X**3 * Y**2 + 5 * X * Y**4 - X
    X2 = X * X
    X3 = X2 * X
    Y2 = Y * Y
    return X3 * (X2 - 10 * Y2) + 5 * X * Y2 * Y2 - X
def Y_polynome_exemple(X, Y):
    # return 5 * X**4 * Y - 10 * X**2 * Y**3 + Y**5 - Y
    X2 = X * X
    Y2 = Y * Y
    Y3 = Y2 * Y
    return X2 * (5 * X2 * Y -10 * Y3) + Y3 * Y2 -Y

# La fonction carrée
# z' = z^2
def X_carre(X, Y):
    return X * X - Y * Y
def Y_carre(X, Y):
    return 2 * X * Y

def X_moins(X, Y):
    return -X
def Y_moins(X, Y):
    return -Y

# Gère si les fléches sont maintenues enfoncées ou non
class gestionnaire_evenements:
    def __init__(self):
        self.fleche_haut = False
        self.fleche_bas = False
        self.fleche_gauche = False
        self.fleche_droite = False
        
    def gerer(self, evenement):
        # Dernière fois que j'écris ça ========================================
        if evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_UP:    self.fleche_haut = True
            if evenement.key == pygame.K_DOWN:  self.fleche_bas = True
            if evenement.key == pygame.K_LEFT:  self.fleche_gauche = True 
            if evenement.key == pygame.K_RIGHT: self.fleche_droite = True
        if evenement.type == pygame.KEYUP:
            if evenement.key == pygame.K_UP:    self.fleche_haut = False
            if evenement.key == pygame.K_DOWN:  self.fleche_bas = False
            if evenement.key == pygame.K_LEFT:  self.fleche_gauche = False
            if evenement.key == pygame.K_RIGHT: self.fleche_droite = False
        #======================================================================

# Permet de tracer les antécédents (préimages) d'un plan complexe
class graphe_complexe:
    def __init__(self, Surface, X_fonction = X_polynome_exemple, Y_fonction = Y_polynome_exemple):
        self.surface = Surface
        self.largeur = Surface.get_width() / 2
        self.hauteur = Surface.get_height()

        self.X_fonction = X_fonction
        self.Y_fonction = Y_fonction
        
        self.preimages = [[[x,y] for y in range(self.hauteur)] for x in range(self.largeur)]

        # On coupe la fentre en deux partie:
        #  -une parite pour l'ensemble de départ de la fonction
        #  -une partie pour l'ensemble de départ de la fonction
        self.surface_ensemble_depart = pygame.Surface( (self.largeur, self.hauteur) )
        self.surface_ensemble_arrivee = pygame.Surface( (self.largeur, self.hauteur) )

        self.repere_gauche = repere(self.surface_ensemble_depart, 140)
        self.repere_droite = repere(self.surface_ensemble_arrivee, 120)

        self.precalculer_preimages()
            
        self.vitesse_defilement_image = 5
        self.x_image = self.largeur / 2
        self.y_image = self.hauteur / 2

        self.gestionnaire_evenements = gestionnaire_evenements()

    # On calcule une fois pour toute la position de l'image (dans la surface de droite)
    # en fonction de ses coorodonnées (dans la surface de gauche)
    def precalculer_preimages(self):
        print("Calculs en cours.")
        # Boucle sur tous les pixels de la surface de départ
        # pour chaque pixel on détermine la position de l'image
        for x in range(self.largeur):
            for y in range(self.hauteur):
                # Transformation des coorodonées en pixel
                # en coorodonnées dans le repère de gauche
                X = self.repere_gauche.X(x);
                Y = self.repere_gauche.Y(y);

                # Calcul mathématique de l'image
                X_image = self.X_fonction(X, Y)
                Y_image = self.Y_fonction(X, Y)

                # On repasse en coorodnnées en pixel dans le repère de droite
                x_image = self.repere_droite.x(X_image)
                y_image = self.repere_droite.y(Y_image)

                # Si l'image ne sort pas de la surface de droite
                if(x_image >= 0 and y_image >=0
                   and x_image < self.largeur and y_image < self.hauteur):
                    self.preimages[x][y] = [x_image, y_image] # Un tableau pour les abscisses et un pour les ordonnées serait peut-être mieux
                # sinon, ce qui arrive souvant vu que les modules se multiplient
                else:
                    self.preimages[x][y] = [0, 0]
        print("--> fait")

    def mise_a_jour(self):
        # Faire bouger l'image de la surface d'arrivée
        if(self.gestionnaire_evenements.fleche_haut):   self.y_image -= self.vitesse_defilement_image
        if(self.gestionnaire_evenements.fleche_bas):    self.y_image += self.vitesse_defilement_image
        if(self.gestionnaire_evenements.fleche_gauche): self.x_image -= self.vitesse_defilement_image
        if(self.gestionnaire_evenements.fleche_droite): self.x_image += self.vitesse_defilement_image

        # On efface tout
        self.surface_ensemble_depart.fill((255,255,255))
        self.surface_ensemble_arrivee.fill((200,200,200))

        # On trace l'image dans la surface de droite
        self.surface_ensemble_arrivee.blit(image, [self.x_image, self.y_image])

        # On trace les antécédents dans la surface de gauche
        # grâce à la table de correspondance
        tableau_gauche = pygame.PixelArray(self.surface_ensemble_depart)
        tableau_droite = pygame.PixelArray(self.surface_ensemble_arrivee)
        for x in range(self.largeur):
            for y in range(self.hauteur):
                tableau_gauche[x][y] = tableau_droite[self.preimages[x][y][0]][self.preimages[x][y][1]]
        del tableau_gauche
        del tableau_droite
    def afficher(self):
        self.repere_gauche.tracer()
        self.repere_droite.tracer()
        
        self.surface.blit(self.surface_ensemble_depart, [0,0])
        self.surface.blit(self.surface_ensemble_arrivee, [LARGEUR / 2,0])
        
if __name__ == '__main__':
    if(len(sys.argv) == 3):
        largeur_param = int(sys.argv[1])
        hauteur_param = int(sys.argv[2])
        if(largeur_param > 100 and largeur_param < 1500 and hauteur_param > 50 and hauteur_param < 800):
            LARGEUR = largeur_param
            HAUTEUR = hauteur_param
        else:
            print("Mauvais paramètres.")
            print("Le programme prend deux paramètres entiers: la largeur et la hauteur de la fenêtre, en pixels.")
            print("Exemple: python2 plan_complexe.py 600 300")
    else:
        # Taille de la fenêtre par défaut
        # Attention: la vitesse d'exécution du programme dépend directement du nombre de pixels
        LARGEUR = 600
        HAUTEUR = 300

    # Le menu
    print("Quel fonction voulez-vous utiliser?")
    print("0: z -> -z")
    print("1: z -> z^2")
    print("2: z -> z(z^4 - 1)")
    choix = int(input("Choix: "))

    print("Initialisation de pygame.")
    pygame.init()
    print("--> fait")
        
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))

    print("Importation de l'image.")
    # Peut être qu'il faudrait mettre cela dans la classe graphe_complexe
    # mais c'est pas sûr
    image = pygame.image.load('tux.png')
    ratio = float(image.get_width()) / image.get_height()
    image = pygame.transform.scale(image, [ LARGEUR / 4, int(LARGEUR / 4 / ratio)])
    print("--> fait")
    
    print("Création des deux repères.")
    # Instanciation du bouzin
    if( choix == 0):
        plan = graphe_complexe(ecran, X_moins, Y_moins)
    elif( choix == 1):
        plan = graphe_complexe(ecran, X_carre, Y_carre)
    else: 
        plan = graphe_complexe(ecran)    
    print("--> fait")

    fini = False
    while not fini:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                fini = True
            else:
                plan.gestionnaire_evenements.gerer(evenement)
        plan.mise_a_jour()
        plan.afficher()
        
        pygame.display.flip()
