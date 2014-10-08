import GestionDatetime
import Connexion
import Slot
import Option
from icalendar import Calendar # support des .ics

class Edt:

	def __init__(self):
		self.startWeek = 37 #Semaine de départ
		self.endWeek = 51 #Semaine de fin
		self.nbWeek = self.endWeek - self.startWeek + 1
		self.nbDayInWeek = 6 #Nombre de jour par semaine
		self.nbSlotInDay = 8 #Nombre de créneaux par jour

		self.connexion = Connexion.Connexion()
		self.edt = {}

		self.nbSlot = self.nbWeek * self.nbDayInWeek * self.nbSlotInDay

		self.gestionDate = GestionDatetime.GestionDatetime()

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
			del self.options[name]


	def analyseEdt(self, edt): 

		slots = [1]*self.nbSlot #At the beggining, all the slots are free

		for component in Calendar.from_ical(edt.text).walk():
			if component.name == 'VEVENT':
				start = self.gestionDate.getDatetime(component.get('DTSTART'))
				end = self.gestionDate.getDatetime(component.get('DTEND'))

				isoIndex = self.getIsoIndex(start)

				slot = Slot.Slot(start.time(), end.time())


				for index, defaultSlot in Slot.defaultSlots:
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
		slot = [s for i,s in Slot.defaultSlots if i == result[2]][0]

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
			
	def listForAllGroupsAndPrint(self):
	
		for group, group_edt in self.edt.items():
			print("Créneaux pour " + group + " :")
			
			results_tmp = [i for i,item in enumerate(group_edt) if item == 1]

			results = map(self.resultToString, [item for item in map(self.indexToResult, results_tmp) if any(option.isIn(item) for option in self.options.values())])

			for e in results:
				print(e)
			
			print("\n")

	def groupAvailable(self):
		groups =  list(self.connexion.correspondance_group_tab.keys())
		groups.sort()
		return groups







def etbit(x, y): # comparaison logique d'indices de deux horaires
        # identique de deux groupes différents
        return x & y
        
