import requests # permet de réaliser simplement (plus qu'avec urllib2) des requêtes HTTP
import getpass # permet d'utilier getpass.getpass([prompt[, stream]]) pour demander un mot de passe

import Option

class Connexion:
	
	""" Demande le login et le mot de passe à l'initilisation de la classe et initialise les groupes disponibles
		Les mêmes identifiants seront utilisés pour tous les appels à connect()
	"""
	def __init__(self):
		self.login = input("Login : ")
		self.mdp = getpass.getpass("Mot de passe : ")

		self.correspondance_group_tab = Option.option.loadGroup()

	""" Se connecte à l'emploi du temps en ligne et télécharge celui du groupe passé en paramètre """
	def connect(self, group):
		code_group = self.correspondance_group_tab[group]

		request = requests.get(
						'https://edt.univ-nantes.fr/sciences/' + code_group + '.ics',
						auth=(self.login, self.mdp),
						timeout=2)

		if not 200 <= request.status_code < 300:
			print("Error status while retrieving the ics file for group " + group + ".")
			exit(1)

		return request

