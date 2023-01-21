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

import pymongo # pour windows, il faut rouler le serveur à partir d'un cmd
from time import sleep
from projet_prive_pc import URI_mongodb


class BaseDonnees():

    def __init__( self, nom ):
        self.nom = "MongoDB"
        self.document_count = 0

        # ouverture de la connexion avec le serveur MongoDB
        try:
            print( self.nom + ": Pymongo version", pymongo.version)
            self.client = pymongo.MongoClient(  host = URI_mongodb,
                                                #timeoutMS = 5,
                                                #socketTimeoutMS = 5,
                                                #connectTimeoutMS = 10,
                                                appname = nom )

            print(self.nom + ": connexion en cours...")
            sleep(1)

            # on établit la bdd et la collection
            self.db = self.client.toucan   # Verification 1
            self.collection = self.db.tempreel  # Verification 2
            print( self.nom + ": connecté à MongoDB")
            #print(self.client.server_info())
        except:
            print( self.nom + ": ERREUR - La connexion à Mongo n'a pu se faire" )
            return


    def inscrireDocument( self, document ):
        try:
            self.collection.insert_one( document ) # Verification 3
            self.document_count += 1
        except:
            print( self.nom + ": ERREUR - L'ajout de messages n'a pas pu être effectué" )


    def recupererDonnees(self, limite):
        # on retourne une liste de documents (messages)
        try:
            return list( self.collection.find().sort( "_id", pymongo.DESCENDING).limit( limite ) )
        except:
            print(self.nom + ": ERREUR - La lecture de messages n'a pas pu être effectué" )


    def deconnexion(self):
        if self.client is not None:
            self.client.close()
            print(self.nom + ": " + str(self.document_count) + " documents insérés")
            print(self.nom + ": déconnecté" )


# -------------------------------- TESTS -------------------------------------


def main():
    print("début du test")
    obj = BaseDonnees("test")
    obj.deconnexion()
    print("test terminé")
    pass


if __name__ == '__main__':
    main()