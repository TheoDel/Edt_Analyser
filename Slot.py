from datetime import time

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
				(7, Slot(time(18,30), time(19,30)))
]
