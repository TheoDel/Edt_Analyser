#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Autheur: Matthieu Riou <matthieu.riou@etu.univ-nantes.fr>
# Version: v0.1
# Versions de python supportées: 3.3+ (à cause d'icalendar)
# Dépendances: icalendar, requests (pip install ; utiliser virtualenvwrapper)
# Notes: Pour choisir les groupes, aller remplir la fonction à la toute
# fin du programme.
# ToDo: Modulariser la fonction appelante à la fin du programme ;
# Commenter ; Développer une interface graphique.

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

# VARIABLE GLOBALES
correspondance_group_tab = {"L3_Info" : "g11529", "M1_Atal" : "g78030", "L2_401" : "g93283", "L2_402" : "g115774", "L2_419" : "g7127","M1_Alma" : "g6935","M1_Oro" : "g9238", "L1_245" : "g51728", "L1_247" : "g94501", "L1_248" : "g115113", "L1_243K" : "g7057"}
horaire_to_heure = ["8h00", "9h30", "11h00", "12h30", "14h00", "15h30", "17h00", "18h30"]
request = ""

def order(group):
        req = connect(group) # objet reçu de la connexion via la
                # fonction connect. se connecte et définit request.
        paris = pytz.timezone('Europe/Paris')
        format = "%Y%m%dT%H%M%SZ"
        datefind = datetime(2014, 4, 16, 11) # careful: 04 is invalid. 4
        # is. (octal numbers not allowed in python!)
        find = datefind.strftime("%d/%m/%Y/%Hh%M")
        ffind = utc.localize(datefind)
        fffind = ffind.astimezone(paris)
        
        #semaine de 4 à 22 (19 semaine)
        #semaine de 6 jour
        #jour de 8 crénaux 
        #tableau de 19 * 6 * 8 = 912 case
        
        crenaux = [1]*912
        
        for component in Calendar.from_ical(req.text).walk():
                if component.name == 'VEVENT':
                        start = component.get('DTSTART').to_ical()
                        dtutcstart = utc.localize(datetime.strptime(start.decode(), format))
                        dtstart = dtutcstart.astimezone(paris)
                        fstart = dtstart.strftime("%d/%m/%Y/%Hh%M")
                        
                        end = component.get('DTEND').to_ical()
                        dtutcend = utc.localize(datetime.strptime(end.decode(), format))
                        dtend = dtutcend.astimezone(paris)
                        fend = dtend.strftime("%d/%m/%Y/%Hh%M")
        
                        getCrenaux(crenaux, dtstart, dtend)
                        
        return crenaux

def getCrenaux(crenaux, start, end): #Pour le semestre 2 de 2014
        
        isodate = start.isocalendar() #tuple (annee, semaine, jour de 1 a 7)
        
        index = (isodate[1]-4) * 48
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
        
def affiche_cours(start, end, description):
        format = "%Y%m%dT%H%M%SZ"
        paris = pytz.timezone('Europe/Paris')
        
        dtutcstart = utc.localize(datetime.strptime(start, format))
        dtutcend = utc.localize(datetime.strptime(end, format))
        dtstart = dtutcstart.astimezone(paris)
        dtend = dtutcend.astimezone(paris)
        result = u"Prochain cours le {date} de {start} à {end}".format(
                date=dtstart.strftime("%A %d/%m/%Y"),
                start=dtstart.strftime("%Hh%M"),
                end=dtend.strftime("%Hh%M"))
        
        return result

def etbit(x, y): # comparaison logique d'indices de deux horaires
        # identique de deux groupes différents
        return x & y

def compare_local(crenaux1, crenaux2):
        result = map(etbit, crenaux1, crenaux2)
        return result

def affiche_result(x): # indice x. en fonction de l'indice qui varie de 1
        # à 912, on affiche les semaine, jour et horaire de l'indice.
        semaine = x / 48
        jour = (x - semaine*48) / 8
        horaire = int(x - semaine*48 - jour*8)
        
        heure = horaire_to_heure[horaire]
        
        if jour + 1 != 6 and heure != "12h30" and heure != "18h30" and (semaine == 13 or semaine == 14):
                print("Semaine {} jour {} horaire {}".format(semaine+4, jour+1, heure))

def compare(liste_crenaux):
        if len(liste_crenaux) == 1:
                lst = list(liste_crenaux[0]) # on rend la liste subscriptable
                for x in range(len(lst)):
                        if lst[x] == 1:
                                affiche_result(x)

                return liste_crenaux
        else:
                crenaux1 = liste_crenaux.pop()
                crenaux2 = liste_crenaux.pop()
                liste_crenaux.append(compare_local(crenaux1, crenaux2))
                return compare(liste_crenaux)

def ordergroup(liste_group):
        liste_result = []
        for group in liste_group:
                liste_result.append(order(group))

        return list(liste_result)

def correspondance_group(group):
        global correspondance_group_tab
        return correspondance_group_tab[group]


def main(tableauGroupe): # raccourci final d'utilisation
        try:
                edtParGroupe = ordergroup(list(map(correspondance_group, tableauGroupe)))
                # grouplist est la liste des groupes, de la forme suivante:
                # ["L1_245", "L1_247", ...]
                compare(edtParGroupe)
        except (KeyboardInterrupt, SystemExit):
                exit # quitte sans rien dire pour les évènements Ctrl-C, Ctrl-Q

# main(["L1_245", "L1_247", "L1_248", "L1_243K", "L2_401", "L2_402",
#       "L2_419", "M1_Alma", "M1_Atal", "M1_Oro"])
main(["L1_245", "M1_Oro"])
