import Option
import Slot

class Resultat:
	
	def __init__(self, nom):
		self.nom = nom
		self.result = [1]*(Option.option.nbWeek*Option.option.nbDayInWeek*Option.option.nbSlotInDay) #At the beggining, all the slots are free
		
	def compare(self, other_result, nomComparaison):
		return Resultat(nomComparaison, list(map(etbit, self.result, other_result)))

	def toString(self):
		res = self.nom + "\n\n"
		
		indexLibre = [i for i,item in enumerate(self.result) if item == 1]
		tripletLibre = map(indexToTriplet, indexLibre)
		allStr = map(tripletToString, tripletLibre)
		
		for tripletStr in allStr:
			res += tripletStr + "\n"
			
		return res
		
		
def tripletToString(triplet):
	convertDay = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
	slot = [s for i,s in Slot.defaultSlots if i == triplet[2]][0]

	return "Semaine " + str(triplet[0]) + " " + convertDay[triplet[1]-1] + " " + slot.toString()
	
""" Recréé un triplet (semaine, jour, créneau) à partir de l'index du créneau dans un tableau d'emploi du temps """	
def indexToTriplet(index):
	week = int(index / (Option.option.nbDayInWeek * Option.option.nbSlotInDay)) + Option.option.startWeek
	day = int((index % (Option.option.nbDayInWeek * Option.option.nbSlotInDay)) / Option.option.nbSlotInDay) + 1
	time = int((index % (Option.option.nbDayInWeek * Option.option.nbSlotInDay)) % Option.option.nbSlotInDay)

	return week, day, time
		
""" Effectue un et binaire entre deux bit """
def etbit(x, y): # comparaison logique d'indices de deux horaires
        # identique de deux groupes différents
        return x & y
        
r = Resultat("Coucou")
