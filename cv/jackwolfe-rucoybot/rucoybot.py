import rucoyadb
import time
from random import randint

class RucoyBot():
	def __init__(self, mode, bpq, weapon, special, usepots, pottime, serial, ratio, ipaddr):
		#initialize bot dicts and values, etc.
		self.mode = mode
		self.bpq = bpq
		self.weapon = weapon
		self.special = special
		self.usepots = usepots
		hptime, mptime, _ = self.splitandint(pottime)
		self.hp = 100
		self.maxhp = 100
		self.mp = 100
		self.maxmp = 100
		self.hptime = hptime
		self.mptime = mptime
		self.adb = rucoyadb.AdbLib(mode='fast')
		self.adb.setserial(serial)
		self.adb.setratio(ratio)
		self.monster_ids = {}
		self.monster_distances = {}
		self.drop_ids = {}
		self.drop_distances = {}
		self.coords = '0'
		self.old_coords = '0'
		self.plzlist = [':']*10
		self.atktgt = ''
		self.droptgt = ''
		self.next_action = ''
		self.last_actions = ['']*10
		self.blacklist = {}
		self.darker_than_blacklist = []
		self.last_attack = 9000000000
		self.last_forgive = 0
		self.last_hppot = 0
		self.last_mppot = 0
		self.swordname = ''
		self.bowname = ''
		self.wandname = ''
		self.forgiven = []
		self.super_hp_pots = '0'
		self.great_hp_pots = '0'
		self.normal_hp_pots = '0'
		self.start_time = time.time()
		self.begone_count = 0
		self.need_screenshot = True
		self.pauseplz = False
		self.ipaddr = ipaddr
		self.switchplz = False
		self.tempignore = []
		self.bagfull = False
		
	def update_hp(self, hp, maxhp):
		self.hp = hp
		self.maxhp = maxhp
	
	def update_mp(self, mp, maxmp):
		self.mp = mp
		self.maxmp = maxmp
		
	def update_monsters(self, monster_id, monster_info, force=''):
		x, y, z = self.splitandint(self.coords)
		mx, my, mz = self.splitandint(monster_info.split(':')[1]) 
		if z != mz:
			return
		
		if force != 'force':
			if monster_id in self.darker_than_blacklist:
				return
			black_ids = [x.split('@')[0] for x in self.blacklist]
			if monster_id in black_ids:
				for key in self.blacklist:
					if key.startswith(monster_id):
						self.blacklist[key] = monster_info
				return
		
		self.monster_ids[monster_id] = monster_info # monster_info contains monster name & coords
	
	def update_monster_distances(self):
		if self.coords == '0':
			if self.next_action.split('@')[0] == 'step3':
				return
			self.prettyprint("Fatal Error: I don't know my own coordinates.")
			self.adb.restartrucoy()
			self.next_action = 'step3@{}'.format(time.time()+5)
			return
		
		x, y, z = self.splitandint(self.coords)
		
		for monster_id in self.monster_ids:
			monster_x, monster_y, monster_z = self.splitandint(self.monster_ids[monster_id].split(':')[1])
			if z != monster_z:
				pass
			monster_distance = abs(monster_y - y) + abs(monster_x - x)
			self.monster_distances[monster_id] = monster_distance
	
	def update_drops(self, drop_id, drop_info, force=''):
		if drop_id in self.darker_than_blacklist:
			return
		if self.bagfull and drop_info.split(':')[0] != 'Gold':
			return
		x, y, z = self.splitandint(self.coords)
		dx, dy, dz = self.splitandint(drop_info.split(':')[2]) 
		if z != dz:
			return
		if force != 'force':
			black_ids = [x.split('@')[0] for x in self.blacklist]
			if drop_id in black_ids:
				return
		self.drop_ids[drop_id] = drop_info # drop_info contains drop name, quantity, and coords
	
	def update_drop_distances(self):
		if self.coords == '0':
			if self.next_action.split('@')[0] == 'step3':
				return
			self.prettyprint("Fatal Error: I don't know my own coordinates.")
			self.adb.restartrucoy()
			self.next_action = 'step3@{}'.format(time.time()+5)
			return
		
		x, y, z = self.splitandint(self.coords)
		
		for drop_id in self.drop_ids:
			drop_x, drop_y, drop_z = self.splitandint(self.drop_ids[drop_id].split(':')[2])
			if z != drop_z:
				pass
			drop_distance = abs(drop_y - y) + abs(drop_x - x)
			self.drop_distances[drop_id] = drop_distance
	
	def update_coords(self, coords):
		self.coords = coords
	
	def update_plzlist(self, action):
		self.plzlist.insert(0, action)
		self.plzlist.pop(10)
	
	def forget(self, forget_me, organic=False):
		monster_exists = self.monster_ids.get(forget_me, 'n/a')
		if monster_exists != 'n/a':
			try:
				del self.monster_distances[forget_me]
				del self.monster_ids[forget_me]
				self.update_monster_distances()
			except:
				pass
		
		drop_exists = self.drop_ids.get(forget_me, 'n/a')
		if drop_exists != 'n/a':
			try:
				del self.drop_distances[forget_me]
				del self.drop_ids[forget_me]
				self.update_drop_distances()
			except:
				pass
		
		if self.atktgt == forget_me:
			self.atktgt = ''
			if self.pauseplz == False:
				self.next_action = ''
		
		if self.droptgt == forget_me:
			self.droptgt = ''
			if self.pauseplz == False:
				self.next_action = ''
		
		if forget_me in self.forgiven:
			self.forgiven.remove(forget_me)
		
		if organic:
			if forget_me in self.darker_than_blacklist:
				self.darker_than_blacklist.remove(forget_me)
			black_ids = [x.split('@')[0] for x in self.blacklist]
			delete_me = []
			if forget_me in black_ids:
				for key in self.blacklist:
					if key.startswith(forget_me):
						delete_me.append(key)
			for key in delete_me:
				del self.blacklist[key]
	
	def monster_slayer(self):
		#Figure out which monster is closest to attack. :-)
		if len(self.monster_distances) == 0:
			return 0
		self.atktgt = min(self.monster_distances.keys(), key=(lambda k: self.monster_distances[k]))
		#self.prettyprint("{} with the id of {} has been selected as the target.".format(self.monster_ids[self.atktgt].split(':')[0], self.atktgt))
		
		x, y, z = self.splitandint(self.coords)
		monster_x, monster_y, monster_z = self.splitandint(self.monster_ids[self.atktgt].split(':')[1])
		
		xtotap = monster_x - x
		ytotap = monster_y - y
		
		if xtotap == 0 and ytotap == 0:
			self.update_blacklist(self.atktgt)
			return 0
		else:
			self.prettyprint("Attacking {} at relative {}, {}.".format(self.monster_ids[self.atktgt].split(':')[0], xtotap, ytotap))
			
			# use adb to tap on the monsters and use special if needed. if not melee, try to close 
			# the distance to the monster as well.
			if self.weapon == 'melee':
				if self.special and self.monster_distances[self.atktgt] == 1:
					self.adb.tapat(xtotap, ytotap)
					self.adb.tapspecial()
				else:
					self.adb.tapat(xtotap, ytotap)
			elif self.weapon == 'dist' and self.monster_distances[self.atktgt] < 5:
				self.adb.tapat(xtotap, ytotap)
				self.move_closer(xtotap, ytotap)
				if self.special:
					self.adb.tapspecial()	
			else:
				#self.weapon == 'mage'
				self.adb.tapat(xtotap, ytotap)
				self.move_closer(xtotap, ytotap)
				if self.special and self.monster_distances[self.atktgt] < 5:
					self.adb.tapspecial()
					self.adb.tapat(xtotap, ytotap)
			
		# Return time action was taken to take_action
		return time.time()
	
	def move_closer(self, xtotap=0, ytotap=0):
		if xtotap == 0 and ytotap == 0:
			x, y, z = self.splitandint(self.coords)
			monster_x, monster_y, monster_z = self.splitandint(self.monster_ids[self.atktgt].split(':')[1])
			
			xtotap = monster_x - x
			ytotap = monster_y - y
		
		if self.monster_distances[self.atktgt] > 3:
			if xtotap > 0:
				xtogetclose = xtotap-1
			elif xtotap == 0:
				xtogetclose = xtotap
			else:
				xtogetclose = xtotap+1
			if ytotap > 0:
				ytogetclose = ytotap-1
			elif xtotap == 0:
				ytogetclose = ytotap
			else:
				ytogetclose = ytotap+1
			if xtogetclose == 0 and ytogetclose == 0:
				xtogetclose = 1
			
			self.adb.tapat(xtogetclose, ytogetclose)
		else:
			self.adb.tapat(xtotap, ytotap)
	
	def gimme_drops(self):
		#Figure out which drop is closest to pickup. :-)
		self.droptgt = min(self.drop_distances.keys(), key=(lambda k: self.drop_distances[k]))
		
		if self.drop_distances[self.droptgt] > 5:
			self.forget(self.droptgt)
			return 0
		
		#self.prettyprint("{} with the id of {} has been selected to pickup.".format(self.drop_ids[self.droptgt].split(':')[0], self.droptgt))
		
		x, y, z = self.splitandint(self.coords)
		drop_x, drop_y, drop_z = self.splitandint(self.drop_ids[self.droptgt].split(':')[2])
		
		xtotap = drop_x - x
		ytotap = drop_y - y 
		
		if xtotap == 0 and ytotap == 0:
			xtotap += 1
		
		if drop_x == 0 and drop_y == 0 and drop_z == 0:
			self.forget(self.droptgt)
			return 0
		
		if drop_z != z:
			self.forget(self.droptgt)
			return 0
		
		# use adb to tap on where the drop is.
		if xtotap <= 1 and xtotap >= -1 and ytotap >= -1 and ytotap <= 1:
			self.adb.tapat(xtotap, ytotap)
			self.adb.tappickup()
			self.forget(self.droptgt)
			return 0
		else:
			self.prettyprint("Picking up {} at relative {}, {}.".format(self.drop_ids[self.droptgt].split(':')[0], xtotap, ytotap))
			self.adb.tapat(xtotap, ytotap)
			return time.time()
	
	def take_action(self):
		self.update_blacklist()
		current_hp_percent = 100*(int(self.hp)/int(self.maxhp))
		if current_hp_percent <= 30:
			self.adb.restartrucoy(1800)
			self.prettyprint("Pausing for 30 minutes because HP has dropped below 30%.")
		if self.usepots:
			if current_hp_percent <= int(self.hptime):
				if self.last_hppot <= time.time():
					self.adb.taphppot()
					self.last_hppot = time.time()+4
			current_mp_percent = 100*(int(self.mp)/int(self.maxmp))
			if current_mp_percent <= int(self.mptime):
				if self.last_mppot <= time.time():
					self.adb.tapmppot()
					self.last_mppot = time.time()+4
		if self.next_action == '':
			# implicit step null
			self.old_coords = self.coords
			if len(self.drop_ids) > 0 and self.mode == 'farm':
				# navigate to and pick up some drops.
				action_time = self.gimme_drops()
				if action_time != 0:
					self.update_last_actions(self.droptgt, action_time)
					# next action is step 2, which should be done in 3 seconds.
					self.next_action = 'step2@{}'.format(action_time+3)
				else:
					self.next_action = 'step3@{}'.format(action_time+2)
			else:
				# step 0, try to attack the monster.
				#self.prettyprint('step 0 done at {}'.format(time.time()))
				action_time = self.monster_slayer()
				if action_time != 0:
					self.update_last_actions(self.atktgt, action_time)
					# next action is the step 1, which should be done in 3 seconds.
					if self.monster_distances[self.atktgt] > 5:
						self.next_action = 'step1@{}'.format(action_time+6)
					else:
						self.next_action = 'step1@{}'.format(action_time+3)
				else:
					#self.prettyprint('no monsters, returning...')
					return
		elif self.next_action.split('@')[0] == 'step1' and float(self.next_action.split('@')[1]) <= time.time():
			# step 1
			# check if we moved, attacked, or nada
			#self.prettyprint('step 1 done at {}'.format(time.time()))
			#self.diagnostics()
			if self.special and not self.amiblocked() and self.mode == 'skill': 
				self.tempignore.append(self.atktgt)
				self.update_blacklist(self.atktgt, True)
				self.next_action = ''
				return
			else:
				for monster in self.tempignore:
					self.try_to_forgive(monster, 'yes')
				self.tempignore = []
			if self.old_coords == self.coords and self.last_attack+3 <= time.time():
				#nothing happened, so we failed to move or make a hit
				x = randint(-2, 2)
				y = randint(-2, 2)
				if x == 0 and y == 0:
					x = 1
				self.adb.tapat(x, y)
				self.next_action = ''
				self.update_blacklist(self.atktgt)
			elif self.plzlist[0].split(':')[0] == 'hit' and self.plzlist[0].split(':')[1] == self.atktgt:
				# we tapped the monster, lets back off and wait til death or attacks stop if melee
				# if not melee, check self.last_attack, ensure an attack is made, if not move and start over.
				if self.atktgt == '' or self.last_attack+3 <= time.time():
					self.next_action = ''
					if self.weapon != 'melee':
						x = randint(-2, 2)
						y = randint(-2, 2)
						if x == 0 and y == 0:
							x = 1
						self.adb.tapat(x, y)
						self.update_blacklist(self.atktgt)
			elif self.plzlist[0].split(':')[0] == 'move' and self.plzlist[1].split(':')[0] == 'hit':
				# assuming self.weapon != 'melee', hit & move successful, so wait til death or
				# til no more attacks are successful
				if self.weapon == 'melee':
					self.next_action = ''
				if self.plzlist[1].split(':')[1] == self.atktgt:
					if self.atktgt == '' or self.last_attack+3 <= time.time():
						self.next_action = ''
				else:
					self.next_action = ''
			else:
				self.next_action = ''
		elif self.next_action.split('@')[0] == 'step2' and float(self.next_action.split('@')[1]) <= time.time():
			#self.prettyprint('step 2 done at {}'.format(time.time()))
			action_time = self.gimme_drops()
			self.update_blacklist(self.droptgt)
			self.next_action = ''
		elif self.next_action.split('@')[0] == 'step3' and float(self.next_action.split('@')[1]) <= time.time():
			self.next_action = ''
			self.pauseplz = False
			if self.begone_count == 7331:
				self.begone_count = 0
				if self.switchplz:
					self.switchplz = False
					if self.weapon == 'melee':
						self.adb.switchmeleeweapon()
					elif self.weapon == 'dist':
						self.adb.switchdistweapon()
					else:
						self.adb.switchmageweapon()
		elif self.next_action.split('@')[0] == 'step4' and float(self.next_action.split('@')[1]) <= time.time():
			#print('s4, {}'.format(self.begone_count))
			if self.begone_count == 1337:
				if self.old_coords == self.coords:
					self.begone_count = 1
					self.next_action = 'step4@{}'.format(time.time()+1)
				else:
					oldx, oldy, oldz = self.splitandint(self.old_coords)
					newx, newy, newz = self.splitandint(self.coords)
					distance_moved = abs(newy - oldy) + abs(newx - oldx)
					if distance_moved > 15:
						self.begone_count = 7331
						self.next_action = 'step3@{}'.format(time.time()+10)
					else:
						self.begone_count = 1
						self.next_action = 'step4@{}'.format(time.time()+1)
			elif self.begone_count == 2:
				self.begone_count = 1337
				self.adb.tapmap()
				x = randint(0, 1)
				y = randint(0, 1)
				if x == 0:
					x = randint(-3, -1)
				else:
					x = randint(1, 3)
				if y == 0:
					y = randint(-3, -1)
				else:
					y = randint(1, 3)
				self.adb.tapat(x, y)
				self.adb.tapclose()
				self.next_action = 'step4@{}'.format(time.time()+2)
				self.old_coords = self.coords
			else:
				if self.weapon == 'mage':
					self.adb.tapspecial()
					self.adb.tapat('1', '0')
					self.adb.tapat('-1', '0')
				else:
					self.adb.tapspecial()
				self.next_action = 'step4@{}'.format(time.time()+1)
				self.begone_count += 1
		else:
			pass
		if self.last_attack+60 <= time.time():
			self.prettyprint('No attacks made for over 60 seconds. Restarting.')
			self.last_attack = 9000000000
			self.monster_ids = {}
			self.monster_distances = {}
			self.drop_ids = {}
			self.drop_distances = {}
			self.coords = '0'
			self.old_coords = '0'
			self.plzlist = [':']*10
			self.atktgt = ''
			self.droptgt = ''
			self.next_action = ''
			self.last_actions = ['']*10
			self.blacklist = {}
			self.darker_than_blacklist = []
			self.last_attack = 9000000000
			self.last_hppot = 0
			self.last_mppot = 0
			self.swordname = ''
			self.bowname = ''
			self.wandname = ''
			self.forgiven = []
			self.super_hp_pots = '0'
			self.great_hp_pots = '0'
			self.normal_hp_pots = '0'
			self.begone_count = 0
			self.adb.restartrucoy()
		if self.start_time+15 <= time.time() and self.need_screenshot:
			self.need_screenshot = False
			self.adb.tapsettings()
			self.adb.tapsettings_stats()
			self.adb.pullscreenshot('start{}.png'.format(self.ipaddr))
			self.adb.tapclose()
		if all([x.split('@')[0]=='move' for x in self.last_actions]) and self.next_action.split('@')[0] != 'step3':
			self.prettyprint('Nothing but air... Suspending for 10 seconds.')
			self.next_action = 'step3@{}'.format(time.time()+10)
	
	def update_blacklist(self, nogood='forgive', temp=False):
		if nogood == 'forgive':
			# Cycle through self.blacklist and forgive any monsters who have been
			# blacklisted for longer than 9 seconds.
			new_blacklist = {}
			for key in self.blacklist.keys():
				id = key.split('@')[0]
				the_time = key.split('@')[1]
				if float(the_time) <= time.time():
					if int(id) < 65000:
						self.update_monsters(id, self.blacklist[key], 'force')
						self.update_monster_distances()
					else:
						self.update_drops(id, self.blacklist[key], 'force')
						self.update_drop_distances()
				if float(the_time) > time.time(): 
					value = self.blacklist[key] 
					new_blacklist.update({ key : value })
			self.blacklist = new_blacklist
		else:
			if nogood == '':
				return
			black_ids = [x.split('@')[0] for x in self.blacklist]
			if nogood in black_ids:
				return
			if nogood in self.darker_than_blacklist:
				nogood_and_time = '{}@{}'.format(nogood, time.time()+50)
			else:
				nogood_and_time = '{}@{}'.format(nogood, time.time()+9)
			if nogood in self.monster_ids:
				nogood_info = self.monster_ids[nogood]
			else:
				nogood_info = self.drop_ids[nogood]
			self.blacklist.update({ nogood_and_time : nogood_info})
			self.forget(nogood)
			if not temp:
				self.darker_than_blacklist.append(nogood)
	
	def update_last_actions(self, action, action_time):
		self.last_actions.insert(0, '{}@{}'.format(action, action_time))
		self.last_actions.pop(10)
	
	def update_last_attack(self, last):
		self.last_attack = last
		if self.special and self.atktgt != '':
			self.last_attack += 1
			if self.weapon == 'melee' and self.monster_distances[self.atktgt] <= 2:
				self.adb.tapspecial()
			elif self.weapon == 'dist' and self.monster_distances[self.atktgt] < 5:
				self.adb.tapspecial()
			elif self.weapon != 'melee' and self.monster_distances[self.atktgt] < 5:
				self.adb.tapspecial()
				self.move_closer()
			else:
				pass
	
	def check_weapon(self, wpn):
		if self.weapon == 'melee' and wpn != '0':
			time.sleep(0.5)
			self.adb.tapmelee()
			time.sleep(0.5)
		elif self.weapon == 'dist' and wpn != '1':
			time.sleep(0.5)
			self.adb.tapdist()
			time.sleep(0.5)
		elif self.weapon == 'mage' and wpn != '2':
			time.sleep(0.5)
			self.adb.tapmage()
			time.sleep(0.5)
		else:
			pass
	
	def update_equiped(self, x, weapon_name):
		if x == 28:
			return
		elif x == 26:
			self.swordname = weapon_name
		elif x == 30:
			self.bowname = weapon_name
		elif x == 32:
			self.wandname = weapon_name
		else:
			pass
	
	def try_to_forgive(self, monster_id, force='no'):
		if force == 'no':
			if self.pauseplz:
				return
			if monster_id in self.forgiven:
				return
		black_ids = [x.split('@')[0] for x in self.blacklist]
		temp1 = ''
		temp2 = ''
		'''
		if monster_id in self.monster_distances:
			# self.plzlist[0].split(':')[1] != self.atktgt and self.plzlist[1].split(':')[1] != self.atktgt and self.atktgt != monster_id
			if self.plzlist[0].split(':')[1] != monster_id and self.plzlist[1].split(':')[1] != monster_id and self.last_attack+2 <= int(time.time()) and self.last_forgive+2 <= int(time.time()):
				self.next_action = ''
		'''
		
		if self.last_attack+1.3 <= time.time() and self.last_forgive+1.3 <= time.time() and self.next_action != '':
			self.next_action = ''
			self.last_forgive = time.time()
		
		if monster_id in black_ids:
			for key in self.blacklist:
				if key.startswith(monster_id):
					if float(key.split('@')[1]) > time.time()+10:
						temp1 = key
						temp2 = self.blacklist[key]
			if temp1 != '':
				del self.blacklist[temp1]
				if monster_id in self.darker_than_blacklist:
					self.darker_than_blacklist.remove(monster_id)
				new_key = '{}@{}'.format(monster_id, time.time()-5)
				self.blacklist.update({ new_key : temp2})
				self.forgiven.append(monster_id)
				self.update_blacklist()
		
		
	
	def update_pot_count(self, id, qty):
		if not self.usepots:
			return
		if qty == '0':
			if id == 'hp':
				self.super_hp_pots = '0'
				self.great_hp_pots = '0'
				self.normal_hp_pots = '0'
				self.hptime = '0'
				if self.mptime == '0':
					self.usepots = False
			else:
				# id == 'mp'
				self.super_hp_pots = '0'
				self.great_hp_pots = '0'
				self.normal_hp_pots = '0'
				self.hptime = '0'
				if self.hptime == '0':
					self.usepots = False
		if id.find('Super') >= 0:
			if id.find('Mana') >= 0:
				self.super_mp_pots = qty
			else:
				#assumes health potion
				self.super_hp_pots = qty
		elif id.find('Great') >= 0:
			if id.find('Mana') >= 0:
				self.great_mp_pots = qty
			else:
				#assumes health potion
				self.great_hp_pots = qty
		else:
			#Assume normal health or mana potion.
			if id.find('Mana') >= 0:
				self.normal_mp_pots = qty
			else:
				#assumes health potion
				self.normal_hp_pots = qty
	
	def gimme_the_training(self, slot, id):
		if self.start_time+10 <= time.time() and self.start_time+60 >= time.time():
			if self.mode == 'skill':
				if self.weapon == 'melee':
					if self.swordname.find('Training') == -1:
						if id.find('Training Dagger') >= 0:
							self.adb.tapsettings()
							self.adb.tapsettings_inventory()
							self.adb.tapsettings_inventory_select(int(slot))
							self.adb.tapsettings_inventory_green()
							self.adb.tapclose()
				elif self.weapon == 'dist':
					if self.bowname.find('Training') == -1:
						if id.find('Training Bow') >= 0:
							self.adb.tapsettings()
							self.adb.tapsettings_inventory()
							self.adb.tapsettings_inventory_select(int(slot))
							self.adb.tapsettings_inventory_green()
							self.adb.tapclose()
				else:
					#assumes self.weapon == 'mage'
					if self.wandname.find('Training') == -1:
						if id.find('Training Wand') >= 0:
							self.adb.tapsettings()
							self.adb.tapsettings_inventory()
							self.adb.tapsettings_inventory_select(int(slot))
							self.adb.tapsettings_inventory_green()
							self.adb.tapclose()
	
	def prettyprint(self, message):
		forwardthis = "Bot    >>> {}".format(message)
		self.bpq.put(forwardthis)
		#print(forwardthis)
	
	def reconnect(self):
		self.prettyprint('Disconnected, reconnecting in 3 seconds...')
		time.sleep(3)
		self.adb.tapat(1, 1)
	
	def pause(self):
		self.prettyprint("Monsters have become exhausted. Trying to move... ")
		blocked = self.amiblocked()
		time.sleep(0.5)
		if blocked:
			self.switchplz = True
			if self.weapon == 'melee':
				self.adb.switchmeleeweapon()
				self.adb.tapspecial()
			elif self.weapon == 'dist':
				self.adb.switchdistweapon()
				self.adb.tapspecial()
			else:
				self.adb.switchmageweapon()
				self.adb.tapspecial()
				self.adb.tapat('1', '0')
				self.adb.tapat('-1', '0')
		self.next_action = 'step4@{}'.format(time.time()+1)
		self.pauseplz = True
	
	def amiblocked(self):
		count = 0
		for monster in self.monster_distances:
			if self.monster_distances[monster] <= 2:
				count += 1
		return count > 2
	
	def splitandint(self, coords):
		try:
			x, y, z = coords.split(',')
			x = int(x)
			y = int(y)
			z = int(z)
			return x,y,z
		except Exception as e:
			return 0,0,0
	
	def diagnostics(self):
		self.prettyprint(f'mode: {self.mode}\tweapon: {self.weapon}\tspecial: {self.special}')
		self.prettyprint(f'usepots: {self.usepots}\thptime: {self.hptime}\tmptime: {self.mptime}')
		self.prettyprint(f'coords: {self.coords}\tatktgt: {self.atktgt}\tdroptgt: {self.droptgt}')
		self.prettyprint(f'next action: {self.next_action}\tlast atk: {self.last_attack}\told coords: {self.old_plzlist}')
		self.prettyprint(f'monster ids: {self.monster_ids}')
		self.prettyprint(f'monster distances: {self.monster_distances}')
		self.prettyprint(f'drop ids: {self.drop_ids}')
		self.prettyprint(f'drop distances: {self.drop_distances}')
		self.prettyprint(f'plzlist: {self.plzlist}')
		self.prettyprint(f'forgiven: {self.forgiven}')
		self.prettyprint(f'last_actions: {self.last_actions}')
		self.prettyprint(f'blacklist: {self.blacklist}')
		self.prettyprint(f'darker than black: {self.darker_than_blacklist}')




def quecatcher(botq, mode, botprintq, botatk, botspecial, botusepots, botpottime, serial, ratio, ipaddr):
	#declare RucoyBot() object with necessary params
	bot = RucoyBot(mode, botprintq, botatk, botspecial, botusepots, botpottime, serial, ratio, ipaddr)
	
	while True:
		datas = botq.get()
		data = datas.split('|')
		if data[0] == "hp":
			bot.update_hp(data[1], data[2])
		elif data[0] == "mp":
			bot.update_mp(data[1], data[2])
		elif data[0] == "coords":
			bot.update_coords(data[1])
			bot.update_monster_distances()
			bot.update_drop_distances()
		elif data[0] == "atkplz":
			bot.update_plzlist('hit:{}'.format(data[1]))
		elif data[0] == "moveplz":
			bot.update_plzlist('move:{}'.format(data[1]))
		elif data[0] == "monster":
			bot.update_monsters(data[1], data[2])
			bot.update_monster_distances()
		elif data[0] == "forget":
			bot.forget(data[1], True)
		elif data[0] == "drop":
			bot.update_drops(data[1], data[2])
			bot.update_drop_distances()
		elif data[0] == "takeatk":
			bot.update_last_attack(time.time())
		elif data[0] == "wpn":
			bot.check_weapon(data[1])
		elif data[0] == "equip":
			bot.update_equiped(data[1], data[2])
		elif data[0] == "forgive":
			bot.try_to_forgive(data[1])
		elif data[0] == "ended":
			if bot.start_time+60 >= time.time():
				bot = RucoyBot(mode, botprintq, botatk, botspecial, botusepots, botpottime, serial, ratio, ipaddr)
				bot.reconnect()
			else:
				bot = RucoyBot(mode, botprintq, botatk, botspecial, botusepots, botpottime, serial, ratio, ipaddr)
				bot.start_time = 9000000000
				bot.reconnect()
		elif data[0] == "exhaust":
			bot.pause()
		elif data[0] == "pot":
			bot.update_pot_count(data[1], data[2])
		elif data[0] == "bag":
			bot.gimme_the_training(data[1], data[2])
		elif data[0] == "taken":
			if data[1] in bot.monster_ids:
				bot.update_blacklist(data[1], True)
			if data[1] == bot.atktgt:
				bot.next_action = ''
		elif data[0] == "bagfull":
			bot.bagfull = True
		elif data[0] == "bagnotfull":
			bot.bagfull = False
		elif data[0] == "bye" and data[1] == "bye":
			bot.adb.quit_loop()
			break
		elif data[0] == "dead":
			bot.prettyprint("Character has died. Bot stopping.")
			break
		else:
			bot.prettyprint("Error, unknown data: {}".format(data))
		
		bot.take_action()


















