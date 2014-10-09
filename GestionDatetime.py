from datetime import datetime # time manipulation functions
from datetime import date
from datetime import time
import locale # support of local locale (oh really ?), and internationalization
import pytz

""" Permet l'extraction des dates au format voulu, et dans la timezone de Paris """
class GestionDatetime:
	
	""" Initialise la timezone et le format """
	def __init__(self):
		self.paris = pytz.timezone('Europe/Paris')
		self.format = "%Y%m%dT%H%M%SZ"	
	
	""" Formate proprement la date passé en paramètre """
	def getDatetime(self, my_date):
		date = my_date.to_ical()
		dtutcdate = pytz.utc.localize(datetime.strptime(date.decode(), self.format))
		dtdate = dtutcdate.astimezone(self.paris)

		return dtdate
