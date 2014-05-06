import edt_analyser

class Menu:
	def __init__(self, titre, commands, racc):
		self.titre = titre
		self.racc = racc
		self.commands = commands


	def help(self, command = None):
		if not command:
			print(self.titre)
			print("Tapez q ou quit pour retourner au menu précédent")
			print("Tapez h ou help pour revoir ce message")
			for k,v in self.commands.items():
				print("Tapez", k, "pour", v['help'])
		else:
			print(self.commands[command]['details'])

	def wait(self):

		print(self.titre)

		command = [""]

		while not(command[0] == 'q' or command[0] == 'quit'):
			print()				
			command = input(self.racc + ">> ").split()
			print()

			try:
				if command[0] == 'h' or command[0] == 'help':
					if len(command) > 1:
						self.help(command[1])
					else:
						self.help()
				elif command[0] in self.commands:
					value = self.commands[command[0]]
					arguments = command[1:value['args']+1]

					if len(arguments) != value['args'] :
						print("Erreur, cette commande nécéssite", value['args'], "arguments.")
					else:
						value['fct'](*arguments)

				elif command[0] == 'q' or command[0] == 'quit':
					print("Retour au menu précédent")
				else:
					print("Cette commande n'existe pas, tapez h ou help pour plus d'informations")
			except (KeyboardInterrupt):
				print("\nCommande annulée")
			except (Exception):
				print("Erreur lors de l'éxécution")

class Interface:
	def __init__(self):
		self.edt = edt_analyser.Edt()
		option = edt_analyser.Option([18], [2,3], [0,1,2,4,5,6])
		option2 = edt_analyser.Option([15], [1], [0,1,2,4,5,6])
		self.edt.addOption("1", option)
		self.edt.addOption("2", option2)

		self.menuGroups = Menu("Interface de gestion des groupes",
								{
									'add' : {'fct' : lambda g : self.edt.addEdt(g), 'args' : 1, 'help' : "ajouter un groupe",
											'details' : 
												"Ajoute un groupe à analyser.\n"
												"Prend un argument : le groupe.\n\n"
												"Vous pouvez voir les groupes disponibles en tapant la commande info dans l'interface de gestion des groupes.\n\n"
												"Exemple : add L1_245"
											},
									'remove' : {'fct' : lambda g : self.edt.removeEdt(g), 'args' : 1, 'help' : "enlever un groupe",
												'details' : 
													"Enlève un groupe à analyser.\n"
													"Prend un argument : le groupe.\n\n"
													"Vous pouvez voir les groupes prévu pour l'analyse en tapant la commande info dans l'interface de gestion des groupes.\n\n"
													"Exemple : remove L1_245"
												},
									'info' : {'fct' : lambda : self.infoGroups(), 'args' : 0, 'help' : "afficher des informations sur les groupes", 
												'details' : 
													"Affiche des informations sur les groupes.\n"
													"Ne prend aucun argument.\n\n"
													"Affiche les groupes disponibles, ainsi que ceux prêts à être analysés."
											}
								}, 'Groups ')

		self.menuOption = Menu("Interface de gestion des options",
								{
									'add' : {'fct' : lambda n, w,d,s : self.addOption(n, w,d,s), 'args' : 4, 'help' : "ajouter une option",
											'details' : 
												"Ajoute une option pour l'analyse.\n"
												"Prend 4 arguments : le nom donné à l'option, les semaines à analyser, les jours et les créneaux.\n\n"
												"On donne un nom à l'option pour la retrouver après.\n"
												"Une option comprends : \n \t- un tableau de semaines, données par leurs numéros dans l'année\n"
												"\t- un tableau de jours, donnés par leurs numéros dans la semaine (de 1 à 6, le dimanche n'est pas analysable)\n"
												"\t- un tableau de créneaux, numérotés de 0 à 7 :\n"
												"\t\t 0 : de 8h à 9h20\n"
												"\t\t 1 : de 9h30 à 10h50\n"
												"\t\t 2 : de 11h à 12h20\n"
												"\t\t 3 : de 12h30 à 13h50\n"
												"\t\t 4 : de 14h à 15h20\n"
												"\t\t 5 : de 15h30 à 16h50\n"
												"\t\t 6 : de 17h à 18h20\n"
												"\t\t 7 : de 18h30 à 19h30\n\n"
												"Tapez la commande info pour les options déjà ajoutées.\n\n"
												"Exemple : add semaine18 18 2,3 0,1 = Les créneaux de 8h à 11h le mardi et le mercredi de la semaine 18"
											},
									'remove' : {'fct' : lambda n : self.edt.removeOption(n), 'args' : 1, 'help' : "supprimmer une option",
												'details' :
													"Supprime une option pour l'analyse.\n"
													"Prend 1 argument : le nom de l'option.\n\n"
													"Supprime l'option dont le nom est passé en paramètre.\n"
													"Vous pouvez connaître les noms des options ajoutées en tapant la commande info.\n\n"
													"Exemple : remove semaine18\n"
												},
									'info' : {'fct' : lambda : self.infoOption(), 'args' : 0, 'help' : "afficher des informations sur les options",
												'details' :
													"Affiche des informations sur les options.\n"
													"Ne prend aucun argument.\n\n"
													"Donne le nom et le détails des options ajoutées pour l'analyse."
											}
								}, 'Options ')

		self.menuInterface = Menu("Interface de l'Edt Analyser",
								{
									'option' : {'fct' : lambda : self.menuOption.wait(), 'args' : 0, 'help' : "gérer les options",
												'details' :
													"Amène à l'interface de gestion des options.\n"
													"Ne prend aucun argument."
												},
									'groups' : {'fct' : lambda : self.menuGroups.wait(), 'args' : 0, 'help' : "gérer les groupes",
												'details' :
													"Amène à l'interface de gestion des groupes.\n"
													"Ne prend aucun argument."
												},
									'launch' : {'fct' : lambda : self.edt.compareAndPrint(), 'args' : 0, 'help' : "lancer le programme",
												'details' :
													"Lance le programme.\n"
													"Ne prend aucun argument.\n\n"
													"Appelle la fonction compareAndPrint() et trouve les créneaux libres pour tous les groupes ajoutés."
												},
									'compareEach' : {'fct' : lambda : self.edt.compareEachToEachAndPrint(), 'args' : 0, 'help' : "compare chaque groupe avec tous les autres",
														'details' : 
															"Compare chaque groupe avec tous les autres.\n"
															"Ne prend aucun argument.\n\n"
															"Appelle la fonction compareEachToEachAndPrint() et trouve les créneaux libres pour chaque pair de groupe possible."
													}
								}, '')

		self.menuInterface.wait()

		print("Au revoir !")


	def infoGroups(self):
		groupsAvailable = self.edt.groupAvailable()
		groupsAdded = list(self.edt.edt.keys())
		groupsAdded.sort()

		print("Groupes disponibles :")
		print(groupsAvailable)
		print("Groupes déjà ajoutés :")
		print(groupsAdded)

	def infoOption(self):
		for k,v in self.edt.options.items():
			print(k, " : ", v.toString())

	def addOption(self, name, weeks, days, slots):
		listWeek = [int(w) for w in weeks.split(',')]
		listDay = [int(d) for d in days.split(',')]
		listSlot = [int(s) for s in slots.split(',')]

		option = edt_analyser.Option(listWeek, listDay, listSlot)
		self.edt.addOption(name, option)

		print(self.edt.options)
		

try:		
	Interface()
except (KeyboardInterrupt, SystemExit):
	print("\nAu revoir")
	exit
