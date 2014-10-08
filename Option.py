class Option: #Filter slots we want
	
	def __init__(self, listWeek, listDay, listSlot):
		self.listWeek = listWeek
		self.listDay = listDay
		self.listSlot = listSlot

	def toString(self):
		return "Semaines " + str(self.listWeek) + "  Jours " + str(self.listDay) + "  Créneaux " + str(self.listSlot)

	def isIn(self, result): #result : (week, day, slot)
		return result[0] in self.listWeek and result[1] in self.listDay and result[2] in self.listSlot
