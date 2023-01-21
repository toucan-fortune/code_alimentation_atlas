"""
###########################################################################
#                              Projet Intégrateur
# Étudiant: Linus Levi
# Cours: 420-321-AH
# Date: 17/01/2023
#
#
#
###########################################################################
"""

import datetime
from random import randint, choice, random, seed # pour le test
import sys
import math
from projet_noeud import Noeud
from time import sleep
from projet_basedonnees import BaseDonnees
from projet_prive_pc import topic


metriques = ["brute", "moy_10_sec", "moy_15_sec", "moy_20_sec", "moy_30_sec", "moy_60_sec",
                      "moy_10_min", "moy_15_min", "moy_20_min", "moy_30_min", "moy_60_min"]


njours = 1  # nombre de jours
nnoeuds = 1 # nombre de noeuds
pas = 15    # en secondes
attente = 0.01 # en secondes


def main():
    seed()

    """
    Avant d'aller en production, il est impératif de vérifier plusieurs choses pour ne pas
    se retrouver avec des résultats désagréables. Tout au long du code se trouve des
    indications de vérification, apparaissant comme "Vérification #"
    Utiliser l'outil de recherche pour les repérer facilement
    """

    nombre_de_documents = 0

    # On essaie d'instancier un objet bdd
    try:
        # Vérification 0: se trouve dans le fichier de la bdd (le nom de la bdd et sa collection)
        bdd = BaseDonnees("Production") # Vérification 1
    except:
        print("'bdd' n'est pas valide")
        sys.exit()

    # la liste des noeuds (capteurs)
    nombre_de_noeuds = nnoeuds  # Vérification 2
    noeuds = [Noeud() for i in range(nombre_de_noeuds)]
    noeuds[0].capteur = "temperature"  # toujours une capteur de température

    # Obtention de la date et l'heure ainsi que quelques calculs relatifs
    aujourdhui = datetime.datetime.now()
    annee = aujourdhui.year
    mois = aujourdhui.month
    jour = aujourdhui.day

    decalage = 24 - randint(0, 5) # en heures

    # les unités des minutes et de l'angle
    # On établit une intervalle par laquelle on divisera une heure de temps (60 minutes)
    # pour établir la grandeur de notre pas (mesuré en minutes)

    # Vérification 3
    intervalle = pas # la grandeur de pas (en minutes)
    tranches = 60 / intervalle # le nombre de tranches par heure

    # L'angle, lui, s'étale sur toute une journée (24 heures), on a donc besoin de savoir
    # le nombre de tranches en 24 heures et le diviser par ce nombre.
    inc_ang = 180.0 / (24.0 * tranches) # incrément de l'angle (degrés) par tranche dans 24 heures

    # le décallage est utilisé pour décaller la courbe de température et d'humidité
    # relatif au cycle des heures.
    # Lorsque non-décallé, l'angle est remis à 0 en même temps que le début du cycle d'heures
    # Lorsque décallé, l'angle commence par une valeur qui représente le décallage et se remet
    # à zéro lorsqu'il atteint 180.0 ou plus. Cela se traduit par une valeur d'angle qui
    # correspond à:
    angle = decalage * tranches * inc_ang
    # Cela veut dire le nombre d'heures de décallage, multiplié par le nombre de tranches
    # dans une heure, multiplié par le nombre de degrés par tranche

    print("Debut:", datetime.datetime.now() )
    print("insertion des documents...")

    # Pour les fins de notre démonstration, on doit produire des valeurs réalistes
    # Quoique pour du temps réel on utilise la fonction datetime.datetime.now()
    # pour notre démonstration, puisqu'on simule plusieurs capteurs ainsi que
    # les dates et les heures, on utilise le montage suivant:

    for jour in range(jour, jour + njours): # Vérification 4
        for heure in range(0, 24):
            for minute in range(0, 60, intervalle):
                # les angles sont indépendants du cycle d'heures en raison du décallage
                if angle > 180:
                    angle = 0 # on recommence depuis le début

                # On produit le facteur utilisé pour les calculs
                sinus = math.sin(angle/57.3) # 57.3 pour convertir en radians

                # On génère des données pour chaque capteur
                for noeud in noeuds:
                    # on s'occupe de la temperature et de l'humidité. Cette dernière est l'inverse
                    # de la température. Lorsque la température est élevée, l'humidité est
                    # à son plus bas niveau, et lorsque la température est à son plus bas,
                    # c'est l'humidité qui est à son plus haut

                    noeud.temperature = round(noeud.tmp_min + (noeud.jeu_tmp * sinus) + 3 * random(), 3)
                    noeud.humidite = round(noeud.hum_max - (noeud.jeu_hum * sinus) + 3 * random(), 3)

                    date_et_heure = str(annee) + "-" + str(mois) + "-" + str(jour) + " " + \
                    str(heure) + ":" + str(minute) + ":00.000000"

                    # La valeur de l'enregistrment dépend de la grandeur mesurée
                    if noeud.capteur == "temperature":
                        valeur = noeud.temperature
                    else:
                        valeur = noeud.humidite

                    # le document est préparé, puis inséré
                    document = { "datetime" : date_et_heure,
                                 "noeud"    : noeud.ID,
                                 "capteur"  : noeud.capteur,
                                 "metrique" : metriques[0],
                                 "valeur"   : valeur }

                    # ATTENTION: ne PAS imprimer en production
                    #print(document)          # Vérification 6

                    try: # la véritable insértion des documents
                        #bdd.inscrireDocument( document ) # Vérification 7
                        nombre_de_documents += 1
                        print(document)
                        pass
                    except:
                        print("erreur d'enregistrement")
                        # peut être un problème de connexion
                        sleep(1) # bref delai pour réconnexion

                    # bref délai afin d'eviter de stresser, le module Wifi
                    # le modem, le fournisseur, et le nuage
                    sleep(attente)    # Vérification 8

                # fin de la boucle 'for' des noeuds
                angle += inc_ang
            # fin de la boucle 'for' des minutes
        # fin de la boucle 'for' des heures
    # fin de la boucle 'for' des jours

    print(nombre_de_documents, "documents traités")
    print("Fin:", datetime.datetime.now() )

    bdd.deconnexion() # Vérification 9

    print("'main' terminé")


if __name__ == '__main__':
    main()
