"""
TODO: add attacks
Calculate next optimal platform using current best platform position
Also continue to include current next best platform based on current platform and not all time best
"""
import os
from random import randint
import pygame
from pygame.locals import *
from math import sqrt, sin, radians, cos
from time import sleep, time
from itertools import repeat
import pickle
import neat


# Centre la fenêtre sur l'écran de l'ordinateur
os.environ["SDL_VIDEO_CENTERED"] = "1"
# Crée la fenêtre et change son titre
org_screen = pygame.display.set_mode((0, 0), FULLSCREEN)
screen = org_screen.copy()
pygame.display.set_caption("Jeu de platformes")
# Définit la taille de la fenêtre
HAUTEUR_ÉCRAN = screen.get_height()
LARGEUR_ÉCRAN = screen.get_width()

clock = pygame.time.Clock()
# Définit les variable utilisées par le générateur (globales car les difficultés doivent pouvoir les modifier)
min_distance_y = 10
max_distance_y = 90
min_distance_x = 20
max_distance_x = 700
distance_max_deux_platformes = 350
distance_min_toutes_platformes = 125
vitesse = 360
# Définit la variable pour le mode disco
disco = False
# Définit les listes pour l'affichage des difficultés
difficultés = ['Facile', 'Moyen', 'Difficile', 'HARDCORE', 'Bizarre']
difficulté_active = [False, True, False, False, False]
# Donne le numéro du niveau en cours
niveau = 0


def reset_difficulté_active():
    """Met à False toutes les difficultés de la liste
    afin de les désactiver avant que une seule difficultée soit activée"""
    for i in range(len(difficulté_active)):
        difficulté_active[i] = False


def objets_texte(texte: str, police: pygame.font.Font) -> (list, list):
    """Une fonction qui retourne un texte comme surface, et le rectangle couvert par le texte

    :param texte: (str) qui est le texte destiné à être transformé en objet Surface
    :param police: la police du texte
    :return: le texte comme objet surface et le rectangle couvert par le texte
    """
    surface_texte = police.render(texte, True, (0, 0, 0))
    return surface_texte, surface_texte.get_rect()


def étiquette(texte: str, x: int, y: int, taile=30) -> None:
    """Une fonction qui crée une étiquette qui sera affichée aux coordonnées x et y

    :param texte: (str) le texte à afficher
    :param x: (int) la coordonnée horizontale de l'étiquette
    :param y: (int) la coordonnée vertical de l'étiquette
    :param taile: (int) la taille de la police de l'étiquette
    """
    font = pygame.font.Font(None, taile)
    objet_texte = font.render(texte, 1, (255, 255, 255))
    screen.blit(objet_texte, (x, y))


def boutton(msg: str, x: int, y: int, l: int, h: int, ci: tuple, ca: tuple, action=None) -> None:
    """Une fonction qui crée un boutton avec un message, aux coordonnées spécifiés et qui change de couleur lorsque
    l'utilisateur passe sa souris par dessus

    :param msg: (str) le texte à afficher sur le bouton
    :param x: (int) la coordonnée horizontale du boutton
    :param y: (int) la coordonnée verticale du boutton
    :param l: (int) la largeur du bouton
    :param h: (int) la hauteur du bouton
    :param ci: (tuple) la couleur RGB du boutton à l'état normal
    :param ca: (tuple) la couleur RGB du boutton lorsque l'utilisateur passe sa souris dessus
    :param action: (function) la fonction à éxécuter sur un click du boutton
    """
    souris = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    # Vérifie si la souris est sur le boutton
    if x+l > souris[0] > x and y+h > souris[1] > y:
        pygame.draw.rect(screen, ca, (x, y, l, h))
        # Si la souris est sur le boutton et qu'il y a un click, faire une action
        if click[0] == 1 and action is not None:
            action()
    else:
        # Change la couleur du boutton pendant que la souris est dessus
        pygame.draw.rect(screen, ci, (x, y, l, h))

    # Met comic sans ms comme police pour le texte du boutton
    police = pygame.font.SysFont("comicsansms", 20)
    surface_texte, rectangle_texte = objets_texte(msg, police)
    rectangle_texte.center = ((x + (l/2)), (y + (h/2)))
    # Affiche le texte et le rectangle coloré du boutton
    screen.blit(surface_texte, rectangle_texte)


def menu_général() -> None:
    """Une fonction qui affiche le menu général quand elle est appelée"""
    sleep(0.2)
    num_image = 10
    screen.fill((0, 0, 0))
    while True:
        # Vérifie si l'utilisateur quitte le jeu, si oui, ferme tout
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitter()

        num_image += 1
        # Fait fonctionner la vidéo qui joue comme fond d'écran
        background_image = pygame.image.load("Fond/2019-06-16 20-20-33 {:0>3}.jpg".format(num_image*2))
        screen.blit(background_image, [0, -30])
        if num_image*2 > 340:
            num_image = 10
        # Affiche les bouttons du menu
        boutton('Jouer', 870, 300, 150, 35, (0, 127, 0), (0, 255, 0), jeu)
        boutton('Aide/Tutoriel', 870, 400, 150, 35, (0, 0, 127), (0, 0, 255), menu_aide)
        boutton('Options', 870, 500, 150, 35, (127, 0, 0), (255, 0, 0), menu_options)
        boutton('Quitter', 870, 600, 150, 35, (127, 0, 0), (255, 0, 0), quitter)
        org_screen.blit(screen, (0, 0))
        pygame.display.update()
        clock.tick(60)


def quitter() -> None:
    """Une fonction qui quitte le jeu et arrête la musique quand elle est appelée"""
    pygame.mixer.stop()
    pygame.quit()
    exit()


def menu_options() -> None:
    """Une fonction qui affiche le menu options quand elle est appelée"""
    sleep(0.2)
    while True:
        # Vérifie si certaines touches sont préssées, et faire une action
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitter()
            if event.type == KEYDOWN:
                key = event.key
                if key == K_ESCAPE:
                    menu_général()
                    break
        # Affiche les bouttons de difficulté, ainsi que l'étiquette qui affiche la difficulté active
        screen.fill((0, 0, 0))
        for i in range(5):
            if difficulté_active[i]:
                étiquette("Difficulté : {}".format(difficultés[i]), 300, 400, 40)
        boutton(difficultés[0], 300, 500, 130, 35, (0, 127, 0), (0, 255, 0), difficulté_facile)
        boutton(difficultés[1], 500, 500, 130, 35, (0, 127, 0), (0, 255, 0), difficulté_moyenne)
        boutton(difficultés[2], 700, 500, 130, 35, (0, 127, 0), (0, 255, 0), difficulté_difficile)
        boutton(difficultés[3], 900, 500, 130, 35, (127, 0, 0), (255, 0, 0), difficulté_hardcore)
        boutton(difficultés[4], 1100, 500, 130, 35, (127, 0, 0), (255, 0, 0), difficulté_bizarre)
        # Change le texte du boutton disco s'il est allumé ou étient
        if disco:
            texte_btn_mode_disco = "Mode disco allumé"
        else:
            texte_btn_mode_disco = "Mode disco éteint"
        boutton(texte_btn_mode_disco, 1300, 500, 180, 35, (127, 0, 0), (255, 0, 0), mode_disco)
        # Affiche le boutton retour
        boutton("Retour", 300, 300, 130, 35, (0, 0, 127), (0, 0, 255), menu_général)
        # Affiche les bouttons pour changer de musique de fond
        étiquette("Musique : ", 300, 700, 40)
        boutton('Électronique 1', 300, 800, 160, 35, (0, 127, 0), (0, 255, 0), musique_électronique)
        boutton('Électronique 2', 500, 800, 160, 35, (0, 127, 0), (0, 255, 0), musique_électronique2)
        boutton('Bollywood', 700, 800, 160, 35, (0, 127, 0), (0, 255, 0), musique_bollywood)
        boutton('Super Mario', 900, 800, 160, 35, (0, 127, 0), (0, 255, 0), musique_mario)
        boutton('Aucune musique', 1100, 800, 160, 35, (0, 127, 0), (0, 255, 0), aucune_musique)
        org_screen.blit(screen, (0, 0))
        pygame.display.update()
        clock.tick(60)


def difficulté_facile() -> None:
    """Une fonction qui chansge les paramètres de génération pour que le niveau soit plus facile,
    ainsi que la vitesse du joueur, pour le rendre plus facile à contrôler"""
    global distance_min_toutes_platformes, vitesse, min_distance_y, distance_max_deux_platformes
    distance_min_toutes_platformes = 75
    vitesse = 100
    reset_difficulté_active()
    difficulté_active[0] = True


def difficulté_moyenne() -> None:
    """ Une fonction qui chansge les paramètres de génération pour que le niveau soit de difficultée moyenne,
    et remet toutes les valeurs aux valeurs par défaut"""
    global distance_min_toutes_platformes, vitesse
    distance_min_toutes_platformes = 100
    vitesse = 360
    reset_difficulté_active()
    difficulté_active[1] = True


def difficulté_difficile() -> None:
    """Une fonction qui chansge les paramètres de génération pour que le niveau soit plus difficile,
    ainsi que la vitesse du joueur, pour le rendre plus dur à contrôler"""
    global distance_min_toutes_platformes, vitesse, distance_max_deux_platformes
    distance_min_toutes_platformes = 150
    distance_max_deux_platformes = 400
    vitesse = 140
    reset_difficulté_active()
    difficulté_active[2] = True


def difficulté_hardcore() -> None:
    """Une fonction qui chansge les paramètres de génération pour que le niveau soit très dur.
    Génère fréquemment des niveaux impossibles. La vitesse du joueur est doublée, et l'écran pulse d'une couleur rouge"""
    global distance_min_toutes_platformes, distance_max_deux_platformes, vitesse
    distance_min_toutes_platformes = 160
    distance_max_deux_platformes = 400
    vitesse = 240
    reset_difficulté_active()
    difficulté_active[3] = True


def difficulté_bizarre() -> None:
    """ Une fonction qui chansge les paramètres de génération pour que le niveau soit étrange.
    Génère des niveaux parfois impossiblesm et avec un très grand nombre de platformes"""
    global distance_min_toutes_platformes, distance_max_deux_platformes, min_distance_y, max_distance_y, vitesse
    distance_min_toutes_platformes = 10
    distance_max_deux_platformes = 1000
    min_distance_y = 5
    max_distance_y = 30
    vitesse = 120
    reset_difficulté_active()
    difficulté_active[4] = True


def mode_disco() -> None:
    """Active ou désactive le mode disco (fond qui change de couleur très rapidement)"""
    global disco
    if disco:
        disco = False
    else:
        disco = True
        musique_bollywood()
    sleep(0.3)


def musique_électronique() -> None:
    """ Fait jouer de la musique électronique sur le clic du boutton"""
    pygame.mixer.music.stop()
    pygame.mixer.music.load("Musique/BlastProcessing.ogg")
    pygame.mixer.music.play(-1)


def musique_électronique2() -> None:
    """Fait jouer de la musique électronique sur le clic du boutton"""
    pygame.mixer.music.stop()
    pygame.mixer.music.load("Musique/BlastProcessing.ogg")
    pygame.mixer.music.play(-1)


def musique_bollywood() -> None:
    """ Fait jouer de la musique bollywood sur le clic du boutton"""
    pygame.mixer.music.stop()
    pygame.mixer.music.load("Musique/Bollywood.ogg")
    pygame.mixer.music.play(-1)


def musique_mario() -> None:
    """Fait jouer de la musique de mario sur le clic du boutton"""
    pygame.mixer.music.stop()
    pygame.mixer.music.load("Musique/Super Mario Bros.mp3")
    pygame.mixer.music.play(-1)


def aucune_musique() -> None:
    """Ne joue aucune musique et arrête la musique actuelle"""
    pygame.mixer.music.stop()


def menu_aide() -> None:
    """Affiche le menu d'aide pour expliquer à un nouveau joueur comment jouer"""
    while True:
        # Vérifie si des touches spécifiques sont préssées
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                key = event.key
                if key == K_ESCAPE:
                    menu_général()
                    break
        # Affiche les étiquettes qui décrivent le fontionnement du jeu, ainsi que un boutton retour
        screen.fill((0, 0, 0))
        étiquette("Contrôles :", 500, 300, 70)
        étiquette("Utiliser les flèches pour le déplacement", 500, 400)
        étiquette("ESC ou M pour revenir au menu (pendant le jeu)", 500, 450)
        étiquette("Si le niveau est impossible, appuyez sur R", 500, 500)
        étiquette("Une fois sur la platforme verte, sautez et le jeu passera au niveau suivant", 500, 550)
        étiquette("Avertissement : le mode disco consiste de couleurs éclatantes qui changent rapidement", 500, 800)
        boutton("Retour", 1100, 290, 130, 35, (0, 0, 127), (0, 0, 255), menu_général)
        org_screen.blit(screen, (0, 0))
        pygame.display.flip()
        clock.tick(60)


def partie_perdue(hauteur_lave: int, générateur, liste_de_sprites: pygame.sprite.Group) -> None:
    """Vérifie si le joueur touche la lave, si oui, afficher qu'il a perdu puis le faire retourner au menu

    :param hauteur_lave: (int) la hauteur de la lave depuis le haut de la fenêtre de jeu
    :param générateur: le générateur de niveaux, l'accès est donné pour pouvoir afficher les platformes
    :param liste_de_sprites: une liste qui contient le joueur, permet d'afficher le joueur
    """
    global niveau
    # Si le joueur touche la lave
    # Remet le niveau actif à 0
    niveau = 0
    # Dessiner tout le niveau et afficher qu'il a perdu
    générateur.draw()
    player.handle_keys()
    liste_de_sprites.update()
    liste_de_sprites.draw(screen)
    étiquette('Vous avez perdu!', 720, 400, 60)
    org_screen.blit(screen, (0, 0))
    pygame.display.flip()
    sleep(1)
    # Faire attendre le joueur 3 secondes avant que le jeu ne le ramène au menu
    for i in range(3):
        screen.fill((0, 0, 0))
        étiquette('Vous avez perdu!'.format(3 - i), 720, 400, 60)
        étiquette('Retour au menu dans {} secondes'.format(3 - i), 600, 500, 60)
        org_screen.blit(screen, (0, 0))
        pygame.display.flip()
        sleep(1)
    # Retoune le joueur au menu principal
    menu_général()


def modes_spéciaux(conteur: int, temps_niveau: float) -> int:
    """Définit les modes spéciaux pour le fond, ainsi que la lave

    :param conteur: (int) le nombre de fois que la boucle principale a joué
    :param temps_niveau: (float) le temps depuis lequel le joueur est sur le niveau
    :return: (int) la hauteur de la lave pour vérifier si le joueur perd
    """
    valeur_couleur_moitié = 127
    # Fait osciller les valeurs RGB pour les modes de fond spéciaux
    R = 127 + (valeur_couleur_moitié * (sin(radians(conteur))))
    G = 127 - (valeur_couleur_moitié * (sin(radians(conteur))))
    B = 127 + (valeur_couleur_moitié * (cos(radians(conteur))))
    hauteur_lave = screen.get_height() + 200
    if disco:
        # Mode disco -- fait changer le fond de couleur rapidement
        if conteur % 6 == 0:
            screen.fill((R, 0, B))
        elif conteur % 4 == 0:
            screen.fill((0, G, B))
        else:
            screen.fill((R, G, 0))

        # Lave normale -- fait monter progressivement la 'lave' après 10 secondes de jeu
        if time() - temps_niveau > 10:
            hauteur_lave = screen.get_height() + 200 - int((time() - temps_niveau) * 20)
            screen.fill((200, 50, 0), (0, hauteur_lave, screen.get_width(), 1060))
        else:
            étiquette("Lave dans {}s".format(round(10 - (time() - temps_niveau), 2)), 1760, 1060)
    elif difficulté_active[3]:
        screen.fill((R, 0, 0))
        # Lave hardcore -- fait monter progressivement la 'lave' après 5 secondes de jeu
        if time() - temps_niveau > 5:
            hauteur_lave = screen.get_height() + 200 - int((time() - temps_niveau) * 40)
            screen.fill((200, 50, 0), (0, hauteur_lave, screen.get_width(), 1060))
        else:
            étiquette("Lave dans {}s".format(round(5 - (time() - temps_niveau), 2)), 1760, 1060)
    else:
        screen.fill((0, 0, 0))
        # screen.fill((50, 0, 0), player.rect)
        # Lave normale -- fait monter progressivement la lave après 10 secondes de jeu
        if time() - temps_niveau > 10:
            hauteur_lave = screen.get_height() + 200 - int((time() - temps_niveau) * 20)
            screen.fill((200, 50, 0), (0, hauteur_lave, screen.get_width(), 1060))
        else:
            étiquette("Lave dans {}s".format(round(10 - (time() - temps_niveau), 2)), 1760, 1060)
    return hauteur_lave


def secouer():
    s = -1
    for _ in range(0, 5):
        for x in range(0, 30, 5):
            yield (x*s, 0)
        for x in range(30, 0, 5):
            yield (x*s, 0)
        s *= -1
    while True:
        yield (0, 0)


class Player(pygame.sprite.Sprite):
    """La classe du joueur, s'occupe de sa position et de son affichage"""
    def __init__(self, platformes, best=False):
        super().__init__()
        width = 40
        height = 40
        self.image = pygame.Surface([width, height])
        if best:
            self.image.fill((0, 255, 0))
        else:
            self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = (LARGEUR_ÉCRAN / 2) - 20
        self.rect.y = HAUTEUR_ÉCRAN - self.rect.height
        self.vitesse_x = 0
        self.vitesse_y = 0
        self.platformes = platformes
        self.best_platform = len(self.platformes.rect_list)
        self.touched_side = False
        self.all_ys = [1080]
        self.touching_platfrom = False

    def handle_keys(self) -> None:
        """ Une fonction qui vérifie si des touches spécifiques sont préssées,
        et qui appelle une fonction spécifique en fonction de la touche appuyée
        """
        global niveau
        for e in pygame.event.get():
            if e.type == QUIT:
                quitter()
            elif e.type == KEYDOWN:
                key = e.key
                if key == K_LEFT:
                    self.gauche()
                elif key == K_RIGHT:
                    self.droite()
                elif key == K_UP:
                    self.saut()
                elif key == K_DOWN:
                    self.slam()
                elif key == K_ESCAPE:
                    menu_général()
                elif key == K_m:
                    menu_général()
                elif key == K_r:
                    niveau -= 1
                    jeu()
                elif key == K_SPACE:
                    jeu()
            elif e.type == KEYUP:
                key = e.key
                if key == K_LEFT or key == K_RIGHT:
                    self.stop()

    def gravitée(self) -> None:
        """ Calcule la gravitée subie par le joueur"""
        # Ajoute progressivement à la vitesse verticale pour simuler la gravitée
        if self.vitesse_y == 0:
            self.vitesse_y = 0.2
        else:
            self.vitesse_y += .18

        # Met la vitesse verticale 0 si une des bordures verticales est touchée
        if self.rect.y >= HAUTEUR_ÉCRAN - self.rect.height and self.vitesse_y >= 0:
            self.vitesse_y = 0
            self.rect.y = HAUTEUR_ÉCRAN - self.rect.height
        elif self.rect.y <= 0 and self.vitesse_y < 0:
            self.vitesse_y = 0

    def update(self) -> None:
        """ Actualise la position du joueur, et s'occupe des collisions avec les platformes"""
        self.gravitée()
        self.rect.y += 2
        touche_platforme = pygame.sprite.spritecollide(self, self.platformes.platform_list, False)
        self.rect.y -= 2
        if len(touche_platforme) > 0:
            self.touching_platfrom = True
            for i in range(0, len(self.platformes.rect_list) - 1):
                if self.platformes.rect_list[i].rect.x - 40 < self.rect.x < self.platformes.rect_list[i].rect.right:
                    if self.platformes.rect_list[i].rect.top + 2 > self.rect.bottom > self.platformes.rect_list[i].rect.top - 2:
                        self.best_platform = i
        else:
            self.touching_platfrom = False
        # Appliquer les bordures de la fenêtre, pour empêcher le joueur de sortir
        if self.rect.x + self.rect.width >= LARGEUR_ÉCRAN and not self.vitesse_x < 0:
            self.vitesse_x = 0
            if self.rect.y > 600:
                self.touched_side = True
        elif self.rect.x <= 0 and not self.vitesse_x > 0:
            self.vitesse_x = 0
            if self.rect.y > 600:
                self.touched_side = True

        # Change la position en x en fonction de la vitesse en x
        if not self.touched_side:
            self.rect.x += self.vitesse_x
        liste_platformes_touchées = pygame.sprite.spritecollide(self, self.platformes.platform_list, False)
        for platforme in liste_platformes_touchées:
            # Si on bouge vers la droite,
            # mettre la coordonnée du côté droit du joueur à celle du côté gauche de l'objet
            # avec lequel on entre en collision
            if self.vitesse_x > 0:
                self.rect.right = platforme.rect.left
            elif self.vitesse_x < 0:
                # Si l'on se déplace dans l'autre sens, faire l'inverse
                self.rect.left = platforme.rect.right

        # Changer la position en y en fonction de la vitesse en y
        if not self.touched_side:
            self.rect.y += self.vitesse_y
        if self.vitesse_y > 11:
            liste_platformes_touchées = pygame.sprite.spritecollide(self, self.platformes.platform_list, False)
        else:
            liste_platformes_touchées = pygame.sprite.spritecollide(self, self.platformes.platform_list, False)
        if self.rect.bottom > 1070:
            self.best_platform = len(gen.rect_list) - 1
        for platforme in liste_platformes_touchées:
            # Si l'on descend, et que l'on de frappe pas un côté,
            # mettre la coordonnée du bas du joueur à celle du haut de l'objet avec lequel on entre en collision
            if self.vitesse_y > 0:
                self.rect.bottom = platforme.rect.top
            # Si l'on monte, faire l'inverse
            elif self.vitesse_y < 0:
                self.rect.top = platforme.rect.bottom

            self.vitesse_y = 0
        self.all_ys.append(self.rect.bottom)

    def gauche(self):
        """Met la vitesse horizontale à -4, ce qui va déplacer le joueur vers la gauche.
        Cette fonction est appelée lorsque la flèche gauche est appuyé en jeu"""
        self.vitesse_x = -4

    def droite(self):
        """Met la vitesse horizontale à 4, ce qui va déplacer le joueur vers la droite.
        Cette fonction est appelée lorsque la flèche droite est appuyé en jeu"""
        self.vitesse_x = 4

    def stop(self):
        """Met la vitesse en x à 0, ce qui arrête le joueur.
        Cette fonction est appelée lorque la flèche gauche ou la flèche droite est relachée"""
        self.vitesse_x = 0

    def saut(self):
        """Vérifie si le joueur est sur une platforme, ou sur le bas de l'écran.
        Si oui, met la vitesse verticale à -7 (vers le haut)"""
        self.rect.y += 2
        touche_platforme = pygame.sprite.spritecollide(self, self.platformes.platform_list, False)
        self.rect.y -= 2
        if len(touche_platforme) > 0 or self.rect.bottom >= HAUTEUR_ÉCRAN:
            self.vitesse_y = -7


    def slam(self):
        self.vitesse_y = 5

    def victoire(self) -> bool:
        """Vérifie si le joueur saute au-dessus de la platforme verte, si oui, renvoie VRAI"""
        if self.rect.bottom < 50:
            if self.rect.left < 840 < self.rect.right:
                return True


class Platforme(pygame.sprite.Sprite):
    """Une classe qui définit l'objet platforme"""
    def __init__(self, largeur, x, y, start=False):
        super().__init__()
        self.image = pygame.Surface([largeur, 10])
        if start:
            self.image.fill((0, 255, 0))
        else:
            R = randint(150, 255)
            G = 0
            B = 0
            self.image.fill((R, G, B))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Générateur:
    """Une classe qui génère les niveaux en fonction des règles prédéfinies"""
    def __init__(self):
        self.platform_list = pygame.sprite.Group()
        self.rect_list = []
        self.x = 800
        self.y = 150
        self.largeur = 80
        self.vérification_espacement_platforme = []

    def vérifie_distance_toutes_platformes(self, min_y):
        """Génère des nouvelles coordonnées pour une platforme et
        vérifie si la nouvelle platforme se situe à au moins (distance_min_toutes_platforme)

        :param min_y: (int) la hauteur minimale où se pourrait se situer la nouvelle platforme
        """
        global distance_min_toutes_platformes
        # Génère au hasard des coordonnées pour une nouvelle platforme
        self.x = randint(0, LARGEUR_ÉCRAN)
        self.y = randint(min_y, HAUTEUR_ÉCRAN)
        self.largeur = randint(40, 130)
        # Réinitialise la liste clear
        self.vérification_espacement_platforme.clear()
        for x in range(0, len(self.rect_list)):
            pos = self.rect_list[x - 1].rect.topleft
            pos2 = self.rect_list[x - 1].rect.topright
            # Calcule la distance entre la nouvelle platforme et les deux extrémités de toutes les anciennes
            distance = sqrt((self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2)
            distance2 = sqrt((self.x - pos2[0]) ** 2 + (self.y - pos2[1]) ** 2)
            # Si la platforme échoue une condition (trop proche d'une autre platforme), ajouter VRAI à la liste
            if distance < distance_min_toutes_platformes or distance2 < distance_min_toutes_platformes:
                self.vérification_espacement_platforme.append(True)
            else:
                self.vérification_espacement_platforme.append(False)

    def logique(self):
        """Génère le niveau, en vérifiant si la position est valide, si oui, crée une platforme aux coordonnées crées"""
        global min_distance_y, max_distance_y, min_distance_x, max_distance_x, distance_min_toutes_platformes, niveau
        count = 0
        while self.y < screen.get_height() - 80:
            if count == 0:
                # Crée la première platforme qui a des coordonnées et une taille fixe
                block = Platforme(self.largeur, self.x, self.y, start=True)
                block.rect.x = self.x
                block.rect.y = self.y
                self.rect_list.append(block)
                self.platform_list.add(block)
            else:
                # Crée toutes les autres platformes
                pos_prev = self.rect_list[count - 1].rect.topleft
                self.vérifie_distance_toutes_platformes(pos_prev[1] + 10)
                # Calcule la distance entre la platforme potentielle et l'ancienne platforme
                distance = sqrt((self.x - pos_prev[0]) ** 2 + (self.y - pos_prev[1]) ** 2)
                temps_début_des_calculs = time()
                # Vérifie si la nouvelle platforme correspond aux règles du générateur
                # sinon, générer une nouvelle platforme
                while not (max_distance_x > abs(self.x - pos_prev[0]) > min_distance_x
                           and max_distance_y > self.y - pos_prev[1] > min_distance_y) or any(
                        self.vérification_espacement_platforme) or distance > distance_max_deux_platformes:
                    self.vérifie_distance_toutes_platformes(pos_prev[1] + 10)
                    distance = sqrt((self.x - pos_prev[0]) ** 2 + (self.y - pos_prev[1]) ** 2)
                    # Si le temps de génération du niveau est trop long, relancer la génération
                    if time() - temps_début_des_calculs > 5:
                        niveau -= 1
                        jeu()
                # Une fois que les conditions sont remplies, créer la nouvelle platforme
                block = Platforme(self.largeur, self.x, self.y)
                block.rect.x = self.x
                block.rect.y = self.y
                self.rect_list.append(block)
                self.platform_list.add(block)
            count += 1

    def update(self):
        """Met à jour la liste de platformes pour pygame"""
        self.platform_list.update()

    def draw(self):
        """Dessine toutes les platformes de la liste"""
        self.platform_list.draw(screen)


def jeu(genomes, config):
    """Fait fonctionner le jeu, appelle le générateur et dessine tous les objets"""
    global disco, niveau, gen, prev_best_horizontal, prev_best_vertical, action
    niveau += 1
    players = []
    nets = []
    ge = []
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player(gen))
        g.fitness = 0
        ge.append(g)

    # Initialise le générateur de niveau
    screen.fill((0, 0, 0))
    # Dessine le joueur
    # Génère le niveau

    gen.update()
    liste_de_sprites = pygame.sprite.Group()
    for p in players:
        liste_de_sprites.add(p)
    # Crée des variables nécéssaires pour certains modes spéciaux/pour la génération de la lave
    count = 1
    temps_niveau = time()
    # Boucle principale du jeu
    gen.draw()
    offset = repeat((0, 0))
    while True:
        hauteur_lave = modes_spéciaux(count, temps_niveau)
        for i, player in enumerate(players):
            player.update()
            optimal_platform = calculate_optimal_platform(player, i)
            ge[i].fitness = 1080 - min(players[i].all_ys)
            ge[i].fitness -= 0.05
            output = nets[i].activate((player.vitesse_y, player.vitesse_x, player.touching_platfrom, player.platformes.rect_list[player.best_platform - 1].rect.width, (player.rect.x - player.platformes.rect_list[player.best_platform - 1].rect.x), (player.rect.y - player.platformes.rect_list[player.best_platform - 1].rect.y)))
            # output = nets[i].activate((player.rect.x, player.rect.y, player.vitesse_x, player.vitesse_y, player.touching_platfrom, player.platformes.rect_list[player.best_platform - 1].rect.width, player.platformes.rect_list[player.best_platform - 1].rect.x, player.platformes.rect_list[player.best_platform - 1].rect.y))
            if output[0] > 0.5:
                players[i].saut()
            if output[1] > 0.5:
                players[i].droite()
            if output[2] > 0.5:
                players[i].gauche()
            if players[i].rect.y + 40 > hauteur_lave:
                players.pop(i)
                nets.pop(i)
                ge.pop(i)
        if len(players) <= 1:
            break
        étiquette('Generation {}'.format(niveau), 10, 10)
        # Dessine les ennemis
        # Dessine les platformes
        gen.draw()
        #for i in range(0, len(gen.rect_list) - 1):
            #étiquette(str(i), gen.rect_list[i].rect.x, gen.rect_list[i].rect.y + 20)
        # Écoute pour les touches_appuyées
        # Affiche le joueur
        liste_de_sprites.update()
        liste_de_sprites.draw(screen)
        # Limite les FPS
        clock.tick(vitesse)
        # Met à jour l'écran
        org_screen.blit(screen, next(offset))
        pygame.display.flip()
        count += 1


def determine_best_player(players):
    best_y = 1080
    best_player = None
    action_num = 0
    for i in range(0, len(players)):
        for x in range(10, len(players[i].all_ys)):
            if players[i].all_ys[x] <= best_y:
                best_y = players[i].all_ys[x]
                best_player = i

    return best_player


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(jeu, 50)


def calculate_optimal_platform(player, i):
    current_best_platform = [player.platformes.rect_list[player.best_platform].rect.x, player.platformes.rect_list[player.best_platform].rect.y]
    prev_optimal_platform = len(player.platformes.rect_list) - 1
    for x in range(0, len(player.platformes.rect_list) - 1):
        if 0 < current_best_platform[1] - player.platformes.rect_list[x].rect.y < 120:
            x_distance = current_best_platform[0] - player.platformes.rect_list[x].rect.x
            if abs(x_distance) < 150:
                optimal_platform = x
                if optimal_platform < prev_optimal_platform:
                    prev_optimal_platform = optimal_platform
    return prev_optimal_platform


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_file = os.path.join(local_dir, "config.txt")
    # Initialise pygame et la classe joueur
    pygame.init()
    # Lance la musique et le menu général
    aucune_musique()
    prev_best_horizontal = None
    prev_best_vertical = None
    action = None
    gen = Générateur()
    gen.logique()
    run(config_file)
