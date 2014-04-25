#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Autheur: Matthieu Riou <matthieu.riou@etu.univ-nantes.fr>
# Version: v0.1
# Versions de python supportées: 3.3+ (à cause d'icalendar)
# Dépendances: icalendar, requests (pip install ; utiliser virtualenvwrapper)
# Notes: Pour choisir les groupes, aller remplir la fonction à la toute
# fin du programme.
# ToDo: Développer une interface graphique.

try:
        import codecs # support des encodages
        from datetime import datetime # time manipulation functions
        from datetime import time 
        from icalendar import Calendar # support des .ics
        import locale # support of local locale (oh really ?), and internationalization
        import pytz # accurate timezone calculations
        from pytz import utc
        import requests # permet de réaliser simplement (plus qu'avec urllib2) des
        # requêtes HTTP
        import getpass # permet d'utilier getpass.getpass([prompt[, stream]]) pour
        # demander un mot de passe
except ImportError:
        raise ImportError("Modules are required to run this program. Try `pip install icalendar requests`.")
        exit

# VARIABLE GLOBALES
correspondance_group_tab = {"L3_Info" : "g11529", "M1_Atal" : "g78030", "L2_401" : "g93283", "L2_402" : "g115774", "L2_419" : "g7127","M1_Alma" : "g6935","M1_Oro" : "g9238", "L1_245" : "g51728", "L1_247" : "g94501", "L1_248" : "g115113", "L1_243K" : "g7057"}
horaire_to_heure = ["8h00", "9h30", "11h00", "12h30", "14h00", "15h30", "17h00", "18h30"]

# VARIABLES GLOBALES à décommenter pour accélérer les tests (default: "")
# login = ""
# mdp = ""





class GestionDatetime:
	
	def __init__(self):
		self.paris = pytz.timezone('Europe/Paris')
		self.format = "%Y%m%dT%H%M%SZ"
        #datefind = datetime(2014, 4, 16, 11) # careful: 04 is invalid. 4
        # is. (octal numbers not allowed in python!)
        #find = datefind.strftime("%d/%m/%Y/%Hh%M")
        #ffind = utc.localize(datefind)
        #fffind = ffind.astimezone(paris)	
	
	
	def getDatetime(self, my_date):
		date = my_date.to_ical()
		dtutcdate = utc.localize(datetime.strptime(date.decode(), self.format))
		dtdate = dtutcdate.astimezone(self.paris)

		return dtdate

class Connexion:
	
	def __init__(self):
		self.login = input("Login : ")
		self.mdp = getpass.getpass("Mot de passe : ")

		self.correspondance_group_tab = {"L3_Info" : "g11529", "M1_Atal" : "g78030", "L2_401" : "g93283", "L2_402" : "g115774", "L2_419" : "g7127","M1_Alma" : "g6935","M1_Oro" : "g9238", "L1_245" : "g51728", "L1_247" : "g94501", "L1_248" : "g115113", "L1_243K" : "g7057"}


	def connect(self, group):
		code_group = self.correspondance_group_tab[group]

		request = requests.get(
						'https://edt.univ-nantes.fr/sciences/' + code_group + '.ics',
						auth=(self.login, self.mdp),
						timeout=2)
		if not 200 <= request.status_code < 300:
			print("Error status while retrieving the ics file for group " + group + ".")
			exit

		return request


class Edt:

	def __init__(self):
		self.start = 2 #Semaine de départ
		self.end = 20 #Semaine de fin
		self.nbWeek = self.end - self.start + 1
		self.nbDayInWeek = 6 #Nombre de jour par semaine
		self.nbSlotInDay = 8 #Nombre de créneaux par jour

		self.connexion = Connexion()
		self.edt = {}

		self.nbSlot = self.nbWeek * self.nbDayInWeek * self.nbSlotInDay

		self.gestionDate = GestionDatetime()

	def addEdt(self, group):
		if group not in self.edt:
			e = self.connexion.connect(group)
			self.edt[group] = self.analyseEdt(e)


	def analyseEdt(self, edt): 

		slots = [1]*self.nbSlot #At the beggining, all the slots are free

		for component in Calendar.from_ical(edt.text).walk():
			if component.name == 'VEVENT':
				start = self.gestionDate.getDatetime(component.get('DTSTART'))
				end = self.gestionDate.getDatetime(component.get('DTEND'))

				getCrenaux(slots, start, end)
				        
		return slots


	def compare(self, list_groups):
		if not all(group in self.edt for group in list_groups) : #try except ?
			print("Erreur, groupe non présent")
			exit(1)

		res = []

		for group in list_groups:
			#Hou ! Le vilain test à chaque tour de boucle pour un seul cas qui se retrouve ici maintenant !
			#Mais j'ai pas trop trouvé comment faire autrement. Iterateur ?
			if len(res) == 0: 
				res = self.edt[group]
			else:
				res = map(etbit, res, self.edt[group]) #No need to convert it in list here, because we'll just iterate over it (with an other map)

		return list(res) #Must be convert here, because we want to return a list, and not an iterators (map object)

	def compareAll(self):
		if len(self.edt) == 0: #try except ?
			print("Erreur, il faut des groupes à comparer")
			exit(1)

		return self.compare(self.edt)





def getCrenaux(crenaux, start, end): #Pour le semestre 2 de 2014
        
	isodate = start.isocalendar() #tuple (annee, semaine, jour de 1 a 7)

	index = (isodate[1]-2) * 48
	index = index + (isodate[2]-1) * 8

	if intersect(time(8), time(9, 20), start.time(), end.time()):
		crenaux[index + 0] = 0

	if intersect(time(9, 30), time(10, 50), start.time(), end.time()):
		crenaux[index + 1] = 0

	if intersect(time(11), time(12, 20), start.time(), end.time()):
		crenaux[index + 2] = 0

	if intersect(time(12, 30), time(13, 50), start.time(), end.time()):
		crenaux[index + 3] = 0

	if intersect(time(14), time(15, 20), start.time(), end.time()):
		crenaux[index + 4] = 0

	if intersect(time(15, 30), time(16, 50), start.time(), end.time()):
		crenaux[index + 5] = 0

	if intersect(time(17), time(18, 20), start.time(), end.time()):
		crenaux[index + 6] = 0


def intersect(start1, end1, start2, end2):
        return (start1 <= start2 <= end1) or (start2 <= start1 <= end2)






def etbit(x, y): # comparaison logique d'indices de deux horaires
        # identique de deux groupes différents
        return x & y




def affiche_result(liste):
	for i, item in enumerate(liste):
		if item == 1:
			affiche_creneau(i)


def affiche_creneau(x): # indice x. en fonction de l'indice qui varie de 1
        # à 912, on affiche les semaine, jour et horaire de l'indice.
        semaine = int(x / 48)
        jour = int((x - semaine*48) / 8)
        horaire = int(x - semaine*48 - jour*8)
        
        heure = horaire_to_heure[horaire]
        
        if jour + 1 != 6 and heure != "12h30" and heure != "18h30" and semaine+2 == 18:
                print("Semaine {} jour {} horaire {}".format(semaine+2, jour+1, heure))




def main(tableauGroupe): # raccourci final d'utilisation
	try:
		edt = Edt()
		edt.addEdt("L1_245")
		edt.addEdt("L1_248")
		affiche_result(edt.compareAll())
	except (KeyboardInterrupt, SystemExit):
		exit # quitte sans rien dire pour les évènements Ctrl-C, Ctrl-Q
                
# main(["L1_245", "L1_247", "L1_248", "L1_243K", "L2_401", "L2_402",
#       "L2_419", "M1_Alma", "M1_Atal", "M1_Oro"])
main(["L1_245", "L1_248"])
