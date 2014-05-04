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
	from datetime import date
	from datetime import time 
	from icalendar import Calendar # support des .ics
	import locale # support of local locale (oh really ?), and internationalization
	import pytz # accurate timezone calculations
	from pytz import utc
	import requests # permet de réaliser simplement (plus qu'avec urllib2) des
	# requêtes HTTP
	import getpass # permet d'utilier getpass.getpass([prompt[, stream]]) pour
	# demander un mot de passe
	import sys
except ImportError:
	raise ImportError("Modules are required to run this program. Try `pip install icalendar requests`.")
	exit



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
			exit(1)

		return request


class Edt:

	def __init__(self):
		self.startWeek = 2 #Semaine de départ
		self.endWeek = 24 #Semaine de fin
		self.nbWeek = self.endWeek - self.startWeek + 1
		self.nbDayInWeek = 6 #Nombre de jour par semaine
		self.nbSlotInDay = 8 #Nombre de créneaux par jour

		self.connexion = Connexion()
		self.edt = {}

		self.nbSlot = self.nbWeek * self.nbDayInWeek * self.nbSlotInDay

		self.gestionDate = GestionDatetime()

		self.options = {}

		self.convertDay = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

	def addEdt(self, group):
		if group not in self.edt:
			e = self.connexion.connect(group)
			self.edt[group] = self.analyseEdt(e)

	def removeEdt(self, group):
		if group in self.edt:
			del self.edt[group]

	def addOption(self, name, option):
		if name not in self.options:
			self.options[name] = option

	def removeOption(self, name):
		if name in self.options:
			del self.options['name']


	def analyseEdt(self, edt): 

		slots = [1]*self.nbSlot #At the beggining, all the slots are free

		for component in Calendar.from_ical(edt.text).walk():
			if component.name == 'VEVENT':
				start = self.gestionDate.getDatetime(component.get('DTSTART'))
				end = self.gestionDate.getDatetime(component.get('DTEND'))

				isoIndex = self.getIsoIndex(start)

				slot = Slot(start.time(), end.time())


				for index, defaultSlot in defaultSlots:
					if slot.intersect(defaultSlot): #If the slot intersect with a default slot
						slots[isoIndex + index] = 0 #This default slot isn't free

				        
		return slots

	def getIsoIndex(self, datetime):
		isodate = datetime.isocalendar() #tuple (years, week, day) day from 1 to 7

		index = (isodate[1] - self.startWeek) * self.nbDayInWeek * self.nbSlotInDay
		index += (isodate[2] - 1) * self.nbSlotInDay

		return index

	def compare(self, list_groups): #Oh Oh ! Work for both list and dictionnary, it seems
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
				res = list(map(etbit, res, self.edt[group])) #Actually, we need to convert it in list, because we test len(res) after

		return list(res) #Must be convert here, because we want to return a list, and not an iterators (map object)

	def compareAll(self):
		if len(self.edt) == 0: #try except ?
			print("Erreur, il faut des groupes à comparer")

		if len(self.options) == 0: #try except ?
			print("Erreur, il faut définir des options")

		return self.compare(self.edt)

	
	def indexToResult(self, index):
		week = int(index / (self.nbDayInWeek * self.nbSlotInDay)) + self.startWeek
		day = int((index % (self.nbDayInWeek * self.nbSlotInDay)) / self.nbSlotInDay) + 1
		time = int((index % (self.nbDayInWeek * self.nbSlotInDay)) % self.nbSlotInDay)

		return week, day, time

	def resultToString(self, result):
		slot = [s for i,s in defaultSlots if i == result[2]][0]

		return "Semaine " + str(result[0]) + " " + self.convertDay[result[1]-1] + " " + slot.toString()

	def compareAndPrint(self):
		allResults = self.compareAll()
		
		results_tmp = [i for i,item in enumerate(allResults) if item == 1]

		results = map(self.resultToString, [item for item in map(self.indexToResult, results_tmp) if any(option.isIn(item) for option in self.options.values())])

		for e in results:
			print(e)

	def compareAllEachToEach(self):
		if len(self.edt) == 0: #try except ?
			print("Erreur, il faut des groupes à comparer")

		if len(self.options) == 0: #try except ?
			print("Erreur, il faut définir des options")

		return self.compareEachToEach(list(self.edt))

	def compareEachToEach(self, list_group):
		if len(list_group) == 0: #try except ?
			print("Erreur, il faut des groupes à comparer")

		if len(list_group) == 1:
			return []
		else:
			res = []

			group = list_group[0]
			other_group = list_group[1:]

			for group2 in other_group:
				res.append({'groupe1' : group, 'groupe2' : group2, 'resultat' : self.compare([group, group2])})

			
			res.extend(self.compareEachToEach(other_group))

			return res

	def compareEachToEachAndPrint(self):
		allResults = self.compareAllEachToEach()

		for res in allResults:
			print("Comparaison entre " + res['groupe1'] + " et " + res['groupe2'] + " :")
			
			results_tmp = [i for i,item in enumerate(res['resultat']) if item == 1]

			results = map(self.resultToString, [item for item in map(self.indexToResult, results_tmp) if any(option.isIn(item) for option in self.options.values())])

			for e in results:
				print(e)

			print("\n")

	def groupAvailable(self):
		groups =  list(self.connexion.correspondance_group_tab.keys())
		groups.sort()
		return groups

class Slot:

	def __init__(self, start, end): #Only hours, not day, week and years
		
		self.start = start
		self.end = end

	def intersect(self, otherSlot):
		return (self.start <= otherSlot.start <= self.end) or (otherSlot.start <= self.start <= otherSlot.end)

	def toString(self):
		return "de " + self.start.strftime("%Hh%M") + " à " + self.end.strftime("%Hh%M")


defaultSlots = [
				(0, Slot(time(8), time(9,20))),
				(1, Slot(time(9,30), time(10, 50))),
				(2, Slot(time(11), time(12,20))),
				(3, Slot(time(12,30), time(13,50))),
				(4, Slot(time(14), time(15,20))),
				(5, Slot(time(15,30), time(16,50))),
				(6, Slot(time(17), time(18,20))),
				(7, Slot(time(18,20), time(19,30)))
]


class Option: #Filter slots we want
	
	def __init__(self, listWeek, listDay, listSlot):
		self.listWeek = listWeek
		self.listDay = listDay
		self.listSlot = listSlot

	def toString(self):
		return "Semaines " + str(self.listWeek) + "  Jours " + str(self.listDay) + "  Créneaux " + str(self.listSlot)

	def isIn(self, result): #result : (week, day, slot)
		return result[0] in self.listWeek and result[1] in self.listDay and result[2] in self.listSlot





def etbit(x, y): # comparaison logique d'indices de deux horaires
        # identique de deux groupes différents
        return x & y

