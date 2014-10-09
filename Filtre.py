""" Permet de filter les créneaux voulu, d'après la semaine, le jour et/ou l'horaire """
class Filtre: #Filter slots we want
	
	""" Définie le filtre d'après une liste de semaine, une liste de jour (de la semaine) et une liste d'horaire """
	def __init__(self, listWeek, listDay, listSlot):
		self.listWeek = listWeek
		self.listDay = listDay
		self.listSlot = listSlot

	""" Affiche le filtre """
	def toString(self):
		return "Semaines " + str(self.listWeek) + "  Jours " + str(self.listDay) + "  Créneaux " + str(self.listSlot)

	""" Vérifie si un créneaux est accepté par le filtre """
	def isIn(self, result): #result : (week, day, slot)
		return result[0] in self.listWeek and result[1] in self.listDay and result[2] in self.listSlot
