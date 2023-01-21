"""
###########################################################################
#                                Projet 2
# Étudiant: Linus Levi
# Cours: 420-315-AH (Développement d’objets intelligents)
# Date: 04/07/2022
#
# Fichier: - messagerie.py -
# Renferme la classe Messagerie, qui abstrait la connection avec MQTT
# et offre des méthodes
# de réception et envoi de messages
#
###########################################################################
"""

import paho.mqtt.client as mqtt
from globales import *


#host          = "test.mosquitto.org"
host          = "node02.myqtthub.com"
# port          = 1883
# clean_session = True
client_id     = "repi_pico_001"
username      = "toucanfortune"
password      = "X3K7aWtNerDF"


def on_connect(client, userdata, flags, response_code):
    print( userdata.nom + ": Connexion MQTT" ) # (code "+ str(response_code)+ ")" )

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")


def on_message(client, userdata, message):
    contenu = str(message.payload.decode("utf-8"))
    print( userdata.nom + " : message reçu:", contenu )
    userdata.traiteMessages( contenu )


class Messagerie():

    def __init__( self, parent, nom, sujets: list ):

        self.nom = nom
        self.sujets = sujets  # liste de sujets à écouter

        # on obtient une interface à mosquitto
        try:
            self.client = mqtt.Client( client_id = client_id, clean_session = True )
        except:
            print( "ERREUR " + self.nom + " : " + "le client MQTT n'a pu être crée" )
            return

        # on établit quelques paramètres
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.user_data_set(parent) # on passe le parent au callbacks
        self.client.username_pw_set(username, password) # pour l'authentification

        # on tente de se connecter au serveur
        try:
            # host = MQTT_BROKER (lorsque local)
            self.client.connect( host = host, port = port, keepalive = 60 )
        except:
            print( "ERREUR " + self.nom + " : " + "connexion à MQTT n'a pu se faire" )
            return

        # on se souscrit aux sujets à écouter et on démarre le fil
        self.inscrire(sujets)
        self.client.loop_start()
        print( self.nom + ": Attente des messages MQTT" )


    def inscrire(self, sujets: list): # s_inscrir
        for sujet in self.sujets:
            # ce serait bien de vérifier si le sujet existe déjà
            # donc de nous faire une liste de sujets auxquels on est inscrits
            self.client.subscribe( sujet )


    def desinscrire(self, sujets: list):
        # on devrait prendre la liste des sujets de la classe
        for sujet in self.sujets:
            self.client.unsubscribe(sujet)


    def publieMessages(self, sujet, valeur):
        self.client.publish( sujet, valeur )
        print( "Publié au sujet " + sujet, " : valeur: ", valeur )


    def termine(self):
        if self.client is not None:
            self.client.loop_stop()
            # on se désinscrit des sujets et on se déconnecte
            print(self.nom + ": désinscription des sujets...")

            self.desinscrire() # attention aux paramètre

            self.client.disconnect()
            print(self.nom + ": Déconnexion MQTT")


    def __del__(self):
        #print(self.nom + ": destructeur() MQTT")
        pass


# objet pour tests ci-bas
class Obj():

    def __init__(self, nom):
        self.nom = nom

    def traiteMessages(self):
        print("je traite les messages")



def main():

    # ici je suis prêt pour former le message
    payload = {
        "date": "09-01-2023",
        "heure": "13:35",
        "mid": "Ecole"
    }

    # ici on roule le teste
    obj = Obj("Objet")
    messagerie = Messagerie( obj, "Test", ["Bonjour"] ) # le sujet d'inscription est Bonjour
    messagerie.publieMessages( "bonjour", 5 )
    messagerie.termine()
    print( "programme terminé" )


if __name__ == '__main__':
    main()