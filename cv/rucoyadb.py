import subprocess as sp
from time import sleep
from multiprocessing import Process, Queue, freeze_support


CREATE_NO_WINDOW = 0x08000000


class AdbLib():
	def __init__(self, serial='', ratio=1, mode='normal'):
		if serial == '':
			self.s = ''
		else:
			self.s = f'-s {serial}'
		if ratio == 1:
			self.r = 1
		else:
			self.r = ratio
		self.mode = mode
		if self.mode == 'fast':
			self.callq = Queue()
			self.p = Process(target=self.call_loop, args=(self.callq,))
			self.p.daemon = True
			self.p.start()

	def setserial(self, serial):
		if serial == '':
			self.s = ''
		else:
			self.s = f'-s {serial}'
	
	def setratio(self, ratio):
		self.r = ratio

	def taphppot(self):
		res = self.call(f'adb.exe {self.s} shell input tap {100*self.r} {700*self.r}')
		return res

	def tapmppot(self):
		res = self.call(f'adb.exe {self.s} shell input tap {100*self.r} {500*self.r}')
		return res

	def tapspecial(self):
		res = self.call(f'adb.exe {self.s} shell input tap {100*self.r} {400*self.r}')
		return res

	def tapmelee(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {500*self.r}')
		return res

	def tapdist(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {600*self.r}')
		return res

	def tapmage(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {700*self.r}')
		return res

	def switchmeleeweapon(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {500*self.r}')
		res2 = self.call(f'adb.exe {self.s} shell input tap {1150*self.r} {500*self.r}')
		return res+res2

	def switchdistweapon(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {600*self.r}')
		res2 = self.call(f'adb.exe {self.s} shell input tap {1150*self.r} {600*self.r}')
		return res+res2

	def switchmageweapon(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {700*self.r}')
		res2 = self.call(f'adb.exe {self.s} shell input tap {1150*self.r} {700*self.r}')
		return res+res2

	def tapself(self):
		res = self.call(f'adb.exe {self.s} shell input tap {610*self.r} {350*self.r}')
		return res

	def tapat(self, x, y):
		x = str(x)
		y = str(y)
		x_taps = {
			'0': f'{610*self.r}',
			'1': f'{700*self.r}',
			'-1': f'{550*self.r}',
			'2': f'{770*self.r}',
			'-2': f'{480*self.r}',
			'3': f'{850*self.r}',
			'-3': f'{400*self.r}',
			'4': f'{920*self.r}',
			'-4': f'{310*self.r}',
			'5': f'{1000*self.r}',
			'-5': f'{250*self.r}',
			'6': f'{1100*self.r}',
			'-6': f'{190*self.r}'
		}
		y_taps = {
			'0': f'{350*self.r}',
			'1': f'{290*self.r}',
			'-1': f'{410*self.r}',
			'2': f'{200*self.r}',
			'-2': f'{500*self.r}',
			'3': f'{110*self.r}',
			'-3': f'{590*self.r}',
			'4': f'{50*self.r}',
			'-4': f'{650*self.r}'
		}
		if int(x) > 6:
			x = '6'
		if int(x) < -6:
			x = '-6'
		if int(y) > 4:
			y = '4'
		if int(y) < -4:
			y = '-4'
		if int(y) == 4 and int(x) >= 4:
			y = '3'
		if x == '0' and y == '0':
			x = '1'
		command = 'adb.exe {} shell input tap {} {}'.format(self.s, x_taps.get(x), y_taps.get(y))
		res = self.call(command)
		return res

	def tappickup(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {200*self.r}')
		return res

	def tapsettings(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {50*self.r}')
		return res

	def tapclose(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {50*self.r}')
		return res

	def tapsettings_servers(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1000*self.r} {50*self.r}')
		return res

	def tapmap(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1000*self.r} {50*self.r}')
		return res

	def tapsettings_servers_select(self, server):
		server_taps = {
			'NA': f'{300*self.r} {250*self.r}',
			'SA': f'{300*self.r} {300*self.r}',
			'EU': f'{300*self.r} {400*self.r}',
			'AS': f'{300*self.r} {500*self.r}',
			1: f'{610*self.r} {250*self.r}',
			2: f'{610*self.r} {300*self.r}',
			3: f'{610*self.r} {400*self.r}',
			4: f'{610*self.r} {500*self.r}',
			5: f'{1000*self.r} {250*self.r}',
			6: f'{1000*self.r} {300*self.r}'
		}
		tap_cmd = 'adb.exe {} shell input tap {}'.format(self.s, server_taps.get(server))
		res = self.call(tap_cmd)
		return res

	def tapsettings_stats(self):
		res = self.call(f'adb.exe {self.s} shell input tap {200*self.r} {100*self.r}')
		return res

	def tapsettings_inventory(self):
		res = self.call(f'adb.exe {self.s} shell input tap {400*self.r} {100*self.r}')
		return res

	def tapsettings_inventory_select(self, slot):
		slot_taps = {
			0: f'{500*self.r} {250*self.r}',
			1: f'{550*self.r} {250*self.r}',
			2: f'{650*self.r} {250*self.r}',
			3: f'{750*self.r} {250*self.r}',
			4: f'{850*self.r} {250*self.r}',
			5: f'{950*self.r} {250*self.r}',
			6: f'{1050*self.r} {250*self.r}',
			7: f'{1150*self.r} {250*self.r}',
			8: f'{500*self.r} {300*self.r}',
			9: f'{550*self.r} {300*self.r}',
			10: f'{650*self.r} {300*self.r}',
			11: f'{750*self.r} {300*self.r}',
			12: f'{850*self.r} {300*self.r}',
			13: f'{950*self.r} {300*self.r}',
			14: f'{1050*self.r} {300*self.r}',
			15: f'{1150*self.r} {300*self.r}',
			16: f'{500*self.r} {400*self.r}',
			17: f'{550*self.r} {400*self.r}',
			18: f'{650*self.r} {400*self.r}',
			19: f'{750*self.r} {400*self.r}',
			20: f'{850*self.r} {400*self.r}',
			21: f'{950*self.r} {400*self.r}',
			22: f'{1050*self.r} {400*self.r}',
			23: f'{1150*self.r} {400*self.r}',
			24: f'{500*self.r} {500*self.r}',
			25: f'{550*self.r} {500*self.r}',
			26: f'{650*self.r} {500*self.r}',
			27: f'{750*self.r} {500*self.r}',
			28: f'{850*self.r} {500*self.r}',
			29: f'{950*self.r} {500*self.r}',
			30: f'{1050*self.r} {500*self.r}',
			31: f'{1150*self.r} {500*self.r}'
			
		}
		res2 = 0
		res3 = 0
		if slot > 31 and slot < 64:
			res2 = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {400*self.r}')
			slot -= 32
		if slot > 63:
			res2 = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {400*self.r}')
			res3 = self.call(f'adb.exe {self.s} shell input tap {1200*self.r} {400*self.r}')
			slot -= 64
		tap_cmd = 'adb.exe {} shell input tap {}'.format(self.s, slot_taps.get(slot))
		res = self.call(tap_cmd)
		return res+res2+res3

	def tapsettings_inventory_green(self):
		res = self.call(f'adb.exe {self.s} shell input tap {550*self.r} {500*self.r}')
		return res

	def tapsettings_inventory_select_exit(self):
		res = self.call(f'adb.exe {self.s} shell input tap {700*self.r} {650*self.r}')
		return res

	def tapsettings_inventory_drop(self):
		res = self.call(f'adb.exe {self.s} shell input tap {800*self.r} {500*self.r}')
		res2 = self.call(f'adb.exe {self.s} shell input tap {480*self.r} {520*self.r}')
		return res+res2

	def tapmessages(self):
		res = self.call(f'adb.exe {self.s} shell input tap {1100*self.r} {50*self.r}')
		return res

	def tapmessages_local(self):
		res = self.call(f'adb.exe {self.s} shell input tap {200*self.r} {50*self.r}')
		return res

	def tapmessages_server(self):
		res = self.call(f'adb.exe {self.s} shell input tap {350*self.r} {50*self.r}')
		return res

	def tapmessages_direct(self):
		# These messages_direct functions are predicated on a user not being in a guild or team
		res = self.call(f'adb.exe {self.s} shell input tap {600*self.r} {50*self.r}')
		return res

	def tapmessages_direct_close(self):
		res = self.call(f'adb.exe {self.s} shell input tap {800*self.r} {30*self.r}')
		return res

	def sendmessage(self, msg):
		message = msg.replace(' ', '%s')
		sendme = 'adb.exe {} shell input text "{}"'.format(self.s, message)
		res = self.call(sendme)
		res2 = self.call(f'adb.exe {self.s} shell input tap {1100*self.r} {650*self.r}')
		return res+res2

	def pullscreenshot(self, filename='screen.png'):
		res = self.call(f'adb.exe {self.s} shell screencap -p /sdcard/Pictures/{filename}')
		res2 = self.call(f'adb.exe {self.s} pull /sdcard/Pictures/{filename}')
		res3 = self.call(f'adb.exe {self.s} rm /sdcard/Pictures/{filename}')
		return res+res2+res3

	def pullbackup(self):
		res = self.popen(f'adb.exe {self.s} pull /data/data/com.mmo.android/shared_prefs/savefile.xml')
		return res

	def pushbackup(self):
		res = self.popen(f'adb.exe {self.s} push savefile.xml /data/data/com.mmo.android/shared_prefs/savefile.xml')
		return res

	def restartrucoy(self, wait=0):
		res = self.call(f'adb.exe {self.s} shell am force-stop com.mmo.android')
		sleep(wait)
		res2 = self.call(f'adb.exe {self.s} shell monkey -p com.mmo.android 1')
		return res+res2

	def closerucoy(self):
		res = self.call(f'adb.exe {self.s} shell am force-stop com.mmo.android')
		return res

	def devicelist(self):
		try:
			res = self.popen('adb.exe devices')
			res_list = res.split('\r\n')
			if len(res_list) == 3:
				return ['']
			else:
				res_list.pop(0)
				res_list.pop(-1)
				res_list.pop(-1)
				formatted_list = []
				for device in res_list:
					formatted_list.append(device.split('\t')[0])
				return formatted_list
			return res
		except:
			return ['']
	
	def connect(self, address):
		if address.count(':') == 0:
			res = self.popen('adb.exe connect 127.0.0.1:{}'.format(address))
		else:
			res = self.popen('adb.exe connect {}'.format(address))
		return res	

	def popen(self, cmd: str) -> str:
		"""For pyinstaller -w, gotten from https://stackoverflow.com/a/59012092/4044291"""
		startupinfo = sp.STARTUPINFO()
		startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
		process = sp.Popen(cmd,startupinfo=startupinfo, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE)
		return process.stdout.read().decode('utf8')

	def call(self, cmd: str) -> str:
		if self.mode == 'normal':
			res = sp.call(cmd, creationflags=CREATE_NO_WINDOW)
			return res
		else:
			self.callq.put(cmd)
			return 0
	
	def call_loop(self, callq):
		while True:
			callcmd = callq.get()
			if callcmd == 'quit':
				break
			_ = sp.call(callcmd, creationflags=CREATE_NO_WINDOW)
	
	def quit_loop(self):
		self.callq.put('quit')











