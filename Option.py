import csv

""" Gère les options et les données chargées 
 	Permet de charger et sauvegarder les groupes disponibles en csv
 	
 	Cette classe est initialisée dans le fichier. On préfèrera donc utiliser l'instance Option.option, plus qu'instancier une nouvelle classe
"""
class Option:
	
	def __init__(self):
		self.group_file = "group.data"
		self.period_file = "period.data"
		self.loadPeriod()
	
	def loadGroup(self):
		group_dict = {}
		
		with open(self.group_file) as csvfile:
			reader = csv.reader(csvfile, delimiter=' ')
		
			for row in reader:
				group_dict[row[0]] = row[1]
				
		csvfile.close()
		
		return group_dict
		
	def saveGroup(self, new_group_dict):
		with open(self.group_file, 'w') as csvfile:
			writer = csv.writer(csvfile, delimiter=' ')
		
			for group, code in new_group_dict.items():
				writer.writerow([group, code])
			
	
	def loadPeriod(self):
		f = open(self.period_file, 'r')
		
		self.startWeek = int(f.readline())
		self.endWeek = int(f.readline())
		self.nbWeek = self.endWeek - self.startWeek +1
		self.nbDayInWeek = int(f.readline())
		self.nbSlotInDay = int(f.readline())
		
	
	def savePeriod(self, newNbWeek, newNbDayInWeek, newNbSlotInDay):
		f = open(self.period_file, 'w')
		
		f.write(str(newNbWeek) + "\n" + str(newNbDayInWeek) + "\n" + str(newNbSlotInDay))
			
	
option = Option()
