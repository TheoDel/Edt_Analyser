import GestionDatetime
import Connexion
import Slot
import Filtre
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

		self.filtres = {}

		self.convertDay = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


	""" Ajoute un groupe à comparer et analyse son emploi du temps 
		Se connecte à l'emploi du temps en ligne pour récupérer l'emploi du temps du groupe ajouté
	"""
	def addGroup(self, group):
		if group not in self.edt:
			e = self.connexion.connect(group)
			self.edt[group] = self.analyseEdt(e)

	""" Supprime un groupe de la liste des groupes à comparer """
	def removeGroup(self, group):
		if group in self.edt:
			del self.edt[group]

	""" Ajoute un filtre pour l'affichage des résultats """
	def addFiltre(self, name, filtre):
		if name not in self.filtres:
			self.filtres[name] = filtre

	""" Supprime un filtre """
	def removeFiltre(self, name):
		if name in self.filtres:
			del self.filtres[name]
			

	""" Analyse l'emploi du temps donné en paramètre 
		Extrait les informations de l'emploi du temps au format ics
		Transforme ses informations dans le format souhaité :
			Tableau de self.nbSlot cases, trié par semaine, puis par jour, puis par créneaux
				Exemple d'ordre : [Semaine 1 Lundi 8h à 9h20, Semaine 1 Lundi 9h30 à 11h, ... Semaine 1 Mardi 8h à 9h20, ..., Semaine 2 Lundi 8h à 9h20, ...]
			Chaque case contient : 1 si le créneau est libre, 0 sinon
	"""
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

	""" Retourne un index à partir d'une date
		L'index correspond à l'index dans un tableau d'emploi du temps du premier créneau du jour de la date passée en paramètre
	"""
	def getIsoIndex(self, datetime):
		isodate = datetime.isocalendar() #tuple (years, week, day) day from 1 to 7

		index = (isodate[1] - self.startWeek) * self.nbDayInWeek * self.nbSlotInDay
		index += (isodate[2] - 1) * self.nbSlotInDay

		return index


	""" Compare entre eux une liste de groupes
		Comparer deux groupes consiste à faire un et binaire pour chaque créneau
		Pour comparer plusieurs groupes, on compare les deux premiers groupes, puis le resultat de la comparaison avec le troisième groupes, etc...
	"""
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


	""" Compare tous les groupes qui ont été ajouté à la liste des groupes """
	def compareAll(self):
		if len(self.edt) == 0: #try except ?
			print("Erreur, il faut des groupes à comparer")

		if len(self.filtres) == 0: #try except ?
			print("Erreur, il faut définir des filtres")

		return self.compare(self.edt)


	""" Recréé un triplet (semaine, jour, créneau) à partir de l'index du créneau dans un tableau d'emploi du temps """	
	def indexToResult(self, index):
		week = int(index / (self.nbDayInWeek * self.nbSlotInDay)) + self.startWeek
		day = int((index % (self.nbDayInWeek * self.nbSlotInDay)) / self.nbSlotInDay) + 1
		time = int((index % (self.nbDayInWeek * self.nbSlotInDay)) % self.nbSlotInDay)

		return week, day, time

	""" Affiche la date du créneau à partir du triplet (semaine, jour, créneau) """
	def resultToString(self, result):
		slot = [s for i,s in Slot.defaultSlots if i == result[2]][0]

		return "Semaine " + str(result[0]) + " " + self.convertDay[result[1]-1] + " " + slot.toString()


	""" Compare les groupes qui ont été ajouté, puis affiche les résultats """
	def compareAndPrint(self):
		allResults = self.compareAll()
		
		results_tmp = [i for i,item in enumerate(allResults) if item == 1]

		results = map(self.resultToString, [item for item in map(self.indexToResult, results_tmp) if any(filtre.isIn(item) for filtre in self.filtres.values())])

		for e in results:
			print(e)
			
	
	""" Compare les groupes passés en paramètres deux à deux
		Si on a 3 groupe, on aura alors la comparaison du groupe1 avec le groupe2, du groupe1 avec le groupe3, et du groupe2 avec le groupe3
	"""	
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


	""" Compare les groupes ajoutés deux à deux
		Appelle la fonction compareEachtoEach
	"""
	def compareAllEachToEach(self):
		if len(self.edt) == 0: #try except ?
			print("Erreur, il faut des groupes à comparer")

		if len(self.filtres) == 0: #try except ?
			print("Erreur, il faut définir des filtres")

		return self.compareEachToEach(list(self.edt))


	""" Compare les groupes ajoutés deux à deux, puis affiche les résultats """
	def compareEachToEachAndPrint(self):
		allResults = self.compareAllEachToEach()

		for res in allResults:
			print("Comparaison entre " + res['groupe1'] + " et " + res['groupe2'] + " :")
			
			results_tmp = [i for i,item in enumerate(res['resultat']) if item == 1]

			results = map(self.resultToString, [item for item in map(self.indexToResult, results_tmp) if any(filtre.isIn(item) for filtre in self.filtres.values())])

			for e in results:
				print(e)

			print("\n")
			
	""" Affiche les créneaux par chaque groupe ajoutés (sans comparaison) """
	def listForAllGroupsAndPrint(self):
	
		for group, group_edt in self.edt.items():
			print("Créneaux pour " + group + " :")
			
			results_tmp = [i for i,item in enumerate(group_edt) if item == 1]

			results = map(self.resultToString, [item for item in map(self.indexToResult, results_tmp) if any(option.isIn(item) for option in self.options.values())])

			for e in results:
				print(e)
			
			print("\n")

	""" Renvoie la liste des groupes disponibles """
	def groupAvailable(self):
		groups =  list(self.connexion.correspondance_group_tab.keys())
		groups.sort()
		return groups






""" Effectue un et binaire entre deux bit """
def etbit(x, y): # comparaison logique d'indices de deux horaires
        # identique de deux groupes différents
        return x & y
        
