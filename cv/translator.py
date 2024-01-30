from formatters import *

def translator(argument, origin):
	try:
		if origin == "client":
			header = argument[:4]
			if header == '0505':
				return alive()
			elif header == '0100':
				return dead()
			elif header == '011a':
				return pickup()
			elif header == '0503': 
				return attack(argument[4:])
			elif header == '0206':
				return weapon(argument[4:])
			elif header == '0501':
				return moveto(argument[4:])
			elif header == '070d':
				return special(argument[4:])
			elif header == '0104': 
				return revive()
			elif header == '0444':
				return useitem(argument[4:])
			elif header == '0318': 
				return equip(argument[4:])
			elif header == '0003': 
				return unequip(argument[4:])
			elif header == '050b':
				return merchant(argument[4:])
			elif argument[2:4] == '0a':
				return sendmsg(argument[4:])
			else: 
				return argument
			"""
			
			elif header == b'\x00\t\x19': 
				return drop(argument[4:])
			elif header == b'\x00\x0d\x1b': 
				return sell(argument[4:])
			elif header == b'\x00\x11\x0c':
				return buy(argument[4:])
			elif header == b'\x00\x0b\x1c': 
				return selltoworld(argument[4:])
			elif header == b'\x00\x03\x1d': 
				return stopsaleof(argument[4:])
			elif header == b'\x00\x05\x27': 
				return withdraw(argument[4:])
			elif header == b'\x00\x05\x26': 
				return deposit(argument[4:])
			elif header == b'\x00\x09\x24': 
				return getfromvault(argument[4:])
			elif header == b'\x00\x09\x23':
				return addtovault(argument[4:])
			elif header == b'\x00\x01\x02': 
				return byebye()
			elif header == b'\x00\x02\x16': 
				return pvpmode(argument[4:])
			elif header == b'\x00\x0f\x0c': 
				return buyfromshop(argument[4:])
			elif header == b'\x00\x07\x22': 
				return giftdimas(argument[4:])
			elif header == b'\x00\x02\x30': 
				return setupshop(argument[4:])
			elif header == b'\x00\x05\x10': 
				return invitetoteam(argument[4:])
			elif header == b'\x00\x05\x14': 
				return expelfromteam(argument[4:])
			
			elif argument == b'':
				return '' 
			"""
		else:
			header = argument[2:4]
			if header == '02':
				return servmsg(argument[2:])
			elif header == '08': 
				return gotcha(argument[2:])
			elif header == '1e':
				return takeatk(argument[4:])
			elif header == '3f':
				return showobj(argument[2:])
			""" 
			if header == b'\x0c': 
				return recmsg(argument[2:])
			
			elif header == b'\x07': 
				return endconvo()
			
			
			elif header == b'\x18':
				return hpmpupd(argument[3:])
			elif header == b'\x17':
				return statupd(argument[2:])
			elif header == b'\x00':
				return showobj(argument[2:])
			elif header == b'\x0b':
				return bagupd(argument[2:])
			elif header == b'\x01':
				return forget(argument[2:])
			elif header == b'\x03':
				return shownums(argument[2:])
			elif header == b'\x15':
				return showstore(argument[3:])
			elif header == b'\x23':
				return hashtag(argument[2:])
			elif header == b'\x1e':
				return cantsee(argument[2:])
			elif header == b'\x1c':
				return mystery_one(argument[2:])
			elif header == b'\x1b':
				return youhave(argument[2:])
			elif header == b'\x2f':
				return redmsg(argument[2:])
			elif header == b'\x04':
				return levelup(argument[2:])
			elif header == b'\x1a':
				return mystery_three(argument[2:])
			elif header == b'\x20':
				return mystery_four(argument[2:])
			elif header == b'\x22':
				return youare(argument[2:])
			elif header == b'\x1f':
				return mystery_two(argument[2:])
			elif header == b'\x0d':
				return mystery_five(argument[2:])
			elif header == b'\x2d':
				#temporarily using mystery_five cuz arguments are only 4 bytes too
				return mystery_five(argument[2:])
			elif header == b'\x24':
				return friendlist(argument[2:])
			elif header == b'\x25':
				return mystery_six(argument[2:])
			elif header == b'\x27':
				return mystery_six(argument[2:])
			elif argument == b'':
				return '' """
			#else:
			return str(argument)
	except Exception as e:
		return f"An unknown error occurred - translator - {e}"