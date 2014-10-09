import requests # permet de réaliser simplement (plus qu'avec urllib2) des requêtes HTTP
import getpass # permet d'utilier getpass.getpass([prompt[, stream]]) pour demander un mot de passe

class Connexion:
	
	""" Demande le login et le mot de passe à l'initilisation de la classe et initialise les groupes disponibles
		Les mêmes identifiants seront utilisés pour tous les appels à connect()
	"""
	def __init__(self):
		self.login = input("Login : ")
		self.mdp = getpass.getpass("Mot de passe : ")

		self.correspondance_group_tab = {"L3_Info" : "g11529", "M1_Atal" : "g78030", "L2_301" : "g19843", "L2_302" : "g7094", "L2_319" : "g19844","M1_Alma" : "g6935","M1_Oro" : "g9238", "L1_245" : "g51728", "L1_247" : "g94501", "L1_248" : "g115113", "L1_243K" : "g7057", "M2_Alma" : "g6984", "M2_Atal" : "g78125", "M2_Oro" : "g16684"}

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

