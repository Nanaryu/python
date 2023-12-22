import pydivert
import sys
import struct
import binascii
from textwrap import wrap
import requests
from bs4 import BeautifulSoup as beso
import re
import rucoyadb
from time import sleep
from win10toast import ToastNotifier
adb = rucoyadb.AdbLib()
toaster = ToastNotifier()

bp = 'monitor'

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


#create functions to use pydivert, display translated packets, and forward along
def listener(mode, qu, ipaddr, modme, pqueue, botq, botpower, botprintq, resolve_levels, pm_notifications, pm_notify_email, upload_data, region, servnum, all_filters, serial, ratio, atkok):
	sys.stdout = qu
	global pq
	global bq
	global bp
	global bpq
	global filters
	global potsgone
	global attack_me
	global bagfull
	pq = pqueue
	bq = botq
	bp = botpower
	bpq = botprintq
	filters = all_filters
	potsgone = True
	attack_me = atkok
	bagfull = False
	global_settings['resolve_levels'] = resolve_levels
	global_settings['pm_notifications'] = pm_notifications
	global_settings['pm_notify_email'] = pm_notify_email
	global_settings['upload_data'] = upload_data
	
	adb.setserial(serial)
	adb.setratio(ratio)
	
	if ipaddr != '0.0.0.0':
		sleep(8)
		adb.tapsettings()
		adb.tapsettings_servers()
		adb.tapsettings_servers_select(region)
		wdstr = "ip.DstAddr == {} or ip.SrcAddr == {} and tcp.PayloadLength > 0".format(ipaddr, ipaddr)
	else:
		wdstr = "tcp.DstPort == 4000 or tcp.SrcPort == 4000 and tcp.PayloadLength > 0"
	
	
	modmeplz = b'\x00\x02\x30' + bytes([modme])
	#modmeplz = b'\x00\x11\x07\x01\x6a'
	#x5cb2424
	
	longpacket = b''
	temp = 1
	
	with pydivert.WinDivert(wdstr) as w:
		if temp == 1:
			adb.tapsettings_servers_select(servnum)
			adb.tapclose()
			temp = 0
		for packet in w:
			original = packet.tcp.payload
			modded = modify(packet.tcp.payload, modmeplz)
			if original != modded:
				packet.tcp.payload = packet.tcp.payload.replace(original, modded)
				print("Changed >> ", translator(modded, "client"))
			
			w.send(packet)
			
			if packet.tcp.dst_port != 4000:
				if packet.tcp.payload == b'':
					continue
				if len(packet.tcp.payload) >= 1300:
					longpacket += packet.tcp.payload
					continue
				if len(longpacket) > 0:
					packet.tcp.payload = longpacket + packet.tcp.payload
					longpacket = b''
				translated = translator(packet.tcp.payload, "server")
				rawone = int(binascii.hexlify(packet.tcp.payload[:1]), 16)
				if translated.find("b'") >= 0 or translated.find('\\x') >= 0 or translated.find('error') >= 0 or translated.find('what the hell') >= 0:
					if rawone <= 53:
						email = """The following produced a bug report. Please review and provide a patch. Thank you!\n\n{}\nRaw    >>>  {}""".format(prettyreturn(translated), spill(packet.tcp.payload))
						pq.put('send|{}|{}|{}'.format('your.rucoybot@gmail.com', 'Developer', email))
				if mode == 1:
					if packet.tcp.payload != translated and translated[:25] != "An unknown error occurred":
						if translated != '' and translated != ' ' and not translated.startswith("b'") and translated.find('\\x') == -1:
							print(prettyreturn(translated))
						printbot()
				elif mode == 2:
					if packet.tcp.payload != translated and translated[:25] != "An unknown error occurred":
						if translated != '' and translated != ' ' and not translated.startswith("b'") and translated.find('\\x') == -1:
							print(prettyreturn(translated))
							print("Raw    >>> ", spill(packet.tcp.payload))
						printbot()
				elif mode == 3:
					if translated != '' and translated != ' ':
						print(prettyreturn(translated))
					printbot()
				else:
					if translated != '' and translated != ' ':
						print(prettyreturn(translated))
						print("Raw    >>> ", spill(packet.tcp.payload))
					printbot()
			else:
				if packet.tcp.payload == b'':
					continue
				translated = translator(packet.tcp.payload, "client")
				if mode == 1:
					if packet.tcp.payload != translated and translated[:25] != "An unknown error occurred" and translated.find('\\x') == -1:
						print("Client >>> ", translated)
				elif mode == 2:
					if packet.tcp.payload != translated and translated[:25] != "An unknown error occurred" and translated.find('\\x') == -1:
						print("Client >>> ", translated)
						print("Raw    >>> ", spill(packet.tcp.payload))
				elif mode == 3:
					print("Client >>> ", translated)
				else:
					print("Client >>> ", translated)
					print("Raw    >>> ", spill(packet.tcp.payload))


def printbot():
	try:
		if 'bot' not in filters:
			return
		while True:
			if bpq.empty():
				return
			else:
				msg = bpq.get()
				print(msg)
	except:
		return
	
	
#---------------------------RucoyTerp------------------------------#


player_names = {
	1000: 'Bobby Sue Lvl. Max'
}

monster_names = {
	b'\x01': "Rat Lv.1",
	b'\x02': "Rat Lv.3",
	b'\x03': "Crow Lv.6",
	b'\x04': "Goblin Lv.15",
	b'\x05': "Scorpion Lv.12",
	b'\x06': "Worm Lv.14",
	b'\x07': "Cobra Lv.13",
	b'\x08': "Mummy Lv.25",
	b'\x09': "Pharaoh Lv.35",
	b'\x0a': "Assassin Lv.45",
	b'\x0b': "Assassin Lv.50",
	b'\x0c': "Zombie Lv.65",
	b'\x0d': "Zombie Lv.65",
	b'\x0e': "Skeleton Lv.75",
	b'\x0f': "Wolf Lv.9",
	b'\x10': "Skeleton Warrior Lv.90",
	b'\x11': "Vampire Lv.100",
	b'\x12': "Vampire Lv.110",
	b'\x13': "Drow Assassin Lv.120",
	b'\x14': "Drow Ranger Lv.125",
	b'\x15': "Drow Mage Lv.130",
	b'\x16': "Drow Fighter Lv.135",
	b'\x17': "Drow Sorceress Lv.140",
	b'\x18': "Skeleton Archer Lv.80",
	b'\x19': "Lizard Warrior Lv.150",
	b'\x1a': "Lizard Archer Lv.160",
	b'\x1b': "Lizard Shaman Lv.170",
	b'\x1c': "Lizard Captain Lv.180",
	b'\x1d': "Lizard High Shaman Lv.190",
	b'\x1e': "Slime Lord",
	b'\x1f': "Haunted Willow",
	b'\x20': "Haunted Sapling",
	b'\x21': "General Krinok",
	b'\x22': "Vampire King",
	b'\x23': "Kamon the Cursed",
	b'\x24': "Dragon Lv.250",
	b'\x25': "Dragon Warden Lv.280",
	b'\x26': "Dragon Hatchling Lv.240",
	b'\x27': "Evil Santa",
	b'\x28': "Healer Elf",
	b'\x29': "Goblin Lord",
	b'\x2a': "Slime",
	b'\x2b': "Yeti Lv.350",
	b'\x2c': "Ice Dragon Lv.320",
	b'\x2d': "Ice Elemental Lv.300",
	b'\x2e': "Assassin Ninja Lv.55",
	b'\x2f': "Wicked Pumpkin",
	b'\x30': "La Calaca",
	b'\x31': "Evil Snowman",
	b'\x32': "Orthrus",
	b'\x33': "Cerberus",
	b'\x34': "Djinn Lv.150",
	b'\x35': "Dead Eyes Lv.170",
	b'\x36': "Gargoyle Lv.190",
	b'\x37': "Lizard Major",
	b'\x38': "Vampire Prince",
	b'\x39': "Drow Queen",
	b'\x3a': "Drow Princess",
	b'\x3b': "Goliath",
	b'\x3c': "Gargoyle",
	b'\x3d': "Minotaur Lv.225",
	b'\x3e': "Minotaur Lv.250",
	b'\x3f': "Minotaur Lv.275",
	b'\x40': "Zarron Bravehorn",
	b'\x41': "Minotaur"
}

item_names = {
	1: "Health Potion",
	2: "Mana Potion",
	3: "Arrows",
	4: "Gold",
	5: "Leather Helmet",
	6: "Studded Helmet",
	7: "Iron Helmet",
	8: "Soldier Helmet",
	9: "Steel Helmet",
	10: "Leather Armor",
	11: "Studded Armor",
	12: "Iron Armor",
	13: "Soldier Armor",
	14: "Steel Armor",
	15: "Leather Belt",
	16: "Studded Belt",
	17: "Iron Belt",
	18: "Soldier Belt",
	19: "Steel Belt",
	20: "Leather Legs",
	21: "Studded Legs",
	22: "Iron Legs",
	23: "Soldier Legs",
	24: "Steel Legs",
	25: "Leather Boots",
	26: "Studded Boots",
	27: "Iron Boots",
	28: "Soldier Boots",
	29: "Steel Boots",
	30: "Leather Glove Left",
	31: "Studded Glove Left",
	32: "Iron Glove Left",
	33: "Soldier Glove Left",
	34: "Steel Glove Left",
	35: "Leather Glove Right",
	36: "Studded Glove Right",
	37: "Iron Glove Right",
	38: "Soldier Glove Right",
	39: "Steel Glove Right",
	40: "Dagger",
	41: "Short Sword",
	42: "Sword",
	43: "Broadsword",
	44: "Wooden Shield",
	45: "Studded Shield",
	46: "Iron Shield",
	47: "Soldier Shield",
	48: "Bow",
	49: "Studded Bow",
	50: "Iron Bow",
	51: "Drow Bow",
	52: "Wooden Wand",
	53: "Novice Wand",
	54: "Priest Wand",
	55: "Royal Priest Wand",
	56: "Bag",
	57: "Silver Bag",
	58: "Blue Bag",
	59: "Backpack",
	60: "Silver Backpack",
	61: "Blue Backpack",
	62: "Dagger Atk.17",
	63: "Dagger Atk.19",
	64: "Short Sword Atk.22",
	65: "Short Sword Atk.24",
	66: "Sword Atk.27",
	67: "Sword Atk.29",
	68: "Broadsword Atk.32",
	69: "Broadsword Atk.34",
	70: "Bow Atk.17",
	71: "Bow Atk.19",
	72: "Studded Bow Atk.22",
	73: "Studded Bow Atk.24",
	74: "Iron Bow Atk.27",
	75: "Iron Bow Atk.29",
	76: "Drow Bow Atk.32",
	77: "Drow Bow Atk.34",
	78: "Wooden Wand Atk.17",
	79: "Wooden Wand Atk.19",
	80: "Novice Wand Atk.22",
	81: "Novice Wand Atk.24",
	82: "Priest Wand Atk.27",
	83: "Priest Wand Atk.29",
	84: "Royal Priest Wand (Green)",
	85: "Royal Priest Wand (Blue)",
	86: "Lizard Helmet",
	87: "Lizard Armor",
	88: "Lizard Belt",
	89: "Lizard Legs",
	90: "Lizard Boots",
	91: "Lizard Glove Left",
	92: "Lizard Glove Right",
	93: "Green Backpack",
	94: "Lizard Slayer",
	95: "Lizard Slayer Atk.37",
	96: "Lizard Slayer Atk.39",
	97: "Battle Shield",
	98: "Lizard Bow",
	99: "Lizard Bow Atk.37",
	100: "Lizard Bow Atk.39",
	101: "Shaman Wand",
	102: "Shaman Wand Atk.37",
	103: "Shaman Wand Atk.39",
	104: "Greater Health Potion",
	105: "Super Health Potion",
	106: "Training Dagger",
	107: "Training Bow",
	108: "Training Wand",
	109: "Town Scroll",
	110: "Greater Mana Potion",
	111: "Super Mana Potion",
	112: "Diamonds",
	113: "Swift Boots",
	114: "Magic Ring",
	115: "Melee Ring",
	116: "Distance Ring",
	117: "Spiked Ring",
	118: "Life Ring",
	119: "Soul Ring",
	120: "Defense Ring",
	121: "Broadsword Atk.34",
	122: "Lizard Slayer Atk.39",
	123: "Soldier Shield Ar.35",
	124: "Battle Shield Ar.42",
	125: "Drow Bow (Purple)",
	126: "Lizard Bow Atk.39",
	127: "Royal Priest Wand (Purple)",
	128: "Shaman Wand Atk.39",
	129: "Ring",
	130: "Reinforced Ring",
	131: "Life Pendant",
	132: "Soul Pendant",
	133: "Halloween Potion",
	134: "Superior Magic Ring",
	135: "Superior Melee Ring",
	136: "Superior Distance Ring",
	137: "Superior Defense Ring",
	139: "Dragon Slayer",
	140: "Dragon Slayer Atk.42",
	141: "Dragon Slayer Atk.44",
	142: "Dragon Bow",
	143: "Dragon Bow Atk.42",
	144: "Dragon Bow Atk.44",
	145: "Dragon Wand",
	146: "Dragon Wand Atk.42",
	147: "Dragon Wand Atk.44",
	148: "Dragon Shield",
	149: "Dragon Shield Ar.49",
	150: "Dragon Shield Ar.50",
	151: "Dragon Helmet",
	152: "Dragon Armor",
	153: "Dragon Belt",
	154: "Dragon Legs",
	155: "Dragon Boots",
	156: "Dragon Glove Left",
	157: "Dragon Glove Right",
	158: "Dragon Backpack",
	159: "Christmas Candy",
	160: "Dragon Light Armor",
	161: "Lizard Light Armor",
	162: "Steel Light Armor",
	163: "Soldier Light Armor",
	164: "Iron Light Armor",
	165: "Studded Light Armor",
	166: "Leather Light Armor",
	167: "Dragon Robe",
	168: "Lizard Robe",
	169: "Drow Robe",
	170: "Soldier Robe",
	171: "Mage Robe",
	172: "Brown Robe",
	173: "Robe",
	174: "Hood",
	175: "Brown Hood",
	176: "Archer Hood",
	177: "Soldier Hood",
	178: "Drow Hood",
	179: "Lizard Hood",
	180: "Dragon Hood",
	181: "Hat",
	182: "Brown Hat",
	183: "Mage Hat",
	184: "Soldier Hat",
	185: "Drow Hat",
	186: "Lizard Hat",
	187: "Dragon Hat",
	188: "Frozen Helmet",
	189: "Frozen Hood",
	190: "Frozen Hat",
	191: "Frozen Armor",
	192: "Frozen Light Armor",
	193: "Frozen Robe",
	194: "Frozen Legs",
	195: "Frozen Belt",
	196: "Frozen Boots",
	197: "Frozen Glove Left",
	198: "Frozen Glove Right",
	199: "Frozen Backpack",
	200: "Icy Broadsword",
	201: "Icy Broadsword Atk.47",
	202: "Icy Broadsword Atk.49",
	203: "Icy Bow",
	204: "Icy Bow Atk.47",
	205: "Icy Bow Atk.49",
	206: "Icy Wand",
	207: "Icy Wand Atk.47",
	208: "Icy Wand Atk.49",
	209: "Icy Shield",
	210: "Icy Shield Ar.55",
	211: "Icy Shield Ar.56",
	212: "Defense Necklace",
	213: "Magic Necklace",
	214: "Melee Necklace",
	215: "Distance Necklace",
	216: "Lizard Armor Ar.38",
	217: "Lizard Armor Ar.40",
	218: "Lizard Light Armor Ar.19",
	219: "Lizard Light Armor Ar.20",
	220: "Lizard Robe Ar.13",
	221: "Lizard Robe Ar.14",
	222: "Lizard Helmet Ar.25",
	223: "Lizard Helmet Ar.26",
	224: "Lizard Hood Ar.13",
	225: "Lizard Hood Ar.14",
	226: "Lizard Hat Ar.7",
	227: "Lizard Hat Ar.8",
	228: "Lizard Belt Ar.19",
	229: "Lizard Belt Ar.20",
	230: "Lizard Legs Ar.32",
	231: "Lizard Legs Ar.34",
	232: "Lizard Boots Ar.19",
	233: "Lizard Boots Ar.20",
	234: "Lizard Glove Left Ar.13",
	235: "Lizard Glove Left Ar.14",
	236: "Lizard Glove Right Ar.13",
	237: "Lizard Glove Right Ar.14",
	238: "Green Backpack Ca.58",
	239: "Green Backpack Ca.60",
	240: "Dragon Armor Ar.44",
	241: "Dragon Armor Ar.46",
	242: "Dragon Light Armor Ar.22",
	243: "Dragon Light Armor Ar.23",
	244: "Dragon Robe Ar.15",
	245: "Dragon Robe Ar.16",
	246: "Dragon Helmet Ar.29",
	247: "Dragon Helmet Ar.30",
	248: "Dragon Hood Ar.15",
	249: "Dragon Hood Ar.16",
	250: "Dragon Hat Ar.8",
	251: "Dragon Hat Ar.9",
	252: "Dragon Belt Ar.22",
	253: "Dragon Belt Ar.23",
	254: "Dragon Legs Ar.37",
	255: "Dragon Legs Ar.39",
	256: "Dragon Boots Ar.22",
	257: "Dragon Boots Ar.23",
	258: "Dragon Glove Left Ar.15",
	259: "Dragon Glove Left Ar.16",
	260: "Dragon Glove Right Ar.15",
	261: "Dragon Glove Right Ar.16",
	262: "Dragon Backpack Ca.66",
	263: "Dragon Backpack Ca.68",
	264: "Frozen Armor Ar.50",
	265: "Frozen Armor Ar.52",
	266: "Frozen Light Armor Ar.25",
	267: "Frozen Light Armor Ar.26",
	268: "Frozen Robe Ar.17",
	269: "Frozen Robe Ar.18",
	270: "Frozen Helmet Ar.33",
	271: "Frozen Helmet Ar.34",
	272: "Frozen Hood Ar.17",
	273: "Frozen Hood Ar.18",
	274: "Frozen Hat Ar.9",
	275: "Frozen Hat Ar.10",
	276: "Frozen Belt Ar.25",
	277: "Frozen Belt Ar.26",
	278: "Frozen Legs Ar.42",
	279: "Frozen Legs Ar.44",
	280: "Frozen Boots Ar.25",
	281: "Frozen Boots Ar.26",
	282: "Frozen Glove Left Ar.17",
	283: "Frozen Glove Left Ar.18",
	284: "Frozen Glove Right Ar.17",
	285: "Frozen Glove Right Ar.18",
	286: "Frozen Backpack Ca.74",
	287: "Frozen Backpack Ca.76",
	288: "Golden Glove Left",
	289: "Golden Glove Right",
	290: "Superior Defense Necklace",
	291: "Superior Magic Necklace",
	292: "Superior Melee Necklace",
	293: "Superior Distance Necklace",
	294: "Town Scroll Lv.150",
	295: "Assassin's Key",
	296: "Vampire's Key",
	297: "Drow's Key",
	298: "Lizard's Key",
	306: "Gargoyle Hat",
	308: "Gargoyle Armor",
	309: "Gargoyle Armor Ar.38",
	310: "Gargoyle Armor Ar.40",
	311: "Gargoyle Light Armor",
	313: "Gargoyle Light Armor Ar.20",
	314: "Gargoyle Robe",
	315: "Gargoyle Robe Ar.13",
	316: "Gargoyle Robe Ar.14",
	326: "Gargoyle Legs",
	327: "Gargoyle Legs Ar.32",
	331: "Gargoyle Boots Ar.20",
	333: "Gargoyle Backpack Ca.58",
	335: "Gargoyle Slayer",
	337: "Gargoyle Slayer Atk.39",
	339: "Gargoyle Shield Ar.42",
	340: "Gargoyle Shield Ar.42",
	346: "Gargoyle Wand Atk.39",
	347: "Death Charm",
	348: "Return Scroll",
	349: "Gargoyle's Key",
	353: "Healer Helmet (Gold)",
	360: "Healer Boots (Blue)",
	361: "Healer Boots (Purple)",
	362: "Healer Boots (Gold)",
	363: "Healer Glove Right (Blue)",
	364: "Healer Glove Right (Purple)",
	365: "Healer Glove Right (Gold)",
	366: "Healer Glove Left (Blue)",
	367: "Healer Glove Left (Purple)",
	368: "Healer Glove Left (Gold)",
	369: "Healer Belt (Blue)",
	370: "Healer Belt (Purple)",
	372: "Healer Backpack",
	376: "Superior Healer Necklace",
	377: "Healer Ring",
	378: "Superior Healer Ring",
	380: "Recovery Helmet (Purple)",
	387: "Recovery Legs (Gold)",
	388: "Recovery Boots (Blue)",
	389: "Recovery Boots (Purple)",
	390: "Recovery Boots (Gold)",
	391: "Recovery Glove Right (Blue)",
	392: "Recovery Glove Right (Purple)",
	393: "Recovery Glove Right (Gold)",
	394: "Recovery Glove Left (Blue)",
	395: "Recovery Glove Left (Purple)",
	396: "Recovery Glove Left (Gold)",
	397: "Recovery Belt (Blue)",
	404: "Superior Recovery Necklace",
	405: "Recovery Ring",
	408: "Minotaur Helmet Ar.29",
	412: "Minotaur Hood Ar.16",
	413: "Minotaur Hat",
	414: "Minotaur Hat Ar.8",
	416: "Minotaur Armor",
	417: "Minotaur Armor Ar.44",
	418: "Minotaur Armor Ar.46",
	419: "Minotaur Light Armor",
	420: "Minotaur Light Armor Ar.22",
	421: "Minotaur Light Armor Ar.23",
	422: "Minotaur Robe",
	423: "Minotaur Robe Ar.15",
	424: "Minotaur Robe Ar.16",
	427: "Minotaur Belt Ar.23",
	429: "Minotaur Legs Ar.37",
	431: "Minotaur Boots",
	434: "Minotaur Glove Right",
	435: "Minotaur Glove Right Ar.15",
	436: "Minotaur Glove Right Ar.16",
	437: "Minotaur Glove Left",
	438: "Minotaur Glove Left Ar.15",
	439: "Minotaur Glove Left Ar.16",
	440: "Minotaur Backpack",
	441: "Minotaur Backpack Ca.66",
	442: "Minotaur Backpack Ca.68",
	444: "Minotaur Slayer Atk.42",
	445: "Minotaur Slayer Atk.44",
	448: "Minotaur Bow Atk.44",
	449: "Minotaur Wand",
	452: "Minotaur Shield",
	456: "Training Bow Atk.4",
	458: "Destination Scroll",
	459: "Nose Ring",
	464: "Key Ring"
}

global_settings = {
	'resolve_levels': False,
	'pm_notifications': False,
	'pm_notify_email': "mr.jdwolfe@gmail.com",
	'upload_data': False,
	'myid': 0,
	'ignore': []
}

#main function to get called on packet payloads to direct processing to the suitable function
#returns payload if no match is found in the dictionary
def translator(argument, origin):
	try:
		if origin == "client":
			if argument[:3] == b'\x00\x01\x05':
				return alive()
			elif argument[:3] == b'\x00\x01\x00':
				return dead()
			elif argument[:3] == b'\x00\x01\x1a':
				return pickup()
			elif argument[:3] == b'\x00\x05\x03': 
				return attack(argument[3:])
			elif argument[:3] == b'\x00\x02\x06': 
				return weapon(argument[3:])
			elif argument[:3] == b'\x00\x05\x01': 
				return moveto(argument[3:])
			elif argument[:3] == b'\x00\x01\x04': 
				return revive()
			elif argument[:3] == b'\x00\x044':
				return useitem(argument[3:])
			elif argument[:3] == b'\x00\x05\r':
				return special(argument[3:])
			elif argument[:3] == b'\x00\x05\r': 
				return special(argument[3:])
			elif argument[:3] == b'\x00\x03\x18': 
				return equip(argument[3:])
			elif argument[:3] == b'\x00\x03%': 
				return unequip(argument[3:])
			elif argument[:3] == b'\x00\x05\x0b': 
				return merchant(argument[3:])
			elif argument[:3] == b'\x00\t\x19': 
				return drop(argument[3:])
			elif argument[:3] == b'\x00\x0d\x1b': 
				return sell(argument[3:])
			elif argument[:3] == b'\x00\x11\x0c':
				return buy(argument[3:])
			elif argument[:3] == b'\x00\x0b\x1c': 
				return selltoworld(argument[3:])
			elif argument[:3] == b'\x00\x03\x1d': 
				return stopsaleof(argument[3:])
			elif argument[:3] == b'\x00\x05\x27': 
				return withdraw(argument[3:])
			elif argument[:3] == b'\x00\x05\x26': 
				return deposit(argument[3:])
			elif argument[:3] == b'\x00\x09\x24': 
				return getfromvault(argument[3:])
			elif argument[:3] == b'\x00\x09\x23':
				return addtovault(argument[3:])
			elif argument[:3] == b'\x00\x01\x02': 
				return byebye()
			elif argument[:3] == b'\x00\x02\x16': 
				return pvpmode(argument[3:])
			elif argument[:3] == b'\x00\x0f\x0c': 
				return buyfromshop(argument[3:])
			elif argument[:3] == b'\x00\x07\x22': 
				return giftdimas(argument[3:])
			elif argument[:3] == b'\x00\x02\x30': 
				return setupshop(argument[3:])
			elif argument[:3] == b'\x00\x05\x10': 
				return invitetoteam(argument[3:])
			elif argument[:3] == b'\x00\x05\x14': 
				return expelfromteam(argument[3:])
			elif argument[2:3] == b'\n':
				return sendmsg(argument[3:])
			elif argument == b'':
				return ''
			else: 
				return argument
		else:
			if argument[:1] == b'\x0c': 
				return recmsg(argument[1:])
			elif argument[:1] == b'\x02':
				return servmsg(argument[1:])
			elif argument[:1] == b'\x07': 
				return endconvo()
			elif argument[:1] == b'\x08': 
				return gotcha(argument[1:])
			elif argument[:1] == b'\x09':
				return takeatk(argument[1:])
			elif argument[:1] == b'\x18':
				return hpmpupd(argument[3:])
			elif argument[:1] == b'\x17':
				return statupd(argument[1:])
			elif argument[:1] == b'\x00':
				return showobj(argument[1:])
			elif argument[:1] == b'\x0b':
				return bagupd(argument[1:])
			elif argument[:1] == b'\x01':
				return forget(argument[1:])
			elif argument[:1] == b'\x03':
				return shownums(argument[1:])
			elif argument[:1] == b'\x15':
				return showstore(argument[3:])
			elif argument[:1] == b'\x23':
				return hashtag(argument[1:])
			elif argument[:1] == b'\x1e':
				return cantsee(argument[1:])
			elif argument[:1] == b'\x1c':
				return mystery_one(argument[1:])
			elif argument[:1] == b'\x1b':
				return youhave(argument[1:])
			elif argument[:1] == b'\x2f':
				return redmsg(argument[1:])
			elif argument[:1] == b'\x04':
				return levelup(argument[1:])
			elif argument[:1] == b'\x1a':
				return mystery_three(argument[1:])
			elif argument[:1] == b'\x20':
				return mystery_four(argument[1:])
			elif argument[:1] == b'\x22':
				return youare(argument[1:])
			elif argument[:1] == b'\x1f':
				return mystery_two(argument[1:])
			elif argument[:1] == b'\x0d':
				return mystery_five(argument[1:])
			elif argument[:1] == b'\x2d':
				#temporarily using mystery_five cuz arguments are only 4 bytes too
				return mystery_five(argument[1:])
			elif argument[:1] == b'\x24':
				return friendlist(argument[1:])
			elif argument[:1] == b'\x25':
				return mystery_six(argument[1:])
			elif argument[:1] == b'\x27':
				return mystery_six(argument[1:])
			elif argument == b'':
				return ''
			else:
				return str(argument)
	except Exception as e:
		return "An unknown error occurred - translator - {}".format(e)


def modify(lookatme, modme):
	if modme == b'\x00\x02\x30\x00':
		return lookatme
	swap_target = modme[:3]
	if lookatme.find(swap_target) == 0:
		return modme
	else:
		return lookatme

def spill(guts):
	allhex = binascii.hexlify(guts)
	gutlist = wrap(str(allhex), 2)
	gutlist.pop(0)
	gutlist.pop(-1)
	finalguts = ''
	for eachbyte in gutlist:
		finalguts += '\\x{}'.format(eachbyte)
	return finalguts

def prettyreturn(terpd):
	toformat = terpd.split('|')
	g2g = "Server >>> {}\n".format(toformat[0])
	toformat.pop(0)
	for line in toformat:
		if line != '':
			g2g += "s      >>> {}\n".format(line)
	return g2g[:-1]


#------------------Server side down below------------------#

def friendlist(friends):
	try:
		#\x24
		lastindex = 0
		returnable = ""
		max_friends = int(binascii.hexlify(friends[:2]), 16)
		friends_now = int(binascii.hexlify(friends[2:4]), 16)
		returnable += "You currently have {} out of {} friends.|".format(friends_now, max_friends)
		lastindex += 4
		if friends_now != 0:
			returnable += "Your friends are: |"
			status = ""
			for spot in range(friends_now):
				name_length = int(binascii.hexlify(friends[lastindex+6:lastindex+7]), 16)
				lastindex += 7
				name = friends[lastindex:lastindex+name_length].decode()
				lastindex += name_length
				offline = int(binascii.hexlify(friends[lastindex:lastindex+1]), 16)
				if offline == 0:
					status = "Offline"
				else:
					status = "Online"
				lastindex += 1
				returnable += "Slot {}: {}, Status: {}.|".format(spot+1, name, status)
		if 'friendlist' not in filters:
				returnable = ''
		if friends[lastindex:] == b'':
			return returnable
		else:
			if friends[lastindex:lastindex+1] == b'\x2e':
				lastindex += 1
			return "{}{}".format(returnable, translator(friends[lastindex:], "server"))
	except Exception as e:
		return "An unknown error occurred - friendlist - {}".format(e)

def mystery_one(skipme):
	try:
		# \x1c
		skip = int(binascii.hexlify(skipme[:1]), 16)
		skip *= 2
		skip += 1
		if skipme[skip:] == b'':
			return ""
		else:
			return "{}".format(translator(skipme[skip:], "server"))
	except Exception as e:
		return "An unknown error occurred - mystery1 - {}".format(e)

def mystery_two(skipme):
	try:
		# \x1f 
		skip = int(binascii.hexlify(skipme[10:12]), 16)
		skip *= 4
		skip += 12
		if skipme[skip:] == b'':
			return ""
		else:
			return "{}".format(translator(skipme[skip:], "server"))
	except Exception as e:
		return "An unknown error occurred - mystery2 - {}".format(e)

def mystery_three(skipme):
	try:
		# \x1a 
		#testing...
		#return str(skipme)
		#testing...
		if skipme[8:] == b'':
			return ""
		else:
			if skipme[:4] == b'\x14\x03\x00\x01':
				return "{}".format(translator(skipme[26:], "server"))
			elif skipme[8:9] == b'\x03':
				return "{}".format(translator(skipme[9:], "server"))
			else:
				return "{}".format(translator(skipme[8:], "server"))
	except Exception as e:
		return "An unknown error occurred - mystery3 - {}".format(e)

def mystery_four(skipme):
	try:
		# \x20 
		if skipme[25:] == b'':
			return ""
		else:
			return "{}".format(translator(skipme[21:], "server"))
	except Exception as e:
		return "An unknown error occurred - mystery4 - {}".format(e)

def mystery_five(skipme):
	try:
		# \x20 
		if skipme[4:] == b'':
			return ""
		else:
			return "{}".format(translator(skipme[4:], "server"))
	except Exception as e:
		return "An unknown error occurred - mystery5 - {}".format(e)

def mystery_six(skipme):
	try:
		# \x20 
		# I'm pretty sure this is about friends coming online/offline but frankly...
		# who cares?
		if skipme[7:] == b'':
			return ""
		else:
			return "{}".format(translator(skipme[7:], "server"))
	except Exception as e:
		return "An unknown error occurred - mystery6 - {}".format(e)

def youare(number):
	try:
		# \x22
		player_id = int(binascii.hexlify(number[2:6]), 16)
		#playerdict("--Me-- Lvl. ??", player_id)
		returnable = "You will have the ID of {} for this session.|".format(player_id)
		global_settings['myid'] = player_id
		if 'youare' not in filters:
			returnable = ''
		if number[6:] == b'':
			return returnable
		else:
			return "{}{}".format(returnable, translator(number[6:], "server"))
	except Exception as e:
		return "An unknown error occurred - youare - {}".format(e)

def levelup(alert):
	try:
		# \x04 
		msg_length = int(binascii.hexlify(alert[1:2]), 16)
		message = alert[2:msg_length+2].decode()
		returnable = "Alert: {}.|".format(message)
		if 'whitemsg' not in filters:
			returnable = ''
		else:
			if 'online' not in message:
				my_name = playerdict('get', global_settings['myid'])
				if my_name.find('#') >= 0:
					my_name = 'idk'
				else:
					my_name = my_name.split(' Lv')[0]
				
				if message.find('exhaust') >= 0:
					if bp != 'monitor':
						bq.put('exhaust|0')
				elif message.find('training') >= 0:
					pass
				elif message.find('level') >= 0:
					if my_name == 'idk':
						toastme = "Congratulations! {}".format(message)
					else:
						toastme = "Congratulations, {}! {}".format(my_name, message)
					toaster.show_toast("Rucoy Bot", toastme, icon_path="robot.ico", duration=5, threaded=True)
					if global_settings['pm_notifications']:
						pq.put('send|{}|{}|{}'.format(global_settings['pm_notify_email'], my_name, toastme))
				else:
					pass
					'''
					if my_name == 'idk':
						toastme = "{}".format(message)
					else:
						toastme = "{}, {}".format(my_name, message)
					toaster.show_toast("Rucoy Bot", toastme, icon_path="robot.ico", duration=5, threaded=True)
					if global_settings['pm_notifications']:
						pq.put('send|{}|{}|{}'.format(global_settings['pm_notify_email'], my_name, toastme))
					'''
		if len(alert) > msg_length+2:
			if message.find('online') >= 0:
				return "{}{}".format(returnable, translator(alert[msg_length+3:], "server"))
			else:
				return "{}{}".format(returnable, translator(alert[msg_length+2:], "server"))
		return returnable
	except Exception as e:
		return "An unknown error occurred - levelup - {}".format(e)

def youhave(dimas):
	try:
		# \x1b 
		returnable = ""
		diamonds = int(binascii.hexlify(dimas[4:8]), 16)
		max_dimas = int(binascii.hexlify(dimas[8:12]), 16)
		returnable += "You have {:,d} diamonds and can gift/sell {:,d} diamonds.|".format(diamonds, max_dimas)
		if 'dimas' not in filters:
			returnable = ''
		offset = 13 + int(binascii.hexlify(dimas[12:13]), 16)
		if len(dimas) > offset:
			return "{}{}".format(returnable, translator(dimas[offset:], "server"))
		else:
			return returnable
	except Exception as e:
		return "An unknown error occurred - youhave - {}".format(e)

def redmsg(warning):
	try:
		# \x2f 
		msg_length = int(binascii.hexlify(warning[:1]), 16)+1
		warning_msg = warning[1:msg_length].decode()
		returnable = "Warning: {} |".format(warning_msg)
		if 'redmsg' not in filters:
			returnable = ''
		else:
			my_name = playerdict('get', global_settings['myid'])
			if my_name.find('#') >= 0:
				my_name = 'idk'
			else:
				my_name = my_name.split(' Lv')[0]
			if my_name == 'idk':
				toastme = "Warning! {}".format(warning_msg)
			else:
				toastme = "Warning! {}, {}".format(my_name, warning_msg)
			toaster.show_toast("Rucoy Bot", toastme, icon_path="robot.ico", duration=5, threaded=True)
		if warning[msg_length+1:] == b'':
			return returnable
		else:
			return "{}{}".format(returnable, translator(warning[msg_length+1:], "server"))
	except Exception as e:
		return "An unknown error occurred - redmsg - {}".format(e)

def cantsee(thing):
	try:
		# \x1e 
		stalktgt = int(binascii.hexlify(thing[:4]), 16)
		monster_id = monsterdict("get", stalktgt)
		if monster_id != '0':
			if 'select' not in filters:
				returnable = ''
			else:
				returnable = "Attack {} on site.|".format(monster_id)
		else:
			returnable = ''
		if len(thing) > 8:
			if thing[8:9] == b'\x0d':
				return "{}{}".format(returnable, translator(thing[13:], "server"))
			else:
				return "{}{}".format(returnable, translator(thing[8:], "server"))
		else:
			return returnable
	except Exception as e:
		return "An unknown error occurred - cantsee - {}".format(e)

def showstore(offoron):
	try:
		# \x15 
		if offoron[:1] == b'\x01':
			returnable = "You can set up a store here.|"
		if offoron[:1] == b'\x00':
			returnable = "You can no longer set up a store.|"
		if 'shop' not in filters:
			returnable = ''
		if len(offoron) > 1:
			return "{}{}".format(returnable, translator(offoron[1:], "server"))
		else:
			return returnable
	except Exception as e:
		return "An unknown error occurred - showstore - {}".format(e)

def recmsg(server_message):
	try:
		# \x0c 
		sources = {
			b'\x00': "Local",
			b'\x01': "Server",
			b'\x02': "Team",
			b'\x03': "Direct"
		}
		source = sources.get(server_message[:1])
		
		if source == "Local" and server_message[1:2] == b'\x04':
			msg_length = int(binascii.hexlify(server_message[6:7]), 16)
			notification = server_message[7:7+msg_length].decode()
			returnable = "System Notification: '{}' |".format(notification)
			s_length = 7+msg_length
			if s_length < len(server_message):
				returnable += translator(server_message[s_length:], "server")
		elif source != "Direct":
			playerid = int(binascii.hexlify(server_message[2:6]), 16)
			s_length = int(binascii.hexlify(server_message[6:7]), 16)+7
			namewithmsg = server_message[7:s_length].decode()
			if source == "Local" and namewithmsg.find(playerdict('get', global_settings['myid'])) != 0:
				toaster.show_toast("Rucoy Bot", namewithmsg, icon_path="robot.ico", duration=5, threaded=True)
			if global_settings['pm_notifications'] and source == "Local":
				my_name = playerdict('get', global_settings['myid'])
				if my_name.find('#') >= 0:
					my_name = 'idk'
				else:
					my_name = my_name.split(' Lv')[0]
				if namewithmsg.find(my_name) != 0:
					pq.put('send|{}|{}|{}'.format(global_settings['pm_notify_email'], my_name, namewithmsg))
			if global_settings['resolve_levels']:
				nametoadd = namewithmsg.split(':')[0]
				lvltoadd = getlvl(nametoadd)
				message = namewithmsg.split(':')[1]
				returnable = "{} message from Player {}, '{} ({}): {}' |".format(source, playerid, nametoadd, lvltoadd, message)
			else:
				returnable = "{} message from Player {}, '{}' |".format(source, playerid, namewithmsg)
			if s_length < len(server_message):
				returnable += translator(server_message[s_length:], "server")
		else:
			name_length = int(binascii.hexlify(server_message[1:2]), 16)
			msgspot = 3+name_length+4
			msg_length = int(binascii.hexlify(server_message[msgspot:msgspot+1]), 16)
			s_length = msgspot+1+msg_length
			namewithmsg = server_message[msgspot+1:s_length].decode()
			if namewithmsg.find(playerdict('get', global_settings['myid'])) != 0:
				toaster.show_toast("Rucoy Bot", namewithmsg, icon_path="robot.ico", duration=5, threaded=True)
			returnable = "{} message from player: '{}' |".format(source, namewithmsg)
			if global_settings['pm_notifications']:
				my_name = playerdict('get', global_settings['myid'])
				if my_name.find('#') >= 0:
					my_name = 'idk'
				else:
					my_name = my_name.split(' Lv')[0]
				if namewithmsg.find(my_name) != 0:
					pq.put('send|{}|{}|{}'.format(global_settings['pm_notify_email'], my_name, namewithmsg))
			if s_length < len(server_message):
				returnable += translator(server_message[s_length:], "server")
		if 'messages' not in filters:
			returnable = ''
		return returnable
	except Exception as e:
		return "An unknown error occurred - recmsg - {}".format(e)

def servmsg(msg):
	#\x02
	return "{}".format(translator(msg[1:], "server"))

def getlvl(name):
	try:
		name = name.replace(' ', '%20')
		url = 'https://www.rucoyonline.com/characters/{}'.format(name)
		response = requests.get(url)
		soup = beso(response.text, "html.parser")
		level = str(soup.findAll('td')[4]).split('>')[1].split('<')[0]
		return level
	except:
		return '0'

def endconvo():
	# \x07 
	if bp != 'monitor':
		bq.put('ended|0')
	if 'disconnect' in filters:
		return "End Communications.|"
	else:
		return ''

def gotcha(salute):
	try:
		# \x08 
		if salute == b'':
			return "Acknowledged.|"
		else:
			return "{}{}".format("Acknowledged.|", translator(salute, "server"))
	except Exception as e:
		return "An unknown error occurred - gotcha - {}".format(e)

def forget(what):
	try:
		# \x01 
		lastindex = 0
		returnable = ""
		while lastindex < len(what):
			if what[lastindex:lastindex+1] == b'\x01' and lastindex != 0:
				thing_id = int(binascii.hexlify(what[lastindex+1:lastindex+5]), 16)
				what_id = playerdict("get", thing_id)
				if thing_id < 70000:
					monster_id = monsterdict("get", thing_id)
					if bp != 'monitor' and monster_id.find(attack_me) >= 0:
						bq.put('forget|{}'.format(thing_id))
					monsterdict("del", int(binascii.hexlify(what[lastindex+1:lastindex+5]), 16))
					returnable += "Monster {} is now out of range.|".format(monster_id)
				else:
					playerdict("del", int(binascii.hexlify(what[lastindex+1:lastindex+5]), 16))
					returnable += "Player {} is now out of range.|".format(what_id)
				lastindex += 5
			elif lastindex == 0:
				thing_id = int(binascii.hexlify(what[lastindex:lastindex+4]), 16)
				what_id = playerdict("get", thing_id)
				if thing_id < 70000:
					monster_id = monsterdict("get", thing_id)
					if bp != 'monitor' and monster_id.find(attack_me) >= 0:
						bq.put('forget|{}'.format(thing_id))
					monsterdict("del", int(binascii.hexlify(what[lastindex:lastindex+4]), 16))
					returnable += "Monster {} is now out of range.|".format(monster_id)
				else:
					playerdict("del", int(binascii.hexlify(what[lastindex:lastindex+4]), 16))
					returnable += "Player {} is now out of range.|".format(what_id)
				lastindex += 4
			else:
				if 'forget' not in filters:
					returnable = ''
				return "{}{}".format(returnable, translator(what[lastindex:], "server"))
		if 'forget' not in filters:
			returnable = ''
		return returnable
	except Exception as e:
		return "An unknown error occurred - forget - {}".format(e)


def takeatk(whotowho):
	try:
		# \x09 
		lastindex = 0
		returnable = ""
		while lastindex < len(whotowho):
			if whotowho[lastindex:lastindex+1] == b'\x09' and lastindex != 0:
				monster_id = int(binascii.hexlify(whotowho[lastindex+1:lastindex+5]), 16)
				victim_id = int(binascii.hexlify(whotowho[lastindex+5:lastindex+9]), 16)
				lastindex += 10
				if monster_id > 65536:
					if victim_id == global_settings['myid'] and monster_id not in global_settings['ignore']:
						global_settings['ignore'].append(monster_id)
						my_name = playerdict('get', global_settings['myid'])
						if my_name.find('#') >= 0:
							my_name = 'idk'
						else:
							my_name = my_name.split(' Lv')[0]
						mofo = playerdict("get", monster_id)
						if mofo.find('#') >= 0:
							message = "Hurry and fight back! This asshole is attacking you! FIGHT OR DIE!".format(mofo)
						else:
							message = "Hurry and fight back! This '{}' is attacking you! FIGHT OR DIE!".format(mofo)
						toastme = "Warning! {}".format(message)
						toaster.show_toast("Rucoy Bot", toastme, icon_path="robot.ico", duration=5, threaded=True)
						if global_settings['pm_notifications']:
							pq.put('send|{}|{}|{}'.format(global_settings['pm_notify_email'], my_name, toastme))
					if monster_id == global_settings['myid']:
						if bp != 'monitor' and monsterdict("get", monster_id).find(attack_me) >= 0:
							bq.put('takeatk|0')
					else:
						if bp != 'monitor' and monsterdict("get", monster_id).find(attack_me) >= 0:
							bq.put('taken|{}'.format(monster_id))
					player_id = playerdict("get", monster_id)
					monster_id = monsterdict("get", victim_id)
					returnable += "Player {} attacks monster {}.|".format(player_id, monster_id)
				else:
					if victim_id == global_settings['myid']:
						if bp != 'monitor' and monsterdict("get", monster_id).find(attack_me) >= 0:
							bq.put('forgive|{}'.format(monster_id))
					else:
						if bp != 'monitor':
							bq.put('taken|{}'.format(monster_id))
					monster_id = monsterdict("get", monster_id)
					victim_id = playerdict("get", victim_id)
					returnable += "Monster {} attacks player {}.|".format(monster_id, victim_id)
			elif lastindex == 0:
				monster_id = int(binascii.hexlify(whotowho[lastindex:lastindex+4]), 16)
				victim_id = int(binascii.hexlify(whotowho[lastindex+4:lastindex+8]), 16)
				lastindex += 9
				if monster_id > 65536:
					if victim_id == global_settings['myid'] and monster_id not in global_settings['ignore']:
						global_settings['ignore'].append(monster_id)
						my_name = playerdict('get', global_settings['myid'])
						if my_name.find('#') >= 0:
							my_name = 'idk'
						else:
							my_name = my_name.split(' Lv')[0]
						mofo = playerdict("get", monster_id)
						if mofo.find('#') >= 0:
							message = "Hurry and fight back! This asshole is attacking you! FIGHT OR DIE!".format(mofo)
						else:
							message = "Hurry and fight back! This '{}' is attacking you! FIGHT OR DIE!".format(mofo)
						toastme = "Warning! {}".format(message)
						toaster.show_toast("Rucoy Bot", toastme, icon_path="robot.ico", duration=5, threaded=True)
						if global_settings['pm_notifications']:
							pq.put('send|{}|{}|{}'.format(global_settings['pm_notify_email'], my_name, toastme))
					if monster_id == global_settings['myid']:
						if bp != 'monitor':
							bq.put('takeatk|0')
					else:
						if bp != 'monitor':
							bq.put('taken|{}'.format(monster_id))
					player_id = playerdict("get", monster_id)
					monster_id = monsterdict("get", victim_id)
					returnable += "Player {} attacks monster {}.|".format(player_id, monster_id)
				else:
					if victim_id == global_settings['myid']:
						if bp != 'monitor':
							bq.put('forgive|{}'.format(monster_id))
					else:
						if bp != 'monitor':
							bq.put('taken|{}'.format(monster_id))
					monster_id = monsterdict("get", monster_id)
					victim_id = playerdict("get", victim_id)
					returnable += "Monster {} attacks player {}.|".format(monster_id, victim_id)
			else:
				if 'attack' not in filters:
					returnable = ''
				return "{}{}".format(returnable, translator(whotowho[lastindex:], "server"))
		if 'attack' not in filters:
			returnable = ''
		return returnable
	except Exception as e:
		return "An unknown error occurred - takeatk - {}".format(e)

def shownums(whoandnum):
	try:
		# \x03 
		returnable = ""
		lastindex = 0
		while lastindex < len(whoandnum):
			if whoandnum[lastindex:lastindex+1] == b'\x03':
				lastindex += 1
			else:
				if lastindex != 0:
					if 'shownums' not in filters:
						returnable = ''
					return "{}{}".format(returnable, translator(whoandnum[lastindex:], "server"))
			if whoandnum[lastindex:lastindex+2] == b'\x00\x00':
				monster = "true"
				target = monsterdict("get", int(binascii.hexlify(whoandnum[lastindex:lastindex+4]), 16))
			else:
				monster = "false"
				target = playerdict("get", int(binascii.hexlify(whoandnum[lastindex:lastindex+4]), 16))
			dmgorxp = int(binascii.hexlify(whoandnum[lastindex+4:lastindex+8]), 16)
			if whoandnum[lastindex+8:lastindex+9] == b'\x00':
				returnable += "Player {} gained {:,d} xp.|".format(target, dmgorxp)
			elif whoandnum[lastindex+8:lastindex+9] == b'\x01':
				returnable += "Player {} gained {:,d} health.|".format(target, dmgorxp)
			elif whoandnum[lastindex+8:lastindex+9] == b'\x03':
				returnable += "Player {} gained {:,d} mana.|".format(target, dmgorxp)
			else:
				if monster == "true":
					returnable += "Monster {} suffered {:,d} in damage.|".format(target, dmgorxp)
				else:
					returnable += "Player {} suffered {:,d} in damage.|".format(target, dmgorxp)
			lastindex += 9
		if 'shownums' not in filters:
			returnable = ''
		return returnable
	except Exception as e:
		return "An unknown error occurred - shownums - {}".format(e)

def showobj(whattoshow):
	try:
		#\x00 
		lastindex = 0
		returnable = ""
		pqputted = False
		if len(whattoshow) <= 4:
			if 'move' not in filters:
				return '{}'.format(returnable)
			else:
				return "{}Start connection.|".format(returnable)
		while lastindex <= len(whattoshow):
			if lastindex != 0 and whattoshow[lastindex-1:lastindex+1] != b'\x00\x00':
				if pqputted == True and global_settings['upload_data']:
					pq.put('done|0|0')
				if 'move' not in filters:
					returnable = ''
				return "{}{}".format(returnable, translator(whattoshow[lastindex-1:], "server"))
			elif whattoshow[lastindex:lastindex+2] == b'\x00\x00':
				monster_num = int(binascii.hexlify(whattoshow[lastindex:lastindex+4]), 16)
				monster_id = monsterdict("get", monster_num)
				if whattoshow[lastindex+4:lastindex+7] == b'\x01\x01\x01':
					lastindex += 7
					x_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					lastindex += 2
					y_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+2:lastindex+3]), 16)
					if whattoshow[lastindex+4:] != b'':
						extra = int(binascii.hexlify(whattoshow[lastindex+7:lastindex+8]), 16)
						lastindex += 8
						if extra != 0:
							for x in range(extra):
								x += lastindex
								extra_move = int(binascii.hexlify(whattoshow[x:x+1]), 16)
								if extra_move == 1:
									x_coord += 1
								elif extra_move == 2:
									y_coord += 1
								elif extra_move == 3:
									x_coord -= 1
								else:
									y_coord -= 1
					else:
						extra = 0
					returnable += "Monster {} moved to {}, {}.|".format(monster_id, x_coord, y_coord)
					if bp != 'monitor' and monster_id.find(attack_me) >= 0:
						bq.put("monster|{}|{}:{},{},{}".format(monster_num, monster_id, x_coord, y_coord, z_coord))
					lastindex += (4 + extra)
				elif whattoshow[lastindex+4:lastindex+7] == b'\x01\x01\x00':
					lastindex += 7
					x_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					lastindex += 2
					y_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+2:lastindex+3]), 16)
					returnable += "Monster {} moved to {}, {}.|".format(monster_id, x_coord, y_coord)
					if bp != 'monitor' and monster_id.find(attack_me) >= 0:
						bq.put("monster|{}|{}:{},{},{}".format(monster_num, monster_id, x_coord, y_coord, z_coord))
					lastindex += 4
				elif whattoshow[lastindex+4:lastindex+7] == b'\x02\x01\x00':
					lastindex += 7
					x_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					lastindex += 2
					y_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+2:lastindex+3]), 16)
					returnable += "Monster {} moved to {}, {}.|".format(monster_id, x_coord, y_coord)
					if bp != 'monitor' and monster_id.find(attack_me) >= 0:
						bq.put("monster|{}|{}:{},{},{}".format(monster_num, monster_id, x_coord, y_coord, z_coord))
					if whattoshow[lastindex+3:lastindex+5] == b'\x06\x64':
						lastindex += 6
					else:
						lastindex += 7
				elif whattoshow[lastindex+4:lastindex+7] == b'\x03\x02\x01':
					who_byte = whattoshow[lastindex+7:lastindex+8]
					monster_name = monsterdict("get", who_byte)
					try:
						monsterdict(monster_name, int(monster_id))
					except:
						# Monster_ID was already resolved to a name so do nothing
						abc = 1
					extraflag = int(binascii.hexlify(whattoshow[lastindex+12:lastindex+13]), 16)
					lastindex += 13
					x_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					lastindex += 2
					y_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+2:lastindex+3]), 16)
					returnable += "Monster {} is at {}, {} and is a {}.|".format(monster_id, x_coord, y_coord, monster_name)
					if bp != 'monitor' and monster_name.find(attack_me) >= 0:
						bq.put("monster|{}|{}:{},{},{}".format(monster_num, monster_name, x_coord, y_coord, z_coord))
					lastindex += 4
					if extraflag == 1:
						last_offset = int(binascii.hexlify(whattoshow[lastindex+3:lastindex+4]), 16)
						lastindex += 8+last_offset
					if whattoshow[lastindex-1:lastindex] == b'\x1a':
						last_offset = int(binascii.hexlify(whattoshow[lastindex+3:lastindex+4]), 16)
						lastindex += 9+last_offset
				elif whattoshow[lastindex+4:lastindex+7] == b'\x03\x02\x03':
					name_length = int(binascii.hexlify(whattoshow[lastindex+7:lastindex+8]), 16)
					lastindex += 8
					name = whattoshow[lastindex:lastindex+name_length].decode()
					monsterdict(name, monster_id)
					lastindex += name_length
					lastindex += 7
					x_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					lastindex += 2
					y_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+2:lastindex+3]), 16)
					lastindex += 4
					if name.find('Merchant') > 0:
						returnable += "The {} will have the id of {} for this session.|".format(name, monster_id)
						if name == 'Gear Merchant':
							lastindex += 315
						elif name == 'Supplies Merchant':
							lastindex += 351
						else:
							lastindex += 0
					else:
						returnable += "The {} will have the id of {} for this session and is at {}, {}.|".format(name, monster_id, x_coord, y_coord)
						if bp != 'monitor' and name.find(attack_me) >= 0:
							bq.put("monster|{}|{}:{},{},{}".format(monster_num, name, x_coord, y_coord, z_coord))
				elif whattoshow[lastindex+4:lastindex+7] == b'\x03\x02\x04':
					x_coord = int(binascii.hexlify(whattoshow[lastindex+11:lastindex+13]), 16)
					y_coord = int(binascii.hexlify(whattoshow[lastindex+13:lastindex+15]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+15:lastindex+16]), 16)
					lastindex += 17
					returnable += "The item or monster at {}, {} has been removed from the map.|".format(x_coord, y_coord)
				elif whattoshow[lastindex+4:lastindex+7] == b'\x03\x02\x05':
					x_coord = int(binascii.hexlify(whattoshow[lastindex+12:lastindex+14]), 16)
					y_coord = int(binascii.hexlify(whattoshow[lastindex+14:lastindex+16]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+16:lastindex+17]), 16)
					lastindex += 18
					returnable += "A gate is at {}, {}.|".format(x_coord, y_coord)
				elif whattoshow[lastindex+4:lastindex+6] == b'\x01\x06':
					returnable += "Monster: {} exists.|".format(monster_id)
					lastindex += 8
				else:
					if 'move' not in filters:
						return ''
					return "Idk what the hell happened - {}".format(whattoshow[lastindex+4:lastindex+7])
			else:
				player_num = int(binascii.hexlify(whattoshow[lastindex:lastindex+4]), 16)
				player_id = playerdict("get", player_num)
				if whattoshow[lastindex+4:lastindex+7] == b'\x01\x01\x01':
					lastindex += 7
					x_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					lastindex += 2
					y_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+2:lastindex+3]), 16)
					if whattoshow[lastindex+4:] != b'':
						extra = int(binascii.hexlify(whattoshow[lastindex+7:lastindex+8]), 16)
						lastindex += 8
						if extra != 0:
							for x in range(extra):
								x += lastindex
								extra_move = int(binascii.hexlify(whattoshow[x:x+1]), 16)
								if extra_move == 1:
									x_coord += 1
								elif extra_move == 2:
									y_coord += 1
								elif extra_move == 3:
									x_coord -= 1
								else:
									y_coord -= 1
					else:
						extra = 0
					returnable += "Player {} moved to {}, {}.|".format(player_id, x_coord, y_coord)
					if player_num == global_settings['myid']:
						if bp != 'monitor':
							bq.put('coords|{},{},{}'.format(x_coord, y_coord, z_coord))
					lastindex += (4 + extra)
				elif whattoshow[lastindex+4:lastindex+7] == b'\x01\x01\x00':
					lastindex += 7
					x_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					lastindex += 2
					y_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+2:lastindex+3]), 16)
					returnable += "Player {} moved to {}, {}.|".format(player_id, x_coord, y_coord)
					if player_num == global_settings['myid']:
						if bp != 'monitor':
							bq.put('coords|{},{},{}'.format(x_coord, y_coord, z_coord))
					lastindex += 4
				elif whattoshow[lastindex+4:lastindex+7] == b'\x02\x01\x00':
					lastindex += 7
					x_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					lastindex += 2
					y_coord = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+2:lastindex+3]), 16)
					returnable += "Player {} moved to {}, {}.|".format(player_id, x_coord, y_coord)
					if player_num == global_settings['myid']:
						if bp != 'monitor':
							bq.put('coords|{},{},{}'.format(x_coord, y_coord, z_coord))
					if whattoshow[lastindex+3:lastindex+5] == b'\x06\x64':
						lastindex += 6
					else:
						lastindex += 7
				elif whattoshow[lastindex+4:lastindex+7] == b'\x03\x02\x02':
					itemid = int(binascii.hexlify(whattoshow[lastindex+8:lastindex+10]), 16)
					itemqty = int(binascii.hexlify(whattoshow[lastindex+10:lastindex+12]), 16)
					x_coord = int(binascii.hexlify(whattoshow[lastindex+14:lastindex+16]), 16)
					y_coord = int(binascii.hexlify(whattoshow[lastindex+16:lastindex+18]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+18:lastindex+19]), 16)
					lastindex += 20
					itemname = item_names.get(itemid, "#{}".format(itemid))
					if itemname == "Gold":
						returnable += "{:,d} gold dropped at {}, {}.|".format(itemqty, x_coord, y_coord)
						if bp != 'monitor':
							bq.put("drop|{}|{}:{}:{},{},{}".format(player_num, "Gold", itemqty, x_coord, y_coord, z_coord))
					else:
						returnable += "{} of item {} dropped at {}, {}.|".format(itemqty, itemname, x_coord, y_coord)
						if bp != 'monitor':
							bq.put("drop|{}|{}:{}:{},{},{}".format(player_num, itemname, itemqty, x_coord, y_coord, z_coord))
				elif whattoshow[lastindex+4:lastindex+7] == b'\x03\x02\x04':
					x_coord = int(binascii.hexlify(whattoshow[lastindex+11:lastindex+13]), 16)
					y_coord = int(binascii.hexlify(whattoshow[lastindex+13:lastindex+15]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+15:lastindex+16]), 16)
					lastindex += 17
					returnable += "The item or monster at {}, {} has been removed from the map.|".format(x_coord, y_coord)
				elif whattoshow[lastindex+4:lastindex+7] == b'\x01\x05\x00':
					lastindex += 7
					slots = int(binascii.hexlify(whattoshow[lastindex:lastindex+1]), 16)
					lastindex += 1
					slotsfull = int(binascii.hexlify(whattoshow[lastindex:lastindex+1]), 16)
					if slotsfull == 0:
						returnable += "Player {} now has 0 items selling in their store.|".format(player_id)
						lastindex += 1
					else:
						lastindex += 1
						itemid = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
						itemname = item_names.get(itemid, "#{}".format(itemid))
						lastindex += 2
						quantity = int(binascii.hexlify(whattoshow[lastindex:lastindex+2]), 16)
						lastindex += 2
						price = int(binascii.hexlify(whattoshow[lastindex:lastindex+4]), 16)
						lastindex += 6
						returnable += "Player {} added {} of item {} at the price of {}. Current slots {} out of {}.|".format(player_id, quantity, itemname, price, slotsfull, slots)
				elif whattoshow[lastindex+4:lastindex+7] == b'\x08\x02\x00':
					x_coord = int(binascii.hexlify(whattoshow[lastindex+9:lastindex+11]), 16)
					y_coord = int(binascii.hexlify(whattoshow[lastindex+11:lastindex+13]), 16)
					z_coord = int(binascii.hexlify(whattoshow[lastindex+13:lastindex+14]), 16)
					if player_num == global_settings['myid']:
						if bp != 'monitor':
							wpn = int(binascii.hexlify(whattoshow[lastindex+15:lastindex+16]), 16)
							bq.put('wpn|{}'.format(wpn))
							bq.put('coords|{},{},{}'.format(x_coord, y_coord, z_coord))
					if len(whattoshow) == lastindex+13:
						returnable += "Player {} moved to {}, {}.|".format(player_id, x_coord, y_coord)
						if 'move' not in filters:
							returnable = ''
						return returnable
					lastindex += 18
					namelenspot = whattoshow[lastindex:].find(b'\x0b')+1+lastindex
					name_length = int(binascii.hexlify(whattoshow[namelenspot:namelenspot+1]), 16)
					name = whattoshow[namelenspot+1:namelenspot+1+name_length].decode()
					level = int(binascii.hexlify(whattoshow[namelenspot+1+name_length:namelenspot+3+name_length]), 16)
					guild_length = int(binascii.hexlify(whattoshow[namelenspot+4+name_length:namelenspot+5+name_length]), 16)
					player_store_slots = int(binascii.hexlify(whattoshow[namelenspot+20+name_length+guild_length:namelenspot+21+name_length+guild_length]), 16)
					storeindex = namelenspot+21+name_length+guild_length
					storeinfo = "Player has nothing in their store.|"
					if player_store_slots > 0:
						storeinfo = "Player Store: |"
						for slot in range(player_store_slots):
							s_itemid = int(binascii.hexlify(whattoshow[storeindex:storeindex+2]), 16)
							storeitemid = item_names.get(s_itemid, "#{}".format(s_itemid))
							storeqty = int(binascii.hexlify(whattoshow[storeindex+2:storeindex+4]), 16)
							storeprice = int(binascii.hexlify(whattoshow[storeindex+4:storeindex+8]), 16)
							storeinfo += "Slot {}: {} of item {} for {:,d} gold.|".format(slot+1, storeqty, storeitemid, storeprice)
							storeindex += 9
							avgprice = int(storeprice/storeqty)
							if global_settings['upload_data']:
								pq.put('{}|{}|{}'.format(s_itemid, storeitemid, avgprice))
							pqputted = True
					playerdict("{} Lvl. {}".format(name, level), player_id[1:])
					#Take a quick break to send level to rucoy gui through StdOutQueue
					if player_num == global_settings['myid']:
						updatelvl = "!#lvl|{}".format(level)
						print(updatelvl)
						updatename = "!#iam|{}".format(name)
						print(updatename)
					if guild_length == 0:
						guild = "None"
					else:
						guild = whattoshow[namelenspot+5+name_length:namelenspot+5+name_length+guild_length].decode()
					if guild == "None":
						returnable += "Player name: '{}' of level {} has the id of {} for this session, is not in a guild, and is at coordinates {}, {}.|{}".format(name, level, player_id, x_coord, y_coord, storeinfo)
					else:
						returnable += "Player name: '{}' of level {} has the id of {} for this session, is in the guild '{}', and is at coordinates {}, {}.|{}".format(name, level, player_id, guild, x_coord, y_coord, storeinfo)
					lastindex = storeindex+1
				elif whattoshow[lastindex+4:lastindex+6] == b'\x01\x06':
					returnable += "Player {} exists.|".format(player_id)
					lastindex += 8
				else:
					lastindex += 10000
		if pqputted == True and global_settings['upload_data']:
			pq.put('done|0|0')
		if 'move' not in filters:
			returnable = ''
		return returnable
	except Exception as e:
		return "An unknown error occurred - showobj - {} - {}".format(e, returnable)

def statupd(stats):
	try:
		# \x17 
		lvl_xp = int(binascii.hexlify(stats[:8]), 16)+5
		melee_xp = int(binascii.hexlify(stats[8:12]), 16)
		archer_xp = int(binascii.hexlify(stats[12:16]), 16)
		mage_xp = int(binascii.hexlify(stats[16:20]), 16)
		def_xp = int(binascii.hexlify(stats[20:24]), 16)
		returnable = "Lvl XP: {:,d}. Melee XP: {:,d}. Archer XP: {:,d}. Mage XP: {:,d}. Defense XP: {:,d}.|".format(lvl_xp, melee_xp, archer_xp, mage_xp, def_xp)
		#Send the xp values to rucoy gui through the StdOutQueue to display on GUI.
		updatexp = "!#lxp|{}".format(lvl_xp)
		print(updatexp)
		updatemel = "!#mel|{}".format(melee_xp)
		print(updatemel)
		updatedis = "!#dis|{}".format(archer_xp)
		print(updatedis)
		updatemag = "!#mag|{}".format(mage_xp)
		print(updatemag)
		updatedef = "!#def|{}".format(def_xp)
		print(updatedef)
		if 'statupd' not in filters:
			returnable = ''
		if len(stats) > 24:
			return "{}{}".format(returnable, translator(stats[24:], "server"))
		else:
			return returnable
	except Exception as e:
		return "An unknown error occurred - statupd - {}".format(e)

def hpmpupd(stats):
	try:
		# \x18 
		hp_left = int(binascii.hexlify(stats[:2]), 16)
		hp_max = int(binascii.hexlify(stats[4:6]), 16)
		mp_left = int(binascii.hexlify(stats[8:10]), 16)
		mp_max = int(binascii.hexlify(stats[12:14]), 16)
		returnable = "HP: {}/{}, MP: {}/{}.|".format(hp_left, hp_max, mp_left, mp_max)
		if bp != 'monitor':
			bq.put('hp|{}|{}'.format(hp_left, hp_max))
			bq.put('mp|{}|{}'.format(mp_left, mp_max))
			current_hp_percent = 100*(hp_left/hp_max)
			if current_hp_percent <= 25:
				my_name = playerdict('get', global_settings['myid'])
				if my_name.find('#') >= 0:
					my_name = 'idk'
				else:
					my_name = my_name.split(' Lv')[0]
				message = "Your health has gone below 25%. Rucoy Bot will be pausing for 30 minutes."
				if my_name == 'idk':
					toastme = "Warning! {}".format(message)
				else:
					toastme = "Warning! {}, {}".format(my_name, message)
				toaster.show_toast("Rucoy Bot", toastme, icon_path="robot.ico", duration=5, threaded=True)
				if global_settings['pm_notifications']:
					pq.put('send|{}|{}|{}'.format(global_settings['pm_notify_email'], my_name, toastme))
		if 'hpmpupd' not in filters:
			returnable = ''
		if len(stats) > 24:
			return "{}{}".format(returnable, translator(stats[14:], "server"))
		else:
			return returnable
	except Exception as e:
		return "An unknown error occurred - hpmpupd - {}".format(e)

def bagupd(bag):
	try:
		# \x0b 
		global bp
		global potsgone
		global bagfull
		lastindex = 0
		returnable = ""
		slot = 1
		money = int(binascii.hexlify(bag[:8]), 16)
		#Send current gold on hand to rucoy gui through the StdOutQueue.
		updategld = "!#gld|{}".format(money)
		print(updategld)
		returnable += "You have {:,d} gold on your person.|".format(money)
		for x in range(8, 35, 2):
			itemid = int(binascii.hexlify(bag[x:x+2]), 16)
			itemid = item_names.get(itemid, "#{}".format(itemid))
			if bp != 'monitor' and x >= 26 and x < 34:
				bq.put('equip|{}|{}'.format(x, itemid))
			if itemid != '#0':
				returnable += "You have {} equiped.|".format(itemid)
		lastindex += 40
		totalslots = int(binascii.hexlify(bag[36:38]), 16)
		slotsfilled = int(binascii.hexlify(bag[38:40]), 16)
		returnable += "Bag currently has {} out of {} slots filled.|".format(slotsfilled, totalslots)
		endofbagupd = lastindex + (slotsfilled * 4)
		if bp == 'farm' and bagfull and slotsfilled != totalslots:
			bagfull = False
			bq.put('bagnotfull|0')
		if bp == 'farm' and slotsfilled == totalslots and bagfull == False:
			bagfull = True
			my_name = playerdict('get', global_settings['myid'])
			if my_name.find('#') >= 0:
				my_name = 'idk'
			else:
				my_name = my_name.split(' Lv')[0]
			message = "You have run out of space in your bag. Rucoy Bot will now only pick up Gold. Please stop the bot, empty your bag, and restart to resume farming other drops."
			bq.put('bagfull|0')
			if my_name == 'idk':
				toastme = "Warning! {}".format(message)
			else:
				toastme = "Warning! {}, {}".format(my_name, message)
			toaster.show_toast("Rucoy Bot", toastme, icon_path="robot.ico", duration=5, threaded=True)
			if global_settings['pm_notifications']:
				pq.put('send|{}|{}|{}'.format(global_settings['pm_notify_email'], my_name, toastme))
		while slot <= slotsfilled:
			itemid = int(binascii.hexlify(bag[lastindex:lastindex+2]), 16)
			itemid = item_names.get(itemid, "#{}".format(itemid))
			lastindex += 2
			itemqty = int(binascii.hexlify(bag[lastindex:lastindex+2]), 16)
			lastindex += 2
			returnable += 'Slot {}: {} of item {}.|'.format(slot, itemqty, itemid)
			if bp != 'monitor':
				if itemid.find('Potion') >= 0 and itemid.find('Halloween') == -1:
					bq.put('pot|{}|{}'.format(itemid, itemqty))
			if bp == 'skill':
				if itemid.find('Training') >= 0:
					bq.put('bag|{}|{}'.format(slot-1, itemid))
			slot += 1
		if bp != 'monitor' and potsgone == False:
			if returnable.find('Health Potion') == -1:
				bq.put('pot|hp|0')
				my_name = playerdict('get', global_settings['myid'])
				if my_name.find('#') >= 0:
					my_name = 'idk'
				else:
					my_name = my_name.split(' Lv')[0]
				message = "You have run out of health potions. Please stop Rucoy Bot and buy more potions if needed."
				potsgone = True
				if my_name == 'idk':
					toastme = "Warning! {}".format(message)
				else:
					toastme = "Warning! {}, {}".format(my_name, message)
				toaster.show_toast("Rucoy Bot", toastme, icon_path="robot.ico", duration=5, threaded=True)
				if global_settings['pm_notifications']:
					pq.put('send|{}|{}|{}'.format(global_settings['pm_notify_email'], my_name, toastme))
			if returnable.find('Mana Potion') == -1:
				bq.put('pot|mp|0')
				my_name = playerdict('get', global_settings['myid'])
				if my_name.find('#') >= 0:
					my_name = 'idk'
				else:
					my_name = my_name.split(' Lv')[0]
				message = "You have run out of mana potions. Please stop Rucoy Bot and buy more potions if needed."
				potsgone = True
				if my_name == 'idk':
					toastme = "Warning! {}".format(message)
				else:
					toastme = "Warning! {}, {}".format(my_name, message)
				toaster.show_toast("Rucoy Bot", toastme, icon_path="robot.ico", duration=5, threaded=True)
				if global_settings['pm_notifications']:
					pq.put('send|{}|{}|{}'.format(global_settings['pm_notify_email'], my_name, toastme))
		if 'bagupd' not in filters:
			returnable = ''
		if endofbagupd < len(bag):
			return "{}{}".format(returnable, translator(bag[endofbagupd:], "server"))
		return returnable
	except Exception as e:
		return "An unknown error occurred - bagupd - {}".format(e)

def hashtag(nextcmd):
	try:
		# \x23 
		if nextcmd[1:] != b'':
			return translator(nextcmd[1:], "server")
		else:
			return ''
	except Exception as e:
		return "An unknown error occurred - hashtag - {}".format(e)

def playerdict(mode, who):
	try:
		global player_names
		if mode == "get":
			return player_names.get(who, '#{}'.format(who))
		elif mode == "del":
			player_names.pop(int(who), None)
			return
		else:
			player_names[int(who)] = mode
			return
	except:
		return who

def monsterdict(mode, who):
	try:
		global monster_names
		if mode == "get":
			return monster_names.get(who, '{}'.format(who))
		elif mode == "del":
			monster_names.pop(who, None)
		else:
			monster_names[who] = mode
			return
	except:
		return who

#------------------Client side down below------------------#

#Invites a player to a team based on player id.
def invitetoteam(who):
	try:
		if 'client' not in filters:
			return ''
		target_id = int(binascii.hexlify(who[:4]), 16)
		player_id = playerdict("get", target_id)
		return "Invite Player {} to a team. ".format(player_id)
	except Exception as e:
		return "An unknown error occurred - invitetoteam - {}".format(e)

#Expels a player using player id.
def expelfromteam(who):
	try:
		if 'client' not in filters:
			return ''
		target_id = int(binascii.hexlify(who[:4]), 16)
		player_id = playerdict("get", target_id)
		return "Expel Player ID#: {} from the team. ".format(player_id)
	except Exception as e:
		return "An unknown error occurred - expelfromteam - {}".format(e)

#Sets up a shop as long as on a shop spot. (\x15 server command toggles this)
def setupshop(howlong):
	try:
		if 'client' not in filters:
			return ''
		hours = int(binascii.hexlify(howlong), 16)
		if hours < 24:
			return "Set up shop for {} hours. ".format(hours)
		else:
			days = hours // 24
			rest_of_hours = hours % 24
			if rest_of_hours != 0:
				return "Set up shop for {} days and {} hours. ".format(days, rest_of_hours)
			else:
				return "Set up shop for {} days. ".format(days, rest_of_hours)
	except Exception as e:
		return "An unknown error occurred - setupshop - {}".format(e)

#Gift diamonds to a player.
def giftdimas(whoandqty):
	try:
		if 'client' not in filters:
			return ''
		#\x00\x07\x22\x00\x01\xa1\x90\x00\x02
		playerid = int(binascii.hexlify(whoandqty[:4]), 16)
		quantity = int(binascii.hexlify(whoandqty[4:]), 16)
		return "Gift {} diamonds to player {}".format(quantity, playerid)
	except Exception as e:
		return "An unknown error occurred - giftdimas - {}".format(e)

#Buys an item from a shop or merchant. Slot, item id, and price must all match or server remains quiet.
def buyfromshop(restofpur):
	try:
		if 'client' not in filters:
			return ''
		#\x00\x01\x91\xfe	\x00\x00\x00\x0f	\x00\x01\	x00\x00\x27\x10
		playerid = int(binascii.hexlify(restofpur[:4]), 16)
		player_id = playerdict("get", player_id)
		slot = int(binascii.hexlify(restofpur[4:6]), 16)+1
		itemid = int(binascii.hexlify(restofpur[6:8]), 16)
		itemname = item_names.get(itemid, "#{}".format(itemid))
		quantity = int(binascii.hexlify(restofpur[8:10]), 16)
		price = int(binascii.hexlify(restofpur[10:]), 16)
		return "Buy {} item(s) of item {} for {:,d} gold from player {}'s shop, slot number {}".format(quantity, itemname, price, playerid, slot)
	except Exception as e:
		return "An unknown error occurred - buyfromshop - {}".format(e)

#sent every few seconds to keep the connection alive
def alive():
	if 'client' not in filters:
		return ''
	return "I'm alive"

#sent when hp falls <= 0
def dead():
	if 'client' not in filters:
		return ''
	
	my_name = playerdict('get', global_settings['myid'])
	if my_name.find('#') >= 0:
		my_name = 'idk'
	else:
		my_name = my_name.split(' Lv')[0]
	
	deadmsg = "!#die|0"
	print(deadmsg)
	
	if bp != 'monitor':
		bq.put('dead|0')
		if my_name == 'idk':
			toastme = "I'm sorry, you have died."
		else:
			toastme = "I'm sorry, {}. You have died".format(my_name)
		toaster.show_toast("Rucoy Bot", toastme, icon_path="robot.ico", duration=5, threaded=True)
		if global_settings['pm_notifications']:
			pq.put('send|{}|{}|{}'.format(global_settings['pm_notify_email'], my_name, toastme))
	return "You have died."

#picks up any objects located right next to player (not diagonally) 
def pickup():
	if 'client' not in filters:
		return ''
	return "Pickup"

#converts the last 4 bytes into an ID that identifies the monster on the map
def attack(restofatk):
	try:
		if 'client' not in filters:
			return ''
		target_id = int(binascii.hexlify(restofatk[:4]), 16)
		bq.put("atkplz|{}".format(target_id))
		if target_id < 99999:
			monster_id = monsterdict("get", target_id)
			return "Attack monster {}".format(monster_id)
		else:
			player_id = playerdict("get", target_id)
			return "Attack player {}".format(player_id)
	except Exception as e:
		return "An unknown error occurred - attack - {}".format(e)

#Sent when weapons are changed
def weapon(restofwpn):
	if 'client' not in filters:
		return ''
	weapon = {
		b'\x00': "Switch to Warrior",
		b'\x01': "Switch to Archer",
		b'\x02': "Switch to Mage"
	}
	return weapon.get(restofwpn)

#Identifies the coordinates of the requested position. Server checks validity of all coordinates.
def moveto(location):
	try:
		if 'client' not in filters:
			return ''
		x = int(binascii.hexlify(location[:2]), 16)
		y = int(binascii.hexlify(location[2:]), 16)
		bq.put("moveplz|{},{},0".format(x, y))
		return "Move to {}, {}".format(x, y)
	except Exception as e:
		return "An unknown error occurred - moveto - {}".format(e)

#Sent after death and the respawn button is pressed. Location is automatically set to NE building of hometown.
def revive():
	if 'client' not in filters:
		return ''
	return "Revive!"

#Use an item whether it be a potion, scroll, or candy. Server validates time interval.
def useitem(whichitem):
	try:
		if 'client' not in filters:
			return ''
		itemid = int(binascii.hexlify(whichitem[:2]), 16)
		itemname = item_names.get(itemid, "#{}".format(itemid))
		destination = int(binascii.hexlify(whichitem[2:3]), 16)
		destinations = {
			1: "Goblins",
			2: "Mummies",
			3: "Assassins",
			4: "Zombies",
			5: "Skeletons",
			6: "Drows",
			7: "Lizards",
			8: "Gargoyles",
			9: "Dragons",
			10: "Minotaurs",
			11: "Ice Dragons",
			12: "Arena"
		}
		if itemname == "Destination Scroll":
			return "Teleport using item {} to go to {}. ".format(itemname, destinations.get(destination, destination))
		elif itemname.find("Scroll") > -1:
			return "Teleport using item {}. ".format(itemname)
		elif itemname.find("Candy") > -1:
			return "Eat a {}. ".format(itemname)
		else:
			return "Drink {}. ".format(itemname)
	except Exception as e:
		return "An unknown error occurred - useitem - {}".format(e)

#Use special move for each class, server validates time interval.
def special(restofspl):
	if 'client' not in filters:
		return ''
	if restofspl ==  b'\x00\x00\x00\x00':
			return "Special Attack (Warrior or Archer)"
	else:
		try:
			return "Special Mage Attack at {}, {}".format(int(restofspl[:2].hex(), 16), int(restofspl[2:].hex(), 16))
		except:
			return "Special Mage Attack"

#Equip something from player inventory to the relevant slot, ie. Equiping a helmet moves the item
#in inventory to the helmet slot, pops the item from the inventory, and moves the previous equiped
#item to the last slot in inventory.
def equip(restofeqp):
	try:
		if 'client' not in filters:
			return ''
		return "Equip item stored in slot: {}".format(int(binascii.hexlify(restofeqp), 16)+1)
	except Exception as e:
		return "An unknown error occurred - equip - {}".format(e)

#Unequip the item in the slot defined belowed in the slots dictionary.
def unequip(restofuqp):
	if 'client' not in filters:
		return ''
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
		return "Unequip item stored in: {}".format(slots.get(int(binascii.hexlify(restofuqp), 16), int(binascii.hexlify(restofuqp), 16)))
	except Exception as e:
		return "An unknown error occurred - unequip - {}".format(e)

def merchant(restofmer):
	if 'client' not in filters:
		return ''
	specialty = {
		b'\x00\x00\x122': "Speak with Gear Merchant",
		b'\x00\x00\x121': "Speak with Supplies Merchant",
		b'\x00\x00\x123': "Speak with Vault Merchant",
		b'\x00\x00\x124': "Speak with Lvl 150 Supplies Merchant",
		b'\x00\x00\x125': "Speak with Lvl 150 Gear Merchant",
		b'\x00\x00\x12\x36': "Speak with Lvl 150 Vault Merchant",
		b'\x00\x00\x12\x39': "Open Door with Assassin's Key (if obtained)",
		b'\x00\x00\x13\x92': "Open Door with Vampire's Key (if obtained)"
	}
	try:
		return "{}".format(specialty.get(restofmer, "Follow Player ID: {}".format(int(binascii.hexlify(restofmer), 16))))
	except Exception as e:
		return "An unknown error occurred - merchant - {}".format(e)

def drop(restofitm):
	try:
		if 'client' not in filters:
			return ''
		# slot		itemid		quantity	slotsfull
		# \x00\x1e	\x00\x63	\x00\x01	\x00\x21
		slot = int(binascii.hexlify(restofitm[:2]), 16)+1
		itemid = int(binascii.hexlify(restofitm[2:4]), 16)
		quantity = int(binascii.hexlify(restofitm[4:6]), 16)
		slotsfull = int(binascii.hexlify(restofitm[6:]), 16)-1
		# quantity, itemid, slot, slotsfull
		return "Drop {} item(s) with ID # {} from slot {}. {} slot(s) filled. ".format(quantity, itemid, slot, slotsfull)
	except Exception as e:
		return "An unknown error occurred - drop - {}".format(e)

def sell(restofsll):
	try:
		if 'client' not in filters:
			return ''
		# ?????		?????		slot		itemid		quantity	slotsfull
		# \x00\x00	\x10\x36	\x00\x29	\x00\x19	\x00\x01	\x00\x2a
		sell_slot = int(binascii.hexlify(restofsll[4:6]), 16)+1
		sell_itemid = int(binascii.hexlify(restofsll[6:8]), 16)
		sell_quantity = int(binascii.hexlify(restofsll[8:10]), 16)
		sell_slotsfull = int(binascii.hexlify(restofsll[10:]), 16)-1
		return "Sell {} item(s) with ID # {} from slot {}. {} slot(s) filled. ".format(sell_quantity, sell_itemid, sell_slot, sell_slotsfull)
	except Exception as e:
		return "An unknown error occurred - sell - {}".format(e)


def buy(restofbuy):
	try:
		if 'client' not in filters:
			return ''
		#					merchant	merchslot	itemid		itmryou		ignore		itemgrp?	grpryou
		#Client >>>  \x00\x00\x10\x36	\x00\x1d	\x00\x39	\x00\x01	\x00\x00	\x01\xae	\x00\x01
		buy_specialty = {
			b'\x00\x00\x106': "Gear Merchant",
			b'\x00\x00\x105': "Supplies Merchant",
			b'\x00\x00\x107': "Vault Merchant",
			b'\x00\x00\x108': "Lvl 150 Supplies Merchant",
			b'\x00\x00\x109': "Lvl 150 Gear Merchant",
			b'\x00\x00\x10:': "Lvl 150 Vault Merchant"
		}
		merchant_name = buy_specialty.get(restofbuy[:4], "Merchant ID : {}".format(int(binascii.hexlify(restofbuy[:4]), 16)))
		merchslot = int(binascii.hexlify(restofbuy[4:6]), 16)+1
		buy_itemid = int(binascii.hexlify(restofbuy[6:8]), 16)
		buy_item_quantity = int(binascii.hexlify(restofbuy[8:10]), 16)
		buy_groupid = int(binascii.hexlify(restofbuy[12:14]), 16)
		buy_group_quantity = int(binascii.hexlify(restofbuy[14:]), 16)
		return "Buy {} item(s) with ID # {}, group ID # {} from {}'s slot # {}".format(buy_item_quantity*buy_group_quantity, buy_itemid, buy_groupid, merchant_name, merchslot)
	except Exception as e:
		return "An unknown error occurred - buy - {}".format(e)

def selltoworld(restofwld):
	try:
		if 'client' not in filters:
			return ''
					#itemid?	slot		price		price		quantity
		#Client >>>  \x00\x19	\x00\x0b	\x00\x00	\x00\x04	\x00\x01
		world_itemid = int(binascii.hexlify(restofwld[:2]), 16)
		world_slot = int(binascii.hexlify(restofwld[2:4]), 16)+1
		world_price = int(binascii.hexlify(restofwld[4:8]), 16)
		world_quantity = int(binascii.hexlify(restofwld[8:]), 16)
		return "Sell {} item(s) with id # {} from slot # {} for {:,d} gold to the world".format(world_quantity, world_itemid, world_slot, world_price)
	except Exception as e:
		return "An unknown error occurred - selltoworld - {}".format(e)

def stopsaleof(slotnumber):
	try:
		if 'client' not in filters:
			return ''
		return "Stop selling item in slot # {}".format(int(binascii.hexlify(slotnumber), 16)+1)
	except Exception as e:
		return "An unknown error occurred - stopsaleof - {}".format(e)

def sendmsg(restofmsg):
	try:
		if 'client' not in filters:
			return ''
		recipient = {
			b'\x00': "Local",
			b'\x01': "Server",
			b'\x02': "Team",
			b'\x04': "Guild"
		}
		if restofmsg[:1] == b'\x03':
			name_length = int(binascii.hexlify(restofmsg[1:2]), 16)
			target = restofmsg[2:name_length+2].decode()
			msg_length = int(binascii.hexlify(restofmsg[name_length+2:name_length+3]), 16)
			message = restofmsg[name_length+3:].decode()
		else:
			target = recipient.get(restofmsg[:1])
			msg_length = int(binascii.hexlify(restofmsg[1:2]), 16)
			message = restofmsg[2:].decode()
		
		return "Send message '{}' | {} characters long to {}".format(message, msg_length, target)
	except Exception as e:
		return "An unknown error occurred - sendmsg - {}".format(e)


def withdraw(restofwtd):
	try:
		if 'client' not in filters:
			return ''
		return "Withdraw {:,d} gold".format(int(binascii.hexlify(restofwtd), 16))
	except Exception as e:
		return "An unknown error occurred - withdraw - {}".format(e)

def deposit(restofdpt):
	try:
		if 'client' not in filters:
			return ''
		return "Deposit {:,d} gold".format(int(binascii.hexlify(restofdpt), 16)) 
	except Exception as e:
		return "An unknown error occurred - deposit - {}".format(e)

def getfromvault(restofget):
	try:
		if 'client' not in filters:
			return ''
		#			 get			slot		itemid		quantity	slotsfull
		#Client >>>  \x00\x09\x24	\x00\x00	\x00\x85	\x00\x01	\x00\xa9
		get_slot = int(binascii.hexlify(restofget[:2]), 16)+1
		get_itemid = int(binascii.hexlify(restofget[2:4]), 16)
		get_quantity = int(binascii.hexlify(restofget[4:6]), 16)
		get_slotsfull = int(binascii.hexlify(restofget[6:]), 16)-1
		return "Get {} item(s) with id # {} from slot # {}. {} slots filled. ".format(get_quantity, get_itemid, get_slot, get_slotsfull)
	except Exception as e:
		return "An unknown error occurred - getfromvault - {}".format(e)

def addtovault(restofadd):
	try:
		if 'client' not in filters:
			return ''
		add_slot = int(binascii.hexlify(restofadd[:2]), 16)+1
		add_itemid = int(binascii.hexlify(restofadd[2:4]), 16)
		add_quantity = int(binascii.hexlify(restofadd[4:6]), 16)
		add_slotsfull = int(binascii.hexlify(restofadd[6:]), 16)-1
		return "Store {} item(s) with id # {} from slot # {}. {} slots filled. ".format(add_quantity, add_itemid, add_slot, add_slotsfull)
	except Exception as e:
		return "An unknown error occurred - addtovault - {}".format(e)

def byebye():
	if 'client' not in filters:
		return ''
	return "Bye Bye!"
	

def pvpmode(restofpvp):
	try:
		if 'client' not in filters:
			return ''
		modes = {
			b'\x00': "Never attack anyone",
			b'\x01': "Only attack cursed players",
			b'\x02': "Attack anyone who gets in the way"
		}
		return "Set PVP Mode to: {}".format(modes.get(restofpvp))
	except Exception as e:
		return "An unknown error occurred - pvpmode - {}".format(e)


def t(testpkt):
	print(prettyreturn(translator(testpkt, 's')))