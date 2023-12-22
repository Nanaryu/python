from webhook import *
from datetime import datetime
from mobs_items import *
filters = [
	"messages", 
	"disconnect",
	"attack",
	"hpmpupd",
	"statupd",
	"move",
	"bagupd",
	"forget",
	"shownums",
	"shop",
	"select",
	"dimas",
	"redmsg",
	"whitemsg",
	"youare",
	"friendlist",
	"bot",
	"client"
]

#sent every few seconds to keep the connection alive
def alive():
	return "I'm alive"

def dead():
	deadmsg = "!#die|0"
	print(deadmsg)
	
	webhook = f"You have died at {datetime.now()}"
	wb_send(webhook)
	
	return f"You have died at {datetime.now()}"

#picks up any objects located right next to player (not diagonally) 
def pickup():
	return "Pickup"

#converts the last 4 bytes into an ID that identifies the monster on the map
def attack(entityID):
	try:
		return f"Attack entity ID {entityID}"
	except Exception as e: 
		return f"An unknown error occurred - attack - {e}"
     
#Sent when weapons are changed
def weapon(restofwpn):
	weapon = {
		'00': "Switch to Warrior",
		'01': "Switch to Archer",
		'02': "Switch to Mage"
	}
	return weapon[restofwpn]

#Identifies the coordinates of the requested position. Server checks validity of all coordinates.
def moveto(location):
	try:
		x = int(location[:4],16)
		y = int(location[4:],16)
		return f"Move to {x}, {y}"
	except Exception as e:
		return "An unknown error occurred - moveto - {}".format(e)
	
#Sent after death and the respawn button is pressed. Location is automatically set to NE building of hometown.
def revive():
	return "Revive!"

def useitem(whichitem):
	return f"Use item {whichitem}"
      
# 070d000000000080 -> Air Slash / Haste
# 070d000000000000 -> Melee Spin / Arrows
# No, you can't bypass cooldowns
def special(restofspl):
	if restofspl == '000000000000':
		return "Special Attack (Warrior or Archer)"
	elif restofspl == '000000000080':
		return 'Air Slash or Haste'
	else:
		try:
			x = int(restofspl[:4],16)
			y = int(restofspl[4:8],16)
			if restofspl[8:] == '0000':
				return f"Fireball at {x}, {y}"
			elif restofspl[8:] == '0080':
				return f"Magic Wall at {x}, {y}"
		except:
			return "MageSpecial ? <PositionError>"
		

#Equip something from player inventory to the relevant slot, ie. Equiping a helmet moves the item
#in inventory to the helmet slot, pops the item from the inventory, and moves the previous equiped
#item to the last slot in inventory.
def equip(restofeqp):
	try:
		return f"Equip item stored in slot {restofeqp}"
	except Exception as e:
		return f"An unknown error occurred - equip - {e}"
	
#Unequip the item in the slot defined belowed in the slots dictionary.
def unequip(restofuqp):
	slots = {
		2: "Helmet Slot",
		3: "Chest Slot",
		4: "Belt Slot",
		5: "Pants Slot",
		6: "Boots Slot",
		7: "Left Glove Slot",
		8: "Right Glove Slot",
		9: "Necklace Slot",
		10: "Ring Slot"
	}
	try:
		return f"Unequip item stored in {slots[int(restofuqp,16)]}"
	except Exception as e:
		return f"An unknown error occurred - unequip - {e}"
	
# Not done as it doesn't have much purpose yet
def merchant(restofmer):
	specialty = {
		b'\x00\x00\x122': "Speak with Gear Merchant",
		b'\x00\x00\x121': "Speak with Supplies Merchant",
		b'\x00\x00\x123': "Speak with Vault Merchant",
		'00000033': "Speak with Lvl 150 Supporter Merchant",
		'0000002b': "Speak with Lvl 150 Supplies Merchant",
		'0000003b': "Speak with Lvl 150 Gear Merchant",
		'00000043': "Speak with Lvl 150 Vault Merchant",
		'0000004b': "Speak with Blacksmith",
		'00000053': "Speak with Specialist",
	}
	try:
		if restofmer in specialty:
			return specialty[restofmer]
		else:
			return f"Follow Player ID {int(restofmer,16)}"
	except Exception as e:
		return f"An unknown error occurred - merchant - {e}"
	
def sendmsg(restofmsg):
	try:
		recipient = {
			'00': "Local",
			'01': "Server",
			'02': "Team",
			'04': "Guild"
		}
		if restofmsg[:2] == '03':
			name_length = int(restofmsg[2:4], 16)
			target = restofmsg[4:name_length+4]
			msg_length = int(restofmsg[name_length+4:name_length+6], 16)
			message = restofmsg[name_length+6:]
		else:
			target = recipient[restofmsg[:2]]
			msg_length = int(restofmsg[2:4], 16)
			message = restofmsg[4:]
		
		return f"Send message '{message}' | {msg_length} characters long to {target}"
	except Exception as e:
		return f"An unknown error occurred - sendmsg - {e}"
	

def servmsg(msg):
	#\x02
	return f"server message"

def gotcha(salute):
	try:
		# \x08 
		if salute == b'':
			return "Acknowledged."
		else:
			return f"Acknowledged - {salute}"
	except Exception as e:
		return f"An unknown error occurred - gotcha - {e}"
	
def takeatk(whotowho):
	"""
	Client -> Attack entity ID 00000000
	Server -> 0f1e0000000000000000600d00000000
	Client -> Attack entity ID 00000d89
	Server -> 0f1e00000d8900000000600d00000d89
	Client -> Attack entity ID 00000000
	Server -> 0f1e0000000000000000600d00000000
	Client -> Attack entity ID 00000d89
	Server -> 1823011a14033c056c06a8001a040000ad80d5000000058880
	Server -> 0f1e00000d8900000000600d00000d89
	Client -> Attack entity ID 00000000
	Server -> 0f1e0000000000000000600d00000000
	Server -> 083e00000d89022301
	Client -> Attack entity ID 00000d89
	Server -> 0f1e00000d8900000000600d00000d89
	Client -> Attack entity ID 00000000
	Server -> 0f1e0000000000000000600d00000000
	"""
	try:
		# \x09 
		lastindex = 0
		returnable = ""
		
		while lastindex < len(whotowho):
			if whotowho[lastindex:lastindex + 1] == '09' and lastindex != 0:
				monster_id = int(whotowho[lastindex + 1:lastindex + 5], 16)
				victim_id = int(whotowho[lastindex + 5:lastindex + 9], 16)
				lastindex += 10
				returnable += f"Monster {monster_id} attacks player {victim_id}.|"
			elif lastindex == 0:
				monster_id = int(whotowho[lastindex:lastindex + 4], 16)
				victim_id = int(whotowho[lastindex + 4:lastindex + 8], 16)
				lastindex += 9
				
				if monster_id > 65536:
					returnable += f"Player attacks monster {monster_id}.|"
				else:
					returnable += f"Monster {monster_id} attacks player {victim_id}."
			else:
				return f" ATTK STRING >>> {returnable}"
		return returnable
	except Exception as e:
		return f"An unknown error occurred - takeatk - {e}"

def showobj(objects):
	return f"SHOW OBJECTS"