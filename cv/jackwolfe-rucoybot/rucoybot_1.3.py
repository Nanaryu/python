import tkinter as tk
from PIL import ImageTk, Image
from tkinter.font import Font
from time import sleep, time, ctime
from urllib.request import urlopen
import os
import re
import sys
import ctypes
import json
import webbrowser
import lxml.etree
from multiprocessing import Process, Queue, freeze_support
import multiprocessing as mp
import multiprocessing.queues as mpq
from threading import Thread, currentThread
from rucoynethelp import helper
from random import random
from functools import partial
import rucoyadb
import mitm
import rucoybot as bot
adb = rucoyadb.AdbLib()

def server_switch_adb_mod(switchvar, serial):
	t = currentThread()
	failed_count = 0
	while getattr(t, "do_run", True):
		try:
			sleep(1)
			adb.setserial(serial)
			success_read = adb.pullbackup()
			if 'pulled' not in success_read:
				failed_count += 1
				pass
			elif 'killing' in success_read:
				failed_count = 100
				pass
			savefile = lxml.etree.parse('savefile.xml')
			for el in savefile.xpath("//int[@name='serverChangeCount']"):
				el.attrib['value'] = "1"
			for el in savefile.xpath("//long[@name='lastServerChange']"):
				timeval = int(time()*1000)-100000
				el.attrib['value'] = str(timeval)
			open('savefile.xml', 'w').write(lxml.etree.tostring(savefile).decode())
			success_read = adb.pushbackup()
			if 'pushed' not in success_read:
				failed_count += 1
				pass
			elif 'killing' in success_read:
				failed_count = 100
				pass
		except Exception as e:
			print(e)
			failed_count += 1
		if failed_count > 4:
			if failed_count == 100:
				adb.call("taskkill /F /IM adb.exe")
				adb.call('copy /Y adb.exe "C:\Program Files (x86)\Microvirt\MEmu\adb.exe"')
				adb.call('copy /Y AdbWinApi.dll "C:\Program Files (x86)\Microvirt\MEmu\AdbWinApi.dll"')
				adb.call('copy /Y AdbWinUsbApi.dll "C:\Program Files (x86)\Microvirt\MEmu\AdbWinUsbApi.dll"')
				sys.stderr.write("Please restart MEmu as I've attempted to fix MEmu's outdated adb.exe. If you're not using MEmu, please try using MEmu to utilize this function.\n")
			else:
				sys.stderr.write("Failed to connect to emulator. Please check it's running and is a rooted emulator like MEmu.\n")
			switchvar.set(0)
			break

def get_jsonparsed_data(url):
	"""
	Receive the content of ``url``, parse it as JSON and return the object.

	Parameters
	----------
	url : str

	Returns
	-------
	dict
	"""
	response = urlopen(url, timeout=5)
	data = response.read().decode("utf-8")
	return json.loads(data)

def highlight_update(text_widget, start="1.0"):
	text_widget.highlight_pattern("^....Starting.*$", "purple", regexp=True, start=start)
	text_widget.highlight_pattern("^Server.*$", "blue", regexp=True, start=start)
	text_widget.highlight_pattern("^s     .*$", "blue", regexp=True, start=start)
	text_widget.highlight_pattern("^Client.*$", "red", regexp=True, start=start)
	text_widget.highlight_pattern("^Raw.*$", "purple", regexp=True, start=start)
	text_widget.highlight_pattern("^Bot.*$", "yellow", regexp=True, start=start)
	text_widget.highlight_pattern("^b     .*$", "yellow", regexp=True, start=start)
	text_widget.highlight_pattern("^Please restart.*$", "red", regexp=True, start=start)
	text_widget.update()


class StdoutQueue(mpq.Queue):
	def __init__(self,*args,**kwargs):
		# This is a Queue that behaves like stdout
		ctx = mp.get_context()
		super(StdoutQueue, self).__init__(*args, **kwargs, ctx=ctx)

	def write(self,msg):
		self.put(msg)

	def flush(self):
		sys.__stdout__.flush()


def callback(event):
	webbrowser.open_new(event.widget.cget("text"))

class CustomText(tk.Text):
	'''A text widget with a new method, highlight_pattern()

	example:

	text = CustomText()
	text.tag_configure("red", foreground="#ff0000")
	text.highlight_pattern("this should be red", "red")

	The highlight_pattern method is a simplified python
	version of the tcl code at http://wiki.tcl.tk/3246
	'''
	def __init__(self, *args, **kwargs):
		tk.Text.__init__(self, *args, **kwargs)

	def highlight_pattern(self, pattern, tag, regexp=False, start="1.0", end="end"):
		'''Apply the given tag to all text that matches the given pattern

		If 'regexp' is set to True, pattern will be treated as a regular
		expression according to Tcl's regular expression syntax.
		'''

		
		end = self.index(end)
		self.mark_set("matchStart", start)
		self.mark_set("matchEnd", start)
		self.mark_set("searchLimit", end)

		count = tk.IntVar()
		while True:
			index = self.search(pattern, "matchEnd","searchLimit",
								count=count, regexp=regexp)
			if index == "": break
			if count.get() == 0: break # degenerate pattern which matches zero-length strings
			self.mark_set("matchStart", index)
			self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
			self.tag_add(tag, "matchStart", "matchEnd")

class RucoyGui(tk.Tk):
	def __init__(self):
		tk.Tk.__init__(self)
		self.withdraw()
		
		self.bot_start_time = 0
		self.bot_stop_time = 0
		
		#Insert in Rucoy Bot Picture and place it onto the grid.
		img = ImageTk.PhotoImage(Image.open("rucoybot.png").resize((200, 150)))
		imglbl = tk.Label(self, image=img)
		imglbl.image = img
		imglbl.grid(row=1,column=0, padx=(25, 25), pady=(25, 5), sticky='nw')
		
		#Insert in Rucoy Bot URL, and 'Credits' & 'Donate' buttons
		#Rucoy Bot URL
		self.urllbl = tk.Label(self, text=r"https://www.rucoybot.com", bg='black', fg='blue', cursor='hand2')
		self.urllbl.grid(row=1,column=0, padx=(50, 0), pady=(190, 5), sticky='nw')
		self.urllbl.bind("<Button-1>", callback)
		#Make URL have underline.
		self.urlfont = Font(self.urllbl, self.urllbl.cget("font"))
		self.urlfont.configure(underline=True)
		self.urllbl.configure(font=self.urlfont)
		#Credits Button
		creditbtn = tk.Button(cursor='hand2', text="Credits", bg='#57cade', command=self.show_credits)
		creditbtn.grid(row=1, column=0, padx=(65, 10), pady=(230, 40), sticky='nw')
		#Donate Button
		donatebtn = tk.Button(cursor='hand2', text="Donate", bg='#57cade', command=self.show_donate)
		donatebtn.grid(row=1, column=0, padx=(140, 0), pady=(230, 40), sticky='nw')
		
		self.welcomebtn = tk.Button(cursor='hand2', text="Welcome", bg='#57cade', command=self.show_welcome, relief='raised')
		self.welcomebtn.grid(row=1, column=1, columnspan=2, padx=(3, 0), pady=(25, 0), sticky='nw', ipady=1)
		
		self.getstartbtn = tk.Button(cursor='hand2', text="Get Started", bg='black', fg='#9a9a9a',  command=self.show_getstarted, relief='sunken')
		self.getstartbtn.grid(row=1, column=1, columnspan=2, padx=(64, 0), pady=(25, 0), sticky='nw', ipady=1)
		
		self.protipbtn = tk.Button(cursor='hand2', text="Pro Tips", bg='black', fg='#9a9a9a',  command=self.show_protips, relief='sunken')
		self.protipbtn.grid(row=1, column=1, columnspan=2, padx=(133, 0), pady=(25, 0), sticky='nw', ipady=1)
		
		self.finetunebtn = tk.Button(cursor='hand2', text="Fine Tuning", bg='black', fg='#9a9a9a',  command=self.show_finetune, relief='sunken')
		self.finetunebtn.grid(row=1, column=1, columnspan=2, padx=(186, 0), pady=(25, 0), sticky='nw', ipady=1)
		
		self.troublebtn = tk.Button(cursor='hand2', text="Troubleshooting", bg='black', fg='#9a9a9a',  command=self.show_troubleshoot, relief='sunken')
		self.troublebtn.grid(row=1, column=1, columnspan=2, padx=(259, 0), pady=(25, 0), sticky='nw', ipady=1)
		
		#Each intro tab messages
		self.welcometxt = """Hi, thank you for trying out Rucoy Bot!\n\nTo start running a bot for gold, xp, and drops, check out the Get Started Tab.\n\nIf you'd like to learn about advanced settings, check out the Fine Tuning Tab.\n\nFor common troubleshooting and known issues, please refer to the Troubleshooting Tab.\n\nIf you have any other questions/feedback/problems/etc, please contact me at your.rucoybot@gmail.com\n\nThanks. :-) """
		
		self.getstarttxt = """There are four modes down below. To bot, you only need to know Hunting Mode, Farming Mode, and Training Mode.\n\n*   Hunting mode will just attack monsters and ignore any drops.\n*   Farming Mode will hunt monsters and pick up all gold/drops.\n*   Training mode will autoswitch to your training weapon and will focus on stats.\n\nTo Start, it's just 5 steps.\n\n1) Select Hunting, Farming, or Training Mode.\n2) Choose the server you want to bot on. (That number is players online.)\n3) Choose a weapon to bot with. (Melee/Dist/Mage)\n4) Click which potions to use while botting.\n5) Hit 'Start Bot!'"""
		
		self.finetunetxt = """Monitor Mode & Changes-\n*   Monitor mode will not bot for you. Monitor just listens in on Rucoy's \n     conversation with the server and translates it to English.\n*   While it can be interesting, this can be used to 'Disable server switch time limit' \n     or 'Set up store for 12+ hours'.\n*   Note: For disabling server switch limits, Rucoy Online must be restarted after \n     the 'you must wait' message for it to work.\n\nSettings and Filter Menu-\n*   In the bottom left, you can see the Settings Button (the gears icon) and the \n     Filter Menu (the funnel icon).\n*   Settings will let you affect how the bot runs and the Filter Menu will let you \n     change what messages you see in the Console at the very bottom. Please open \n     them for more information. """
		
		self.troubletxt = """Fatal Error: I don't know my coordinates-    If this doesn't resolve itself, double check you're on the right server in the Rucoy app. \n\nMy bot isn't doing anything/It's really slow-   If your internet is slow, that's the problem. If not, manually move your character near a monster. If the bot still fails to attack, double check you're not on monitor mode.\n\nThe bot is moving but isn't attacking anything-   What screen resolution is your device or emulator? If it's not 1280x720 or 720p, hit the Device Menu button (phone icon), and enable 1080p mode.\n\nI still can't get this to work right! -   I'm sorry! Please email me at your.rucoybot@gmail.com """
		
		self.protiptxt = """Pro Tip #1 (Advanced)-\n*   You can actually use this program to bot on your phone! First, just plug your phone into your computer. Next, google how to enable ADB and do so. Then, google, install, and run 'gnirehtet' from github.com \n\nPro Tip #2-\n*   Enable email notifications in the Settings Menu and use your 'email to text' address to get text notifications. For example, Verizon in the U.S. is 5553331111@vtext.com\n\nPro Tip #3-\n*   Use the 'Only Attack' option in the Settings menu to keep your bot focused on the monsters you want. For example, typing in 'Skeleton' prevents your bot from wandering into Drow Territory."""
		
		#Intro text message and positioning code.
		self.introtext = tk.StringVar()
		self.introtext.set(self.welcometxt)
		
		self.intromsg = tk.Message(self, textvariable=self.introtext, anchor='w', justify='left', width=435, bg='#1f1f1f', fg='#57cade', relief='groove')
		self.intromsg.grid(row=1, column=1, columnspan=2, padx=(3, 25), pady=(52, 25), sticky='nw')
		
		#Add Bot Stats Labels, first off header.
		headertext = "        Character Stats        "
		header = tk.Label(self, text=headertext, bg='#1f1f1f', fg='#57cade', relief='groove')
		header.grid(row=2, column=0, padx=(60, 25), pady=(25, 5), sticky='nw')
		#next up is Rucoy Stats, so xp.
		xplbl = tk.Label(self, text=" Lvl XP: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		xplbl.grid(row=3, column=0, padx=(60, 25), pady=(5, 0), sticky='nw')
		self.xpvar = tk.StringVar()
		self.xpvar.set(" 0 ")
		self.xpvar_start = self.xpvar.get()
		xpinfo = tk.Label(self, textvariable=self.xpvar, bg='#1f1f1f', fg='#57cade', relief='groove')
		xpinfo.grid(row=3, column=0, padx=(2, 82), pady=(5, 0), sticky='ne')
		#next up is stats so melee, mage, dist, defense.
		#melee xp label widget
		meleelbl = tk.Label(self, text=" Melee XP: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		meleelbl.grid(row=4, column=0, padx=(60, 25), pady=(5, 0), sticky='nw')
		self.meleevar = tk.StringVar()
		self.meleevar.set(" 0 ")
		self.meleevar_start = self.meleevar.get()
		meleeinfo = tk.Label(self, textvariable=self.meleevar, bg='#1f1f1f', fg='#57cade', relief='groove')
		meleeinfo.grid(row=4, column=0, padx=(2, 82), pady=(5, 0), sticky='ne')
		#dist xp label widget
		distlbl = tk.Label(self, text=" Dist XP: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		distlbl.grid(row=5, column=0, padx=(60, 25), pady=(5, 0), sticky='nw')
		self.distvar = tk.StringVar()
		self.distvar.set(" 0 ")
		self.distvar_start = self.distvar.get()
		distinfo = tk.Label(self, textvariable=self.distvar, bg='#1f1f1f', fg='#57cade', relief='groove')
		distinfo.grid(row=5, column=0, padx=(2, 82), pady=(5, 0), sticky='ne')
		#mage xp label widget
		magelbl = tk.Label(self, text=" Mage XP: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		magelbl.grid(row=6, column=0, padx=(60, 25), pady=(5, 0), sticky='nw')
		self.magevar = tk.StringVar()
		self.magevar.set(" 0 ")
		self.magevar_start = self.magevar.get()
		mageinfo = tk.Label(self, textvariable=self.magevar, bg='#1f1f1f', fg='#57cade', relief='groove')
		mageinfo.grid(row=6, column=0, padx=(2, 82), pady=(5, 0), sticky='ne')
		#def xp label widget
		deflbl = tk.Label(self, text=" Def XP: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		deflbl.grid(row=7, column=0, padx=(60, 25), pady=(5, 0), sticky='nw')
		self.defvar = tk.StringVar()
		self.defvar.set(" 0 ")
		self.defvar_start = self.defvar.get()
		definfo = tk.Label(self, textvariable=self.defvar, bg='#1f1f1f', fg='#57cade', relief='groove')
		definfo.grid(row=7, column=0, padx=(2, 82), pady=(5, 0), sticky='ne')
		#now lets show gold gained
		goldlbl = tk.Label(self, text=" Gold: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		goldlbl.grid(row=8, column=0, padx=(60, 25), pady=(5, 0), sticky='nw')
		self.goldvar = tk.StringVar()
		self.goldvar.set(" 0 ")
		self.goldvar_start = self.goldvar.get()
		goldinfo = tk.Label(self, textvariable=self.goldvar, bg='#1f1f1f', fg='#57cade', relief='groove')
		goldinfo.grid(row=8, column=0, padx=(2, 82), pady=(5, 0), sticky='ne')
		#Settings and Filter variables
		self.botspecial = False
		self.botpottime = '80,80,0'
		self.good_option = 1
		self.resolve_var = 0
		self.upload_var = 1
		self.email_notifications = 0
		self.to_email = ""
		self.atkok_var = 0
		self.atkok_name = ''
		'''
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
		"youare",
		"friendlist",
		'''
		self.filters = [
			"redmsg",
			"whitemsg",
			"bot",
			"client"
		]
		self.devserial = ''
		self.devratio = 1
		#Settings button
		self.settings_img = ImageTk.PhotoImage(Image.open("settings.png").resize((25, 25)))
		self.settingbtn = tk.Button(self, cursor='hand2', image=self.settings_img, bg='#1f1f1f', command=self.settingsplz)
		self.settingbtn.image = self.settings_img
		self.settingbtn.grid(row=20, column=0, padx=(60, 2), pady=(5, 0), sticky='nw')
		#Adb Device Button
		self.adbdevice_img = ImageTk.PhotoImage(Image.open("phone.png").resize((25, 25)))
		self.adbdevicebtn = tk.Button(self, cursor='hand2', image=self.adbdevice_img, bg='#1f1f1f', command=self.chooseadbplz)
		self.adbdevicebtn.image = self.adbdevice_img
		self.adbdevicebtn.grid(row=20, column=0, padx=(110, 2), pady=(5, 0), sticky='nw')
		#Filter button
		self.filter_img = ImageTk.PhotoImage(Image.open("filter.png").resize((25, 25)))
		self.filterbtn = tk.Button(self, cursor='hand2', image=self.filter_img, bg='#1f1f1f', command=self.filterplz)
		self.filterbtn.image = self.filter_img
		self.filterbtn.grid(row=20, column=0, padx=(2, 82), pady=(5, 0), sticky='ne')
		#Set botmode to have highlighted option among modes.
		self.botmode = 0
		
		#Options Label to oversee all options.
		options = tk.Label(self, text="              Options              ", bg='#1f1f1f', fg='#57cade', relief='groove')
		options.grid(row=2, column=1, columnspan=2, padx=(155, 0), pady=(5, 10), sticky='w')
		#Mode options, label & label with image for each one.
		#First off, Monitor mode.
		monoption = tk.Label(self, text=" Monitor Mode: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		monoption.grid(row=3, column=1, pady=(5, 0), sticky='nw')
		self.monimg_active = ImageTk.PhotoImage(Image.open("mon_active.png").resize((15, 15)))
		self.monimg_disabled = ImageTk.PhotoImage(Image.open("mon_disabled.png").resize((15, 15)))
		self.monimgbtn = tk.Button(self, cursor='hand2', image=self.monimg_active, bg="#49e0e3", command=self.monitorplz)
		self.monimgbtn.image = self.monimg_active
		self.monimgbtn.grid(row=3, column=1, padx=(150, 0), pady=(5, 0), sticky='nw')
		#Second off, Hunting mode.
		huntoption = tk.Label(self, text=" Hunting Mode: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		huntoption.grid(row=4, column=1, pady=(5, 0), sticky='nw')
		self.huntimg_active = ImageTk.PhotoImage(Image.open("hunt_active.png").resize((15, 15)))
		self.huntimg_disabled = ImageTk.PhotoImage(Image.open("hunt_disabled.png").resize((15, 15)))
		self.huntimgbtn = tk.Button(self, cursor='hand2', image=self.huntimg_disabled, bg='#1f1f1f', command=self.hunterplz)
		self.huntimgbtn.image = self.huntimg_disabled
		self.huntimgbtn.grid(row=4, column=1, padx=(150, 0), pady=(5, 0), sticky='nw')
		#Third off, Farming mode.
		farmoption = tk.Label(self, text=" Farming Mode: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		farmoption.grid(row=5, column=1, pady=(5, 0), sticky='nw')
		self.farmimg_active = ImageTk.PhotoImage(Image.open("farm_active.png").resize((15, 15)))
		self.farmimg_disabled = ImageTk.PhotoImage(Image.open("farm_disabled.png").resize((15, 15)))
		self.farmimgbtn = tk.Button(self, cursor='hand2', image=self.farmimg_disabled, bg='#1f1f1f', command=self.farmerplz)
		self.farmimgbtn.image = self.farmimg_disabled
		self.farmimgbtn.grid(row=5, column=1, padx=(150, 0), pady=(5, 0), sticky='nw')
		#Last off, Skill Training mode.
		skilloption = tk.Label(self, text=" Training Mode: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		skilloption.grid(row=6, column=1, pady=(5, 0), sticky='nw')
		self.skillimg_active = ImageTk.PhotoImage(Image.open("skill_active.png").resize((15, 15)))
		self.skillimg_disabled = ImageTk.PhotoImage(Image.open("skill_disabled.png").resize((15, 15)))
		self.skillimgbtn = tk.Button(self, cursor='hand2', image=self.skillimg_disabled, bg='#1f1f1f', command=self.skillerplz)
		self.skillimgbtn.image = self.skillimg_disabled
		self.skillimgbtn.grid(row=6, column=1, padx=(150, 0), pady=(5, 0), sticky='nw')
		
		#Weapon mode selection, Wand, Bow, or Sword. Set up var for which weapon selected.
		modeoption = tk.Label(self, text=" Select a weapon to use while botting: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		modeoption.grid(row=7, column=1, pady=(5, 0), sticky='nw')
		self.weapon = 0
		self.tier = 1
		#Set Var to keep track of which level range weapon to show/ no sword/ training dagger.
		self.swordimg_n = ImageTk.PhotoImage(Image.open("nosword.png").resize((35, 35)))
		self.swordimg_t = ImageTk.PhotoImage(Image.open("tsword.png").resize((35, 35)))
		self.swordimg_1 = ImageTk.PhotoImage(Image.open("1sword.png").resize((35, 35)))
		self.swordimg_2 = ImageTk.PhotoImage(Image.open("2sword.png").resize((35, 35)))
		self.swordimg_3 = ImageTk.PhotoImage(Image.open("3sword.png").resize((35, 35)))
		self.swordimg_4 = ImageTk.PhotoImage(Image.open("4sword.png").resize((35, 35)))
		self.swordimg_5 = ImageTk.PhotoImage(Image.open("5sword.png").resize((35, 35)))
		self.swordimg_6 = ImageTk.PhotoImage(Image.open("6sword.png").resize((35, 35)))
		self.swordimg_7 = ImageTk.PhotoImage(Image.open("7sword.png").resize((35, 35)))
		#Create sword image Label and grid into place.
		self.swordimgbtn = tk.Button(self, cursor='hand2', image=self.swordimg_n, bg='#1f1f1f', command=self.swordplz)
		self.swordimgbtn.image = self.swordimg_n
		self.swordimgbtn.grid(row=8, column=1, padx=(10, 0), pady=(10, 0), sticky='nw')
		
		#Set Var to keep track of which level range weapon to show/ no bow/ training bow.
		self.bowimg_n = ImageTk.PhotoImage(Image.open("nobow.png").resize((35, 35)))
		self.bowimg_t = ImageTk.PhotoImage(Image.open("tbow.png").resize((35, 35)))
		self.bowimg_1 = ImageTk.PhotoImage(Image.open("1bow.png").resize((35, 35)))
		self.bowimg_2 = ImageTk.PhotoImage(Image.open("2bow.png").resize((35, 35)))
		self.bowimg_3 = ImageTk.PhotoImage(Image.open("3bow.png").resize((35, 35)))
		self.bowimg_4 = ImageTk.PhotoImage(Image.open("4bow.png").resize((35, 35)))
		self.bowimg_5 = ImageTk.PhotoImage(Image.open("5bow.png").resize((35, 35)))
		self.bowimg_6 = ImageTk.PhotoImage(Image.open("6bow.png").resize((35, 35)))
		self.bowimg_7 = ImageTk.PhotoImage(Image.open("7bow.png").resize((35, 35)))
		#Create bow image Label and grid into place.
		self.bowimgbtn = tk.Button(self, cursor='hand2', image=self.bowimg_n, bg='#1f1f1f', command=self.bowplz)
		self.bowimgbtn.image = self.bowimg_n
		self.bowimgbtn.grid(row=8, column=1, padx=(75, 0), pady=(10, 0), sticky='nw')
		
		#Set Var to keep track of which level range weapon to show/ no wand/ training wand.
		self.wandimg_n = ImageTk.PhotoImage(Image.open("nowand.png").resize((35, 35)))
		self.wandimg_t = ImageTk.PhotoImage(Image.open("twand.png").resize((35, 35)))
		self.wandimg_1 = ImageTk.PhotoImage(Image.open("1wand.png").resize((35, 35)))
		self.wandimg_2 = ImageTk.PhotoImage(Image.open("2wand.png").resize((35, 35)))
		self.wandimg_3 = ImageTk.PhotoImage(Image.open("3wand.png").resize((35, 35)))
		self.wandimg_4 = ImageTk.PhotoImage(Image.open("4wand.png").resize((35, 35)))
		self.wandimg_5 = ImageTk.PhotoImage(Image.open("5wand.png").resize((35, 35)))
		self.wandimg_6 = ImageTk.PhotoImage(Image.open("6wand.png").resize((35, 35)))
		self.wandimg_7 = ImageTk.PhotoImage(Image.open("7wand.png").resize((35, 35)))
		#Create wand image Label and grid into place.
		self.wandimgbtn = tk.Button(self, cursor='hand2', image=self.wandimg_n, bg='#1f1f1f', command=self.wandplz)
		self.wandimgbtn.image = self.wandimg_n
		self.wandimgbtn.grid(row=8, column=1, padx=(140, 0), pady=(10, 0), sticky='nw')
		
		#Right side options columns, Server Options & Unlimited Server Switch Option & 10 Day Store Setup
		#Choose a server drop down menu widget set up.
		self.servopt = tk.Label(self, text=" Please Choose a Server to Play On Below: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.servopt.grid(row=3, column=2, pady=(5, 0), sticky='nw')
		#Grab the server data from the rucoyonline.com json file
		self.server_options = tk.StringVar()
		self.all_servers = ['Any Server']
		
		self.update_servlist()
		
		self.server_options.set(self.all_servers[0])
		self.servoptdd = tk.OptionMenu(self, self.server_options, *self.all_servers)
		servoptddfont = Font(size=6)
		self.servoptdd.config(bg='#1f1f1f', fg='#57cade', font=servoptddfont, width=20)
		self.servoptdd['menu'].config(bg='#1f1f1f', fg='#57cade')
		self.servoptdd['highlightthickness'] = 0
		self.servoptdd.grid(row=4, column=2, pady=(5, 0), sticky='w')
		#Refresh Server List Button
		self.reload_serv_img = ImageTk.PhotoImage(Image.open("reload.png").resize((15, 15)))
		#Create wand image Label and grid into place.
		self.reload_serv_btn = tk.Button(self, cursor='hand2', image=self.reload_serv_img, bg='#1f1f1f', command=self.update_servlist)
		self.reload_serv_btn.image = self.reload_serv_img
		self.reload_serv_btn.grid(row=4, column=2, padx=(140, 0), pady=(5, 0), sticky='w')
		#Set up label and checkbox for unlimited server switcharoo.
		self.switchlbl = tk.Label(self, text=" Disable server switch time limit: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.switchlbl.grid(row=5, column=2, pady=(5, 0), sticky='nw')
		#Add checkbox to turn on and off adb xml continuous rewrite mode.
		self.switchvar = tk.IntVar()
		self.switchvar.set(0)
		self.server_adb = Thread(target=server_switch_adb_mod,args=(self.switchvar,self.devserial,))
		self.switchcb = Slider2(self, variable=self.switchvar, onvalue=1, offvalue=0, command=self.switchcbplz, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.switchcb.grid(row=5, column=2, padx=(10, 15), pady=(5, 0), sticky='ne')
		#Set up label and checkbox for store set up hours mod.
		self.hours = 0
		self.storelbl = tk.Label(self, text=" Set up store for 12+ hours: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.storelbl.grid(row=6, column=2, pady=(5, 0), sticky='nw')
		#Add checkbox to turn on and off set up shop payload modification.
		self.storevar = tk.IntVar()
		self.storevar.set(0)
		self.storecb = Slider(self, variable=self.storevar, onvalue=1, offvalue=0, command=self.storecbplz, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.storecb.grid(row=6, column=2, padx=(10, 15), pady=(5, 0), sticky='ne')
		
		
		#Set up label for which potion to use for auto-potting.
		self.potlbl = tk.Label(self, text=" Select which potions to use: ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.potlbl.grid(row=7, column=2, pady=(5, 0), sticky='nw')
		self.hppot = 0
		self.mppot = 0
		self.pottier = 1
		#Create HP potion image resources.
		self.hppotimg_1 = ImageTk.PhotoImage(Image.open("h1pot.png").resize((35, 35)))
		self.hppotimg_2 = ImageTk.PhotoImage(Image.open("h2pot.png").resize((35, 35)))
		self.hppotimg_3 = ImageTk.PhotoImage(Image.open("h3pot.png").resize((35, 35)))
		self.hppotimg_n = ImageTk.PhotoImage(Image.open("nopot.png").resize((35, 35)))
		#Create HP Potion image label and grid into place.
		self.hppotimgbtn = tk.Button(self, cursor='hand2', image=self.hppotimg_n, bg='#1f1f1f', command=self.hppotplz)
		self.hppotimgbtn.image = self.hppotimg_n
		self.hppotimgbtn.grid(row=8, column=2, padx=(20, 0), pady=(10, 0), sticky='nw')
		#Create MP Potion image resources.
		self.mppotimg_1 = ImageTk.PhotoImage(Image.open("m1pot.png").resize((35, 35)))
		self.mppotimg_2 = ImageTk.PhotoImage(Image.open("m2pot.png").resize((35, 35)))
		self.mppotimg_3 = ImageTk.PhotoImage(Image.open("m3pot.png").resize((35, 35)))
		self.mppotimg_n = ImageTk.PhotoImage(Image.open("nopot.png").resize((35, 35)))
		#Create MP Potion image label and grid into place.
		self.mppotimgbtn = tk.Button(self, cursor='hand2', image=self.mppotimg_n, bg='#1f1f1f', command=self.mppotplz)
		self.mppotimgbtn.image = self.mppotimg_n
		self.mppotimgbtn.grid(row=8, column=2, padx=(80, 0), pady=(10, 0), sticky='nw')
		
		
		
		#Start and Stop buttons for the Rucoy Bot and translation/mitm processes
		self.startbtn = tk.Button(text="Start Bot!", cursor='hand2', bg='#c7ffb5', command=self.start_bot)
		self.stopbtn = tk.Button(text="Stop Bot", cursor='hand2', bg='#f73e47', command=self.quit_bot)
		self.startbtn.grid(row=20, column=1, padx=(10, 20), pady=(25, 25), sticky='e')
		self.stopbtn.grid(row=20, column=2, padx=(10, 10), pady=(25, 25), sticky='w')
		
		
		#Button to hide/show mini console
		self.text_visible = True
		self.view_img = ImageTk.PhotoImage(Image.open("view.png").resize((15, 15)))
		self.view_imgd = ImageTk.PhotoImage(Image.open("viewd.png").resize((15, 15)))
		self.viewbtn = tk.Button(self, cursor='hand2', image=self.view_imgd, bg='#1f1f1f', command=self.viewplz)
		self.viewbtn.image = self.view_imgd
		self.viewbtn.grid(row=20, column=2, padx=(5, 20), pady=(5, 0), sticky='se')
		
		#Pop out button to mimic console like view of packets going back and forth.
		self.expand_img = ImageTk.PhotoImage(Image.open("maximize.png").resize((15, 15)))
		self.expandbtn = tk.Button(self, cursor='hand2', image=self.expand_img, bg='#1f1f1f', command=self.expandplz)
		self.expandbtn.image = self.expand_img
		self.expandbtn.grid(row=20, column=2, padx=(5, 0), pady=(5, 0), sticky='se')
		
		#Little Box to show character name while botting.
		self.botname = tk.StringVar()
		self.botname.set(" ")
		self.namelbl = tk.Label(self, textvariable=self.botname, bg='black', fg='#999999')
		self.namelbl.grid(row=20, column=0, columnspan=3, padx=(25, 0), sticky='sw')
		
		#Text Widget to hold all of the real time translated data from the mitm processes
		self.text = CustomText(self, width=90, height=6, wrap="word")
		self.text.config(bg="#1f1f1f")
		self.text.tag_configure("stderr", foreground="#b22222")
		self.text.tag_configure("stdout", foreground="#57cade")
		
		#Add scroll bar and grid the text/scrollbar to it's place
		self.scroll = tk.Scrollbar(command=self.text.yview, orient=tk.VERTICAL)
		self.text.grid(row=21, column=0, columnspan=3, padx=(25, 0), sticky='e')
		self.scroll.grid(row=21, column=3, padx=(0, 30), sticky='nws')
		self.text.configure(yscrollcommand=self.scroll.set)
		
		#Add in phantom label to keep grid spacing maintained after text and scroll disappear
		phantom_txt = " "*250
		self.nolbl = tk.Label(self, text=phantom_txt, bg='black', fg='black')
		self.nolbl.grid(row=22, column=0, columnspan=4, padx=(5, 5), pady=(5, 5), sticky='sew')
		
		#Keep track of whether bot and mitm processes are running so it doesn't get execute twice
		self.botpower = False
		
		#Redirect stdout and stderr from rucoygui (main process) to the text widget.
		sys.stdout = TextRedirector(self.text, "stdout")
		sys.stderr = TextRedirector(self.text, "stderr")
		
		#Print an explanation for this text widget at the bottom
		print("Welcome to Rucoy Bot! This is where all messages going back and forth on the internet will be shown ", end='')
		print("while your bot is running. Configure the options you would like above and then hit 'Start Bot!' when ", end='')
		print("you're all ready to go! Thank you. :)")
		
		self.deiconify()
	
	def update_servlist(self):
		try:
			self.all_servers = ['Any Server']
			self.servjson = get_jsonparsed_data("https://www.rucoyonline.com/server_list.json")
			for a in self.servjson.get('servers'):
				if a.get('visible'):
					info = '{} - {}'.format(a.get('name'), a.get('characters_online'))
					self.all_servers.append(info)
			self.all_servers = sorted(self.all_servers)
			if self.server_options.get() != '':
				for item in self.all_servers:
					if item.startswith(self.server_options.get()):
						self.server_options.set(item)
			else:
				self.server_options.set(self.all_servers[0])
			#Finish setting up widgets with data now obtained from the internet.
			#self.servoptdd.grid_remove()
			#self.servoptdd.grid(row=4, column=2, pady=(5, 0), sticky='w')
		except:
			self.servjson = 'failed'
			self.all_servers = ['Network Failure']
			self.server_options.set(self.all_servers[0])
		
		self.servoptdd = tk.OptionMenu(self, self.server_options, *self.all_servers)
		servoptddfont = Font(size=6)
		self.servoptdd.config(bg='#1f1f1f', fg='#57cade', font=servoptddfont, width=20)
		self.servoptdd['menu'].config(bg='#1f1f1f', fg='#57cade')
		self.servoptdd['highlightthickness'] = 0
		self.servoptdd.grid(row=4, column=2, pady=(5, 0), sticky='w')
		
		#self.after(90, self.update_servlist)
	
	def text_catcher(self):
		if not self.botpower:
			return
		if self.qu.empty() and self.botpower:
			self.after(5, self.text_catcher)
			return
		first = self.qu.get()
		if first[-2:] == "> ":
			print(first, end='')
		elif first == '' or first == " " or first == '\n':
			pass
		elif first[:2] == '!#':
			#decode invisible data from mitm
			stats = first[2:].split('|')
			if stats[0] == 'lxp':
				x = int(stats[1])
				y = "{:,d}".format(x)
				if self.xpvar.get() == ' 0 ':
					self.xpvar_start = x
				self.xpvar.set(y)
			elif stats[0] == 'mel':
				x = int(stats[1])
				y = "{:,d}".format(x)
				if self.meleevar.get() == ' 0 ':
					self.meleevar_start = x
				self.meleevar.set(y)
			elif stats[0] == 'dis':
				x = int(stats[1])
				y = "{:,d}".format(x)
				if self.distvar.get() == ' 0 ':
					self.distvar_start = x
				self.distvar.set(y)
			elif stats[0] == 'mag':
				x = int(stats[1])
				y = "{:,d}".format(x)
				if self.magevar.get() == ' 0 ':
					self.magevar_start = x
				self.magevar.set(y)
			elif stats[0] == 'def':
				x = int(stats[1])
				y = "{:,d}".format(x)
				if self.defvar.get() == ' 0 ':
					self.defvar_start = x
				self.defvar.set(y)
			elif stats[0] == 'gld':
				x = int(stats[1])
				y = "{:,d}".format(x)
				if self.goldvar.get() == ' 0 ':
					self.goldvar_start = x
				self.goldvar.set(y)
			elif stats[0] == 'iam':
				self.botname.set(stats[1])
			elif stats[0] == 'die':
				self.quit_bot()
			else:
				#Assumes stats[0] == 'lvl' and stats[1] == '{player_level}'
				level = int(stats[1])
				tier_changed = False
				
				#Set tier for which weapon icon to show.
				if level < 75:
					if self.tier != 1:
						self.tier = 1
						tier_changed = True
				elif level >= 75 and level < 125:
					if self.tier != 2:
						self.tier = 2
						tier_changed = True
				elif level >= 125 and level < 175:
					if self.tier != 3:
						self.tier = 3
						tier_changed = True
				elif level >= 175 and level < 275:
					if random() < 0.5:
						if self.tier != 4:
							self.tier = 4
							tier_changed = True
					else:
						if self.tier != 5:
							self.tier = 5
							tier_changed = True
				elif level >= 275 and level < 375:
					if self.tier != 6:
						self.tier = 6
						tier_changed = True
				elif level >= 375:
					if self.tier != 7:
						self.tier = 7
						tier_changed = True
				else:
					pass
				
				#Change icons if tier changed.
				if tier_changed:
					if self.weapon == 0:
						self.bowplz(bypass=True)
						self.swordplz(bypass=True)
					elif self.weapon == 1:
						self.swordplz(bypass=True)
						self.bowplz(bypass=True)
					else:
						self.bowplz(bypass=True)
						self.wandplz(bypass=True)
				
				#Set tier for which potion icon to show.
				if level < 75:
					if self.pottier != 1:
						self.pottier = 1
						tier_changed = True
				elif level >= 75 and level < 175:
					if self.pottier != 2:
						self.pottier = 2
						tier_changed = True
				elif level >= 175:
					if self.pottier != 3:
						self.pottier = 3
						tier_changed = True
				
				#Change icons if tier changed.
				if tier_changed:
					self.hppotplz(bypass=True)
					self.mppotplz(bypass=True)
					self.hppotplz(bypass=True)
					self.mppotplz(bypass=True)
		else:
			s = str(float(self.text.index("insert"))-2)
			print(first)
			if first.find("Bye Bye!") >= 0:
				self.quit_bot('no')
			highlight_update(self.text, start=s)
			self.text.see("end")
		if self.botpower:
			self.after(10, self.text_catcher)
	
	def show_welcome(self):
		self.introtext.set(self.welcometxt)
		self.welcomebtn.config(bg='#57cade', fg='black', relief='raised')
		self.getstartbtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.finetunebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.troublebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.protipbtn.config(bg='black', fg='#9a9a9a', relief='sunken')
	
	def show_getstarted(self):
		self.introtext.set(self.getstarttxt)
		self.getstartbtn.config(bg='#57cade', fg='black', relief='raised')
		self.welcomebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.finetunebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.troublebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.protipbtn.config(bg='black', fg='#9a9a9a', relief='sunken')
	
	def show_finetune(self):
		self.introtext.set(self.finetunetxt)
		self.finetunebtn.config(bg='#57cade', fg='black', relief='raised')
		self.welcomebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.getstartbtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.troublebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.protipbtn.config(bg='black', fg='#9a9a9a', relief='sunken')
	
	def show_troubleshoot(self):
		self.introtext.set(self.troubletxt)
		self.troublebtn.config(bg='#57cade', fg='black', relief='raised')
		self.welcomebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.finetunebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.getstartbtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.protipbtn.config(bg='black', fg='#9a9a9a', relief='sunken')
	
	def show_protips(self):
		self.introtext.set(self.protiptxt)
		self.protipbtn.config(bg='#57cade', fg='black', relief='raised')
		self.troublebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.welcomebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.finetunebtn.config(bg='black', fg='#9a9a9a', relief='sunken')
		self.getstartbtn.config(bg='black', fg='#9a9a9a', relief='sunken')
	
	def show_credits(self):
		credit_msg = """This application was developed by a big fan of Rucoy Online who doesn't want to be banned, so you can just refer to me as Mr. Wolf.\n\nHowever, that said, this couldn't have been done without a lot of help and freely available code.\n\nSo first off, biggest thanks to my good friend, Gerald, for putting up with all my constant updates and bitching. I honestly doubt I would have been able to keep up my motivation without him.\n\nNext, thanks to Fabio Falcinelli who wrote the python wrapper, PyDivert, for WinDivert, which was made by basil@recrypt.org. Without the pydivert/windivert functionality, this would've just been another bot that uses image recognition libraries.\n\nThanks to Freepik, Good Ware, Vectors Market, Kiranshastry, Those Icons, bqlqn, and monkik from flaticon.com for their freely available icons. \n\nHuge thanks out to all the python open source developers. I know I'd be searching for days trying to find a list of contributors but without all their hard work developing such powerful libraries, this code would have taken 15 times longer.\n\nLastly, thank you, the user. Without you, there would have never been a point in creating this, and I wouldn't have had so much fun coding and learning."""
		
		set_x = self.winfo_toplevel().winfo_rootx()
		set_y = self.winfo_toplevel().winfo_rooty()
		
		creditmsg = MsgBox("Credits", credit_msg, 31, set_x, set_y)
		
	def show_donate(self):
		donate_msg = """Wow! I've put a lot of time into this project here and let me tell you I've certainly learned a ton. I never really expected money out of this project, but if you're willing to donate something, I would appreciate it a lot! It'll tell me that someone out there truly appreciates the months of free time I poured into this.\nPlease send any donations to my bitcoin address listed below. I apologize in advance for not taking different forms of donation, but I don't want to get banned over this! Lastly, if you're donating money to me, that's all the more reason to give me feedback! Please go to my site, rucoybot.com, and let me know what you loved and hated! There's a lot more that could be added, but I'm sure you might have a few ideas I haven't considered! Thanks, again!\n\nBitcoin address: 1KAsaT639znsW5BVAKXUV4CY6EccyVAUab"""
		
		set_x = self.winfo_toplevel().winfo_rootx()
		set_y = self.winfo_toplevel().winfo_rooty()
		
		donatemsg = MsgBox("Donate", donate_msg, 17, set_x, set_y)
	
	def settingsplz(self):
		set_x = self.winfo_toplevel().winfo_rootx()
		set_y = self.winfo_toplevel().winfo_rooty()
		
		showsettings = SettingsBox(self, "Settings Menu", 17, set_x, set_y)
		showsettings.wait_window()
		self.focus()
	
	def chooseadbplz(self):
		set_x = self.winfo_toplevel().winfo_rootx()
		set_y = self.winfo_toplevel().winfo_rooty()
		
		show_adb_device_window = DeviceBox(self, set_x, set_y)
		show_adb_device_window.wait_window()
		self.focus()
		
	def filterplz(self):
		set_x = self.winfo_toplevel().winfo_rootx()
		set_y = self.winfo_toplevel().winfo_rooty()
		
		showfilter = FilterBox(self, "Filter Menu", set_x, set_y)
		showfilter.wait_window()
		self.focus()
		
	def storecbplz(self):
		if self.storevar.get() == 1:
			self.hours = 0
			set_x = self.winfo_toplevel().winfo_rootx()
			set_y = self.winfo_toplevel().winfo_rooty()
			
			hour_msg = """Please enter how many hours you would like to set up your store. It must be between 13 and 255 with no spaces."""
			
			askforhours = ValueBox(self, "Store Set Up Time", hour_msg, 3, set_x, set_y)
			askforhours.wait_window()
			self.focus()
			if self.hours != 0:
				print("You will now set up a store for {} hours when the bot is started on monitor mode!".format(self.hours))
				return 1
			else:
				print("Store set up times reverted to player input.")
				return 0
		else:
			print("Store set up times reverted to player input.")
			return 0
		
	def switchcbplz(self):
		if self.switchvar.get() == 1:
			print("You can now switch servers infinitely with no time limits!")
			self.server_adb = Thread(target=server_switch_adb_mod,args=(self.switchvar,self.devserial,))
			self.server_adb.daemon = True
			self.server_adb.start()
			return 1
		else:
			self.server_adb.do_run = False
			print("The time limits on server switching has been restored.")
			return 0
		
	def swordplz(self, bypass=False):
		#Make sure bot mode is any mode other than monitor and sword is not already selected.
		if self.botpower and bypass == False:
			sys.stderr.write('These settings cannot be changed until the bot is stopped.\n')
			return
		if self.botmode != 0 and self.weapon != 0:
			self.weapon = 0
			self.bowimgbtn.config(bg='#1f1f1f', image=self.bowimg_n)
			self.bowimgbtn.image = self.bowimg_n
			self.wandimgbtn.config(bg='#1f1f1f', image=self.wandimg_n)
			self.wandimgbtn.image = self.wandimg_n
			if self.botmode != 3:
				#Code for showing color swords if bot mode is other than training mode.
				if self.tier == 1:
					self.swordimgbtn.config(bg="#49e0e3", image=self.swordimg_1)
					self.swordimgbtn.image = self.swordimg_1
				elif self.tier == 2:
					self.swordimgbtn.config(bg="#49e0e3", image=self.swordimg_2)
					self.swordimgbtn.image = self.swordimg_2
				elif self.tier == 3:
					self.swordimgbtn.config(bg="#49e0e3", image=self.swordimg_3)
					self.swordimgbtn.image = self.swordimg_3
				elif self.tier == 4:
					self.swordimgbtn.config(bg="#49e0e3", image=self.swordimg_4)
					self.swordimgbtn.image = self.swordimg_4
				elif self.tier == 5:
					self.swordimgbtn.config(bg="#49e0e3", image=self.swordimg_5)
					self.swordimgbtn.image = self.swordimg_5
				elif self.tier == 6:
					self.swordimgbtn.config(bg="#49e0e3", image=self.swordimg_6)
					self.swordimgbtn.image = self.swordimg_6
				elif self.tier == 7:
					self.swordimgbtn.config(bg="#49e0e3", image=self.swordimg_7)
					self.swordimgbtn.image = self.swordimg_7
			else:
				self.swordimgbtn.config(bg="#49e0e3", image=self.swordimg_t)
				self.swordimgbtn.image = self.swordimg_t
				
		
	def bowplz(self, bypass=False):
		#Make sure bot mode is any mode other than monitor and sword is not already selected.
		if self.botpower and bypass == False:
			sys.stderr.write('These settings cannot be changed until the bot is stopped.\n')
			return
		if self.botmode != 0 and self.weapon != 1:
			self.weapon = 1
			self.swordimgbtn.config(bg='#1f1f1f', image=self.swordimg_n)
			self.swordimgbtn.image = self.swordimg_n
			self.wandimgbtn.config(bg='#1f1f1f', image=self.wandimg_n)
			self.wandimgbtn.image = self.wandimg_n
			if self.botmode != 3:
				#Code for showing color bows if bot mode is other than training mode.
				if self.tier == 1:
					self.bowimgbtn.config(bg="#49e0e3", image=self.bowimg_1)
					self.bowimgbtn.image = self.bowimg_1
				elif self.tier == 2:
					self.bowimgbtn.config(bg="#49e0e3", image=self.bowimg_2)
					self.bowimgbtn.image = self.bowimg_2
				elif self.tier == 3:
					self.bowimgbtn.config(bg="#49e0e3", image=self.bowimg_3)
					self.bowimgbtn.image = self.bowimg_3
				elif self.tier == 4:
					self.bowimgbtn.config(bg="#49e0e3", image=self.bowimg_4)
					self.bowimgbtn.image = self.bowimg_4
				elif self.tier == 5:
					self.bowimgbtn.config(bg="#49e0e3", image=self.bowimg_5)
					self.bowimgbtn.image = self.bowimg_5
				elif self.tier == 6:
					self.bowimgbtn.config(bg="#49e0e3", image=self.bowimg_6)
					self.bowimgbtn.image = self.bowimg_6
				elif self.tier == 7:
					self.bowimgbtn.config(bg="#49e0e3", image=self.bowimg_7)
					self.bowimgbtn.image = self.bowimg_7
			else:
				self.bowimgbtn.config(bg="#49e0e3", image=self.bowimg_t)
				self.bowimgbtn.image = self.bowimg_t
			
	def wandplz(self, bypass=False):
		#Make sure bot mode is any mode other than monitor and sword is not already selected.
		if self.botpower and bypass == False:
			sys.stderr.write('These settings cannot be changed until the bot is stopped.\n')
			return
		if self.botmode != 0 and self.weapon != 2:
			self.weapon = 2
			self.swordimgbtn.config(bg='#1f1f1f', image=self.swordimg_n)
			self.swordimgbtn.image = self.swordimg_n
			self.bowimgbtn.config(bg='#1f1f1f', image=self.bowimg_n)
			self.bowimgbtn.image = self.bowimg_n
			if self.botmode != 3:
				#Code for showing color wands if bot mode is other than training mode.
				if self.tier == 1:
					self.wandimgbtn.config(bg="#49e0e3", image=self.wandimg_1)
					self.wandimgbtn.image = self.wandimg_1
				elif self.tier == 2:
					self.wandimgbtn.config(bg="#49e0e3", image=self.wandimg_2)
					self.wandimgbtn.image = self.wandimg_2
				elif self.tier == 3:
					self.wandimgbtn.config(bg="#49e0e3", image=self.wandimg_3)
					self.wandimgbtn.image = self.wandimg_3
				elif self.tier == 4:
					self.wandimgbtn.config(bg="#49e0e3", image=self.wandimg_4)
					self.wandimgbtn.image = self.wandimg_4
				elif self.tier == 5:
					self.wandimgbtn.config(bg="#49e0e3", image=self.wandimg_5)
					self.wandimgbtn.image = self.wandimg_5
				elif self.tier == 6:
					self.wandimgbtn.config(bg="#49e0e3", image=self.wandimg_6)
					self.wandimgbtn.image = self.wandimg_6
				elif self.tier == 7:
					self.wandimgbtn.config(bg="#49e0e3", image=self.wandimg_7)
					self.wandimgbtn.image = self.wandimg_7
			else:
				self.wandimgbtn.config(bg="#49e0e3", image=self.wandimg_t)
				self.wandimgbtn.image = self.wandimg_t
			
	def hppotplz(self, bypass=False):
		#Make sure bot mode is any mode other than monitor and hppot is not already selected.
		if self.botpower and bypass == False:
			sys.stderr.write('These settings cannot be changed until the bot is stopped.\n')
			return
		if self.botmode != 0:
			if self.hppot == 0:
				self.hppot = 1
				if self.pottier == 1:
					self.hppotimgbtn.config(bg="#49e0e3", image=self.hppotimg_1)
					self.hppotimgbtn.image = self.hppotimg_1
				elif self.pottier == 2:
					self.hppotimgbtn.config(bg="#49e0e3", image=self.hppotimg_2)
					self.hppotimgbtn.image = self.hppotimg_2
				elif self.pottier == 3:
					self.hppotimgbtn.config(bg="#49e0e3", image=self.hppotimg_3)
					self.hppotimgbtn.image = self.hppotimg_3
			else:
				self.hppot = 0
				self.hppotimgbtn.config(bg="#1f1f1f", image=self.hppotimg_n)
				self.hppotimgbtn.image = self.hppotimg_n
				
	def mppotplz(self, bypass=False):
		#Make sure bot mode is any mode other than monitor and mppot is not already selected.
		if self.botpower and bypass == False:
			sys.stderr.write('These settings cannot be changed until the bot is stopped.\n')
			return
		if self.botmode != 0:
			if self.mppot == 0:
				self.mppot = 1
				if self.pottier == 1:
					self.mppotimgbtn.config(bg="#49e0e3", image=self.mppotimg_1)
					self.mppotimgbtn.image = self.mppotimg_1
				elif self.pottier == 2:
					self.mppotimgbtn.config(bg="#49e0e3", image=self.mppotimg_2)
					self.mppotimgbtn.image = self.mppotimg_2
				elif self.pottier == 3:
					self.mppotimgbtn.config(bg="#49e0e3", image=self.mppotimg_3)
					self.mppotimgbtn.image = self.mppotimg_3
			else:
				self.mppot = 0
				self.mppotimgbtn.config(bg="#1f1f1f", image=self.mppotimg_n)
				self.mppotimgbtn.image = self.mppotimg_n
			
	def monitorplz(self):
		if self.botpower:
			sys.stderr.write('These settings cannot be changed until the bot is stopped.\n')
			return
		if self.botmode != 0:
			self.monimgbtn.config(bg="#49e0e3", image=self.monimg_active)
			self.monimgbtn.image = self.monimg_active
			self.botmode = 0
			self.huntimgbtn.config(bg='#1f1f1f', image=self.huntimg_disabled)
			self.huntimgbtn.image = self.huntimg_disabled
			self.farmimgbtn.config(bg='#1f1f1f', image=self.farmimg_disabled)
			self.farmimgbtn.image = self.farmimg_disabled
			self.skillimgbtn.config(bg='#1f1f1f', image=self.skillimg_disabled)
			self.skillimgbtn.image = self.skillimg_disabled
			
			self.weapon = 0
			self.hppot = 0
			self.mppot = 0
			self.swordimgbtn.config(bg='#1f1f1f', image=self.swordimg_n)
			self.swordimgbtn.image = self.swordimg_n
			self.bowimgbtn.config(bg='#1f1f1f', image=self.bowimg_n)
			self.bowimgbtn.image = self.bowimg_n
			self.wandimgbtn.config(bg='#1f1f1f', image=self.wandimg_n)
			self.wandimgbtn.image = self.wandimg_n
			self.mppotimgbtn.config(bg="#1f1f1f", image=self.mppotimg_n)
			self.mppotimgbtn.image = self.mppotimg_n
			self.hppotimgbtn.config(bg="#1f1f1f", image=self.hppotimg_n)
			self.hppotimgbtn.image = self.hppotimg_n
			
		
	def hunterplz(self):
		if self.botpower:
			sys.stderr.write('These settings cannot be changed until the bot is stopped.\n')
			return
		if self.botmode != 1:
			self.huntimgbtn.config(bg="#49e0e3", image=self.huntimg_active)
			self.huntimgbtn.image = self.huntimg_active
			self.botmode = 1
			self.monimgbtn.config(bg='#1f1f1f', image=self.monimg_disabled)
			self.monimgbtn.image = self.monimg_disabled
			self.farmimgbtn.config(bg='#1f1f1f', image=self.farmimg_disabled)
			self.farmimgbtn.image = self.farmimg_disabled
			self.skillimgbtn.config(bg='#1f1f1f', image=self.skillimg_disabled)
			self.skillimgbtn.image = self.skillimg_disabled
			
			self.weapon = 1
			self.hppot = 0
			self.mppot = 0
			self.swordplz()
			self.hppotplz()
			self.mppotplz()
		
	def farmerplz(self):
		if self.botpower:
			sys.stderr.write('These settings cannot be changed until the bot is stopped.\n')
			return
		if self.botmode != 2:
			self.farmimgbtn.config(bg="#49e0e3", image=self.farmimg_active)
			self.farmimgbtn.image = self.farmimg_active
			self.botmode = 2
			self.monimgbtn.config(bg='#1f1f1f', image=self.monimg_disabled)
			self.monimgbtn.image = self.monimg_disabled
			self.huntimgbtn.config(bg='#1f1f1f', image=self.huntimg_disabled)
			self.huntimgbtn.image = self.huntimg_disabled
			self.skillimgbtn.config(bg='#1f1f1f', image=self.skillimg_disabled)
			self.skillimgbtn.image = self.skillimg_disabled
			
			self.weapon = 1
			self.hppot = 0
			self.mppot = 0
			self.swordplz()
			self.hppotplz()
			self.mppotplz()
		
	def skillerplz(self):
		if self.botpower:
			sys.stderr.write('These settings cannot be changed until the bot is stopped.\n')
			return
		if self.botmode != 3:
			self.skillimgbtn.config(bg="#49e0e3", image=self.skillimg_active)
			self.skillimgbtn.image = self.skillimg_active
			self.botmode = 3
			self.monimgbtn.config(bg='#1f1f1f', image=self.monimg_disabled)
			self.monimgbtn.image = self.monimg_disabled
			self.huntimgbtn.config(bg='#1f1f1f', image=self.huntimg_disabled)
			self.huntimgbtn.image = self.huntimg_disabled
			self.farmimgbtn.config(bg='#1f1f1f', image=self.farmimg_disabled)
			self.farmimgbtn.image = self.farmimg_disabled
			
			self.weapon = 1
			self.hppot = 0
			self.mppot = 0
			self.swordplz()
			self.hppotplz()
			self.mppotplz()
	
	def start_bot(self):
		# First check if we have admin privileges...
		if ctypes.windll.shell32.IsUserAnAdmin() == 0:
			sys.stderr.write("Please restart Rucoy Bot with Administrator privileges!!!\n")
			self.startbtn.config(bg='#969696', state='disabled', relief='flat')
		elif self.botpower == True:
			sys.stderr.write("You've already started a bot!\n")
		else:
			self.qu = StdoutQueue()
			if self.servjson == 'failed':
				sys.stderr.write('\nError: please relaunch Rucoy Bot and check your internet connection.\n')
				return
			
			# Check for more than one valid ADB connection.
			devlist = adb.devicelist()
			if devlist[0] == '':
				set_x = self.winfo_toplevel().winfo_rootx()
				set_y = self.winfo_toplevel().winfo_rooty()
				
				alert_msg = """No emulator or device has been detected. Please click the button with the phone icon to manually connect to a device.\n\nNote: MEmu is the recommended emulator for Rucoy Bot."""
				
				alert = MsgBox("No Emulator Detected", alert_msg, 5, set_x, set_y)
				return
			elif len(devlist) > 1 and self.devserial == '':
				set_x = self.winfo_toplevel().winfo_rootx()
				set_y = self.winfo_toplevel().winfo_rooty()
				
				alert_msg = """Multiple emulators or devices have been detected. Please click the button with the phone icon to choose or manually connect to a device.\n\nNote: MEmu is the recommended emulator for Rucoy Bot."""
				
				alert = MsgBox("No Emulator Selected", alert_msg, 5, set_x, set_y)
				return
			elif len(devlist) == 1:
				# only one emulator present
				self.devserial = devlist[0]
			else:
				pass
			
			pqueue = Queue()
			self.botq = Queue()
			botprintq = Queue()
			if self.botmode == 0:
				mode = 'monitor'
			elif self.botmode == 1:
				mode = 'hunt'
			elif self.botmode == 2:
				mode = 'farm'
			else:
				mode = 'skill'
			if self.weapon == 0:
				botatk = 'melee'
			elif self.weapon == 1:
				botatk = 'dist'
			else:
				botatk = 'mage'
			# Set botspecial and botpottime in settings popup
			#botspecial = False
			#botpottime = '80,80,0'
			if self.hppot == 0 and self.mppot == 0:
				botusepots = False
			else:
				botusepots = True
			if self.resolve_var == 0:
				resolve_levels = False
			else:
				resolve_levels = True
			if self.upload_var == 0:
				upload_data = False
			else:
				upload_data = True
			if self.email_notifications == 0:
				pm_notifications = False
				pm_notify_email = ""
			else:
				pm_notifications = True
				pm_notify_email = self.to_email
			if self.atkok_var == 1:
				atkok = self.atkok_name
			else:
				atkok = ''
			#Resolve server name ie. Europe 1 to 'EU' and '1' for adb
			if self.server_options.get() == 'Any Server':
				self.ipaddr = '0.0.0.0'
				region = '0'
				servnum = '0'
				self.bot_start_time = time()
			else:
				for a in self.servjson.get('servers'):
					if self.server_options.get().startswith(a.get('name')):
						self.ipaddr = a.get('ip')
						self.ipname = a.get('name')
				
				if self.ipname[:13] == "North America":
					region = 'NA'
					servnum = int(self.ipname[14:15])
				elif self.ipname[:13] == "South America":
					region = 'SA'
					servnum = int(self.ipname[14:15])
				elif self.ipname[:6] == "Europe":
					region = 'EU'
					servnum = int(self.ipname[7:8])
				else:
					region = 'AS'
					servnum = int(self.ipname[5:6])
				self.bot_start_time = time()+11
			#start mitm and translator
			self.p = Process(target=mitm.listener, args=(self.good_option, self.qu, self.ipaddr, self.hours, pqueue, self.botq, mode, botprintq, resolve_levels, pm_notifications, pm_notify_email, upload_data, region, servnum, self.filters, self.devserial, self.devratio, atkok,))
			self.p.daemon = True
			self.p.start()
			if mode != 'monitor':
				self.b = Process(target=bot.quecatcher, args=(self.botq,mode,botprintq,botatk,self.botspecial,botusepots,self.botpottime,self.devserial,self.devratio,self.ipaddr,))
				#self.b.daemon = True
				self.b.start()
			self.nh = Process(target=helper, args=(pqueue,self.qu,))
			self.nh.daemon = True
			self.nh.start()
			adb.setserial(self.devserial)
			adb.setratio(self.devratio)
			adb.restartrucoy()
			
			self.botpower = True
			
			self.text_catcher()
			self.startbtn.config(bg='#61bd5c', relief='sunken')
			self.stopbtn.config(bg='#ffa8ab', relief='raised')
			s = str(float(self.text.index("insert"))-4)
			print("\n#!--Starting Now--!#")
			highlight_update(self.text, start=s)

	def quit_bot(self, popup='yes'):
		#Quit processes called in start_bot
		if self.botpower == True:
			self.p.terminate()
			try:
				if self.botmode != 0:
					self.botq.put('bye|bye')
					sleep(1)
					self.b.terminate()
					self.botpower = False
					if popup == 'yes':
						self.bot_stop_time = time()
						adb.setserial(self.devserial)
						adb.setratio(self.devratio)
						adb.tapsettings()
						adb.tapsettings_stats()
						adb.pullscreenshot('stop{}.png'.format(self.ipaddr))
						adb.tapclose()
						#uncomment this to make the rucoy app close when the bot is stopped.
						#adb.closerucoy()
						set_x = self.winfo_toplevel().winfo_rootx()
						set_y = self.winfo_toplevel().winfo_rooty()
						
						self.xpchange = int(self.xpvar.get().replace(',', '')) - self.xpvar_start
						self.meleechange = int(self.meleevar.get().replace(',', '')) - self.meleevar_start
						self.distchange = int(self.distvar.get().replace(',', '')) - self.distvar_start
						self.magechange = int(self.magevar.get().replace(',', '')) - self.magevar_start
						self.defchange = int(self.defvar.get().replace(',', '')) - self.defvar_start
						self.goldchange = int(self.goldvar.get().replace(',', '')) - self.goldvar_start
						
						self.xpvar.set(' 0 ')
						self.meleevar.set(' 0 ')
						self.distvar.set(' 0 ')
						self.magevar.set(' 0 ')
						self.defvar.set(' 0 ')
						self.goldvar.set(' 0 ')
						self.botname.set(' ')
						show_stats = StatBox(self, set_x, set_y)
						show_stats.wait_window()
						self.focus()
			except:
				pass
			self.nh.terminate()
			#self.monitor.do_run = False
			if self.switchvar.get() == 1:
				self.server_adb.do_run = False
			self.startbtn.config(bg='#c7ffb5', relief='raised')
			self.stopbtn.config(bg='#f73e47', relief='sunken')
			sys.stderr.write("\nRucoy Bot has stopped running.\n")
			self.botpower = False
		else:
			sys.stderr.write("Rucoy Bot was never started.\n")
	
	def expandplz(self):
		set_x = self.winfo_toplevel().winfo_rootx()
		set_y = self.winfo_toplevel().winfo_rooty()
		
		self.expandbtn.grid_remove()
		self.expandbtn.config(state='disabled')
		
		showconsole = ConsoleBox(self, "Console", set_x, set_y)
	
	def viewplz(self):
		if self.text_visible:
			self.text.grid_remove()
			self.scroll.grid_remove()
			self.winfo_toplevel().geometry("765x630")
			self.viewbtn.config(bg='#1f1f1f', image=self.view_img)
			self.viewbtn.image = self.view_img
			self.text_visible = False
		else:
			self.text.grid(row=21, column=0, columnspan=3, padx=(25, 0), sticky='e')
			self.scroll.grid(row=21, column=3, padx=(0, 30), sticky='nws')
			self.winfo_toplevel().geometry("785x730")
			self.viewbtn.config(bg='#1f1f1f', image=self.view_imgd)
			self.viewbtn.image = self.view_imgd
			self.text_visible = True

	def on_closing(self):
		set_x = self.winfo_toplevel().winfo_rootx()
		set_y = self.winfo_toplevel().winfo_rooty()
		
		close_msg = """\n  Are you sure you would like to quit?\n"""
		
		self.close = True
		closeask = AskBox(self, "Quit Program", close_msg, 3, set_x, set_y)
		closeask.wait_window()
		if self.close == True:
			try:
				self.p.terminate()
				self.nh.terminate()
				self.server_adb.do_run = False
				self.botq.put('bye|bye')
				sleep(1)
				self.b.terminate()
				os.remove('start{}.png'.format(self.ipaddr))
				os.remove('stop{}.png'.format(self.ipaddr))
			except:
				pass
			finally:
				app.destroy()

class MsgBox(tk.Toplevel):

	def __init__(self, title="MsgBox", message="Hello World", set_height=10, set_x=0, set_y=0):
		tk.Toplevel.__init__(self)
		self.withdraw()
		self.title("Rucoy Bot - " + title)
		self.iconbitmap('robot.ico')
		self.configure(background="black")
		self.resizable(False, False)
		
		center_x = self.winfo_toplevel().winfo_width()
		center_x = int(center_x /2)
		center_x = 225 - center_x
		
		self.geometry("+{}+{}".format(set_x+center_x, set_y+5))
		
		self.textbox = tk.Text(self, width=60, wrap="word")
		self.textbox.config(bg="#1f1f1f", fg='#57cade')
		self.textbox.insert("end", message)
		self.textbox.configure(state='disabled')
		self.textbox.grid(row=0, column=0, padx=(25, 25), pady=(25, 0))
		self.textbox.config(height=set_height)

		self.button = tk.Button(self, cursor='hand2', text=" OK ", bg='#c7ffb5')
		self.button['command'] = self.destroy
		self.button.grid(row=1, column=0, padx=(25, 75), pady=(25, 25), sticky='e')
		self.button.focus()
		self.deiconify()

class AskBox(tk.Toplevel):

	def __init__(self, master, title="AskBox", message="Hello World", set_height=10, set_x=0, set_y=0):
		tk.Toplevel.__init__(self, master)
		self.withdraw()
		self.master = master
		
		self.title("Rucoy Bot - " + title)
		self.iconbitmap('robot.ico')
		self.configure(background="black")
		self.resizable(False, False)
		
		center_x = self.winfo_toplevel().winfo_width()
		center_x = int(center_x /2)
		center_x = 300 - center_x
		
		self.geometry("+{}+{}".format(set_x+center_x, set_y+5))
		
		self.textbox = tk.Text(self, width=40, wrap="word")
		self.textbox.config(bg="#1f1f1f", fg='#57cade')
		self.textbox.insert("end", message)
		self.textbox.configure(state='disabled')
		self.textbox.grid(row=0, column=0, padx=(25, 25), pady=(25, 0))
		self.textbox.config(height=set_height)

		self.button = tk.Button(self, cursor='hand2', text="   OK   ", bg='#c7ffb5')
		self.button['command'] = self.okbutton
		self.button.grid(row=1, column=0, padx=(25, 150), pady=(25, 25), sticky='e')
		
		self.button.focus()
		
		self.button2 = tk.Button(self, cursor='hand2', text=" Cancel ", bg='#f73e47')
		self.button2['command'] = self.nobutton
		self.button2.grid(row=1, column=0, padx=(25, 75), pady=(25, 25), sticky='e')
		self.deiconify()
	def okbutton(self):
		self.master.close = True
		self.destroy()
	def nobutton(self):
		self.master.close = False
		self.destroy()

class ValueBox(tk.Toplevel):

	def __init__(self, master, title="ValueBox", message="Hello World", set_height=10, set_x=0, set_y=0):
		tk.Toplevel.__init__(self, master)
		self.withdraw()
		self.master = master
		
		self.topx = set_x
		self.topy = set_y
		
		self.title("Rucoy Bot - " + title)
		self.iconbitmap('robot.ico')
		self.configure(background="black")
		self.protocol("WM_DELETE_WINDOW", self.nobutton)
		self.resizable(False, False)
		
		center_x = self.winfo_toplevel().winfo_width()
		center_x = int(center_x /2)
		center_x = 300 - center_x
		
		self.geometry("+{}+{}".format(set_x+center_x, set_y+5))
		
		self.textbox = tk.Text(self, width=40, wrap="word")
		self.textbox.config(bg="#1f1f1f", fg='#57cade')
		self.textbox.insert("end", message)
		self.textbox.configure(state='disabled')
		self.textbox.grid(row=0, column=0, padx=(25, 25), pady=(25, 0))
		self.textbox.config(height=set_height)
		
		self.hourent = tk.Entry(self, bg="#1f1f1f", fg='white', insertbackground='white')
		self.hourent.grid(row=1, column=0, padx=(25, 25), pady=(25, 0), sticky='e')
		self.hourent.focus_set()

		self.button = tk.Button(self, cursor='hand2', text="   OK   ", bg='#c7ffb5')
		self.button['command'] = self.okbutton
		self.button.grid(row=2, column=0, padx=(25, 150), pady=(25, 25), sticky='e')
		self.button.focus()
		
		self.bind('<Return>', self.retbutton)
		
		self.button2 = tk.Button(self, cursor='hand2', text=" Cancel ", bg='#f73e47')
		self.button2['command'] = self.nobutton
		self.button2.grid(row=2, column=0, padx=(25, 75), pady=(25, 25), sticky='e')
		self.deiconify()
	def okbutton(self):
		try:
			self.master.hours = int(self.hourent.get())
			if self.master.hours < 13 or self.master.hours > 255:
				raise Exception('dummy...')
			self.destroy()
		except:
			error_msg = """Please enter a valid number for hours between 13 and 255."""
			
			errormsg = MsgBox("Error", error_msg, 2, self.topx, self.topy)
	def nobutton(self):
		self.master.hours = 0
		self.master.storevar.set(0)
		self.destroy()
	def retbutton(self, event):
		self.okbutton()

class SettingsBox(tk.Toplevel):
	def __init__(self, master, title="SettingsBox", set_height=10, set_x=0, set_y=0):
		tk.Toplevel.__init__(self, master)
		self.withdraw()
		self.master = master
		
		self.topx = set_x
		self.topy = set_y
		
		self.title("Rucoy Bot - " + title)
		self.iconbitmap('robot.ico')
		self.configure(background="black")
		self.protocol("WM_DELETE_WINDOW", self.nobutton)
		self.resizable(False, False)
		
		center_x = self.winfo_toplevel().winfo_width()
		center_x = int(center_x /2)
		center_x = 145 - center_x
		
		self.geometry("+{}+{}".format(set_x+center_x, set_y+5))
		
		message = """Please change the below advanced settings if necessary.\n\n* 'Email Me' will send you an email in the event of a direct message while your bot is running.\n* 'Resolve Levels' will show the levels after a player's name in the box showing what messages are sent back and forth.\n* 'Upload pricing data' will upload data to rucoybot.com's database of item pricing.\n* 'Verbose Level' will change how much data will be shown. This shown only ever be changed if you are reporting an issue.\n* 'HP & MP Potion Threshold' will change how soon the bot chooses to use a HP or MP potions. For example, 80 means the bot will take a hp potion once HP is 80% or less of the max HP.\n* 'Use Special' will enable the use of special attacks while botting.\n'Only Attack' will only attack monsters whose name includes what you type in, ex. 'Skeleton'."""
		
		self.textbox = tk.Text(self, width=80, wrap="word")
		self.textbox.config(bg="#1f1f1f", fg='#57cade')
		self.textbox.insert("end", message)
		self.textbox.configure(state='disabled')
		self.textbox.grid(row=0, column=0, columnspan=2, padx=(20, 20), pady=(20, 30))
		self.textbox.config(height=set_height)
		
		#Below are the option widgets...
		#Email label and input widgets
		self.emaillbl = tk.Label(self, text=" Email Me ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.emaillbl.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky='w')
		self.sendemails = tk.IntVar()
		self.sendemails.set(self.master.email_notifications)
		self.e_chkbox = Slider(self, text="", variable=self.sendemails, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.e_chkbox.grid(row=2, column=0, padx=(0, 200), pady=(10, 10), sticky='e')
		self.email_address = tk.StringVar()
		self.email_address.set(self.master.to_email)
		self.emailent = tk.Entry(self, bg="#1f1f1f", fg='white', textvariable=self.email_address, width=27, insertbackground='white')
		self.emailent.grid(row=2, column=0, padx=(10, 20), pady=(10, 10), sticky='e')
		
		#Verbose label 
		self.verboselbl = tk.Label(self, text=" Verbose Level ", bg="#1f1f1f", fg='#57cade', relief='groove')
		self.verboselbl.grid(row=2, column=1, padx=(20, 150), pady=(10, 10), sticky='w')
		#Verbose Dropdown
		self.verbose_option = tk.StringVar()
		self.all_verboselvls = ["Default", "Default + Raw", "Everything", "Everything + Raw"]
		self.verbose_option.set(self.all_verboselvls[self.master.good_option-1])
		self.verboptdd = tk.OptionMenu(self, self.verbose_option, *self.all_verboselvls)
		verboptddfont = Font(size=6)
		self.verboptdd.config(bg='#1f1f1f', fg='#57cade', font=verboptddfont, width=20)
		self.verboptdd['menu'].config(bg='#1f1f1f', fg='#57cade')
		self.verboptdd['highlightthickness'] = 0
		self.verboptdd.grid(row=2, column=1, padx=(10, 20), pady=(10, 10), sticky='e')
		
		#Resolve label and checkbox
		self.resolvelbl = tk.Label(self, text=" Resolve Levels ", bg="#1f1f1f", fg='#57cade', relief='groove')
		self.resolvelbl.grid(row=3, column=0, padx=(20, 20), pady=(10, 10), sticky='w')
		self.resolvelvls = tk.IntVar()
		self.resolvelvls.set(self.master.resolve_var)
		self.r_chkbox = Slider(self, text="", variable=self.resolvelvls, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.r_chkbox.grid(row=3, column=0, padx=(10, 20), pady=(10, 10), sticky='e')
		
		#Upload label and checkbox
		self.uploadlbl = tk.Label(self, text=" Upload Pricing Data ", bg="#1f1f1f", fg='#57cade', relief='groove')
		self.uploadlbl.grid(row=4, column=0, padx=(20, 20), pady=(10, 10), sticky='w')
		self.uploaddata = tk.IntVar()
		self.uploaddata.set(self.master.upload_var)
		self.u_chkbox = Slider(self, text="", variable=self.uploaddata, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.u_chkbox.grid(row=4, column=0, padx=(10, 20), pady=(10, 10), sticky='e')
		
		#Hp Threshold Label
		self.hptlbl = tk.Label(self, text=" HP Potion Threshold ", bg="#1f1f1f", fg='#57cade', relief='groove')
		self.hptlbl.grid(row=3, column=1, padx=(20, 20), pady=(10, 10), sticky='w')
		#Hp threshold value entry
		self.hpdef = tk.StringVar()
		self.hpdef.set(self.master.botpottime.split(',')[0])
		self.hpent = tk.Entry(self, textvariable=self.hpdef, bg="#1f1f1f", fg='white', width=3, insertbackground='white')
		self.hpent.grid(row=3, column=1, padx=(10, 20), pady=(10, 10), sticky='e')
		
		#Mp Threshold Label
		self.mptlbl = tk.Label(self, text=" MP Potion Threshold ", bg="#1f1f1f", fg='#57cade', relief='groove')
		self.mptlbl.grid(row=4, column=1, padx=(20, 20), pady=(10, 10), sticky='w')
		#Mp threshold value entry
		self.mpdef = tk.StringVar()
		self.mpdef.set(self.master.botpottime.split(',')[1])
		self.mpent = tk.Entry(self, textvariable=self.mpdef, bg="#1f1f1f", fg='white', width=3, insertbackground='white')
		self.mpent.grid(row=4, column=1, padx=(10, 20), pady=(10, 10), sticky='e')
		
		#Special attack label and checkbox
		self.speciallbl = tk.Label(self, text=" Use Special ", bg="#1f1f1f", fg='#57cade', relief='groove')
		self.speciallbl.grid(row=5, column=0, padx=(20, 20), pady=(10, 10), sticky='w')
		self.specialvar = tk.IntVar()
		if self.master.botspecial:
			self.specialvar.set(1)
		else:
			self.specialvar.set(0)
		self.s_chkbox = Slider(self, text="", variable=self.specialvar, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.s_chkbox.grid(row=5, column=0, padx=(10, 20), pady=(10, 10), sticky='e')
		
		#Attack monster with user provided name label and checkbox
		self.atkoklbl = tk.Label(self, text=" Only Attack ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.atkoklbl.grid(row=5, column=1, padx=(20, 10), pady=(10, 10), sticky='w')
		self.atkokvar = tk.IntVar()
		self.atkokvar.set(self.master.atkok_var)
		self.atk_chkbox = Slider(self, text="", variable=self.atkokvar, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.atk_chkbox.grid(row=5, column=1, padx=(0, 130), pady=(10, 10), sticky='e')
		#Attack monster entry box
		self.atkokname = tk.StringVar()
		self.atkokname.set(self.master.atkok_name)
		self.atkokent = tk.Entry(self, bg="#1f1f1f", fg='white', textvariable=self.atkokname, width=15, insertbackground='white')
		self.atkokent.grid(row=5, column=1, padx=(10, 20), pady=(10, 10), sticky='e')
		
		self.button = tk.Button(self, cursor='hand2', text=" Save ", bg='#c7ffb5')
		self.button['command'] = self.okbutton
		self.button.grid(row=10, column=0, columnspan=2, padx=(25, 225), pady=(25, 25), sticky='e')
		self.button.focus()
		
		self.bind('<Return>', self.retbutton)
		
		self.button2 = tk.Button(self, cursor='hand2', text=" Cancel ", bg='#f73e47')
		self.button2['command'] = self.nobutton
		self.button2.grid(row=10, column=0, columnspan=2, padx=(25, 150), pady=(25, 25), sticky='e')
		self.deiconify()
	def okbutton(self):
		try:
			#self.master.hours = int(self.hourent.get())
			regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
			if self.sendemails.get() == 1:
				if not (re.search(regex, self.email_address.get())):  
					raise Exception('invalid email')
			self.master.atkok_var = self.atkokvar.get()
			self.master.atkok_name = self.atkokname.get()
			self.master.email_notifications = self.sendemails.get()
			self.master.to_email = self.email_address.get()
			self.master.upload_var = self.uploaddata.get()
			self.master.resolve_var = self.resolvelvls.get()
			for option in self.all_verboselvls:
				if option == self.verbose_option.get():
					self.master.good_option = self.all_verboselvls.index(option)+1
			hptime = int(self.hpdef.get())
			mptime = int(self.mpdef.get())
			if hptime > 100 or hptime < 1:
				raise Exception('hpmp')
			if mptime > 100 or mptime < 1:
				raise Exception('hpmp')
			pottime = "{},{},0".format(hptime, mptime)
			self.master.botpottime = pottime
			if self.specialvar.get() == 0:
				self.master.botspecial = False
			else:
				self.master.botspecial = True
			if self.master.botpower:
				warning_msg = """\nThese settings will not be applied til the bot is restarted.\n"""
				warn_msg = MsgBox("Heads Up", warning_msg, 3, self.topx, self.topy)
				warn_msg.wait_window()
			self.destroy()
		except Exception as e:
			if e.args[0] == 'invalid email':
				error_msg = """Please enter in a valid email address. Thank you."""
			else:
				error_msg = """Please enter a valid number for the HP and MP potion threshhold. {}""".format(e.args)
			
			errormsg = MsgBox("Error", error_msg, 2, self.topx, self.topy)
	def nobutton(self):
		self.destroy()
	def retbutton(self, event):
		self.okbutton()

class PicBox(tk.Toplevel):
	def __init__(self, imagename, set_x=0, set_y=0):
		try:
			tk.Toplevel.__init__(self)
			self.withdraw()
			if imagename.startswith('start'):
				self.title("Rucoy Bot - Start Screenshot")
			else:
				self.title("Rucoy Bot - Stop Screenshot")
			self.iconbitmap('robot.ico')
			self.configure(background="black")
			self.resizable(False, False)
			self.minsize(200, 100)
			
			center_x = self.winfo_toplevel().winfo_width()
			center_x = int(center_x /2)
			center_x = 105 - center_x
			
			self.geometry("+{}+{}".format(set_x+center_x, set_y+5))
			
			
			img = ImageTk.PhotoImage(Image.open(imagename).resize((640, 360)))
			imglbl = tk.Label(self, image=img)
			imglbl.image = img
			imglbl.grid(row=0, column=0, padx=(25, 25), pady=(25, 25), sticky='nesw')
			
			self.deiconify()
		except:
			pass

class StatBox(tk.Toplevel):
	def __init__(self, master, set_x=0, set_y=0):
		try:
			tk.Toplevel.__init__(self)
			self.withdraw()
			self.master = master
			self.protocol("WM_DELETE_WINDOW", self.on_exit)
			
			xpc = self.master.xpchange
			meleec = self.master.meleechange
			distc = self.master.distchange
			magec = self.master.magechange
			defc = self.master.defchange
			goldc = self.master.goldchange
			
			adb = rucoyadb.AdbLib()
			
			if xpc == 0 and meleec == 0 and distc == 0 and magec == 0 and defc == 0 and goldc == 0:
				os.remove('start{}.png'.format(self.master.ipaddr))
				os.remove('stop{}.png'.format(self.master.ipaddr))
				self.destroy()
			
			xpreport = self.xp_report(xpc, meleec, distc, magec, defc, goldc)
			timereport = self.time_report(self.master.bot_start_time, self.master.bot_stop_time)
			efficiencyreport = self.efficiency_report(meleec, distc, magec, defc, self.master.bot_start_time, self.master.bot_stop_time)
			
			self.title("Rucoy Bot - Stat Progress")
			self.iconbitmap('robot.ico')
			self.configure(background="black")
			self.resizable(False, False)
			
			center_x = self.winfo_toplevel().winfo_width()
			center_x = int(center_x /2)
			center_x = 225 - center_x
			
			self.geometry("+{}+{}".format(set_x+center_x, set_y+5))
			
			message = """Thanks for using Rucoy Bot! \n\nHere is a before and after screenshot of your stats to show how much progress you made.\n\n{}\n\nThis bot ran for {}\n\n{}""".format(xpreport, timereport, efficiencyreport)
			self.textbox = tk.Text(self, width=60, wrap="word")
			self.textbox.config(bg="#1f1f1f", fg='#57cade')
			self.textbox.insert("end", message)
			self.textbox.configure(state='disabled')
			self.textbox.grid(row=0, column=0, padx=(25, 25), pady=(25, 10))
			h = 10
			if len(xpreport) > 120:
				h += 2
			if len(xpreport) > 60:
				h += 1
			if len(timereport) > 120:
				h += 2
			if len(timereport) > 60:
				h += 1
			if len(efficiencyreport) > 120:
				h += 2
			if len(efficiencyreport) > 60:
				h += 1
			
			self.textbox.config(height=h)
			
			self.start_lbl = tk.Label(self, text="Start Screenshot", bg="black", fg='#57cade')
			self.start_lbl.grid(row=1, column=0, padx=(20, 20), pady=(15, 0), sticky='s')
			
			self.expand_img = ImageTk.PhotoImage(Image.open("maximize.png").resize((10, 10)))
			self.expandbtn = tk.Button(self, cursor='hand2', image=self.expand_img, bg='#1f1f1f', command=self.bigstartplz)
			self.expandbtn.image = self.expand_img
			self.expandbtn.grid(row=1, column=0, padx=(5, 190), pady=(15, 0), sticky='e')
			
			try:
				img = ImageTk.PhotoImage(Image.open('start{}.png'.format(self.master.ipaddr)).resize((330, 180)))
				img2 = ImageTk.PhotoImage(Image.open('stop{}.png'.format(self.master.ipaddr)).resize((330, 180)))
			except:
				#Failed to open images so just fail quietly
				self.destroy()
			
			imglbl = tk.Label(self, image=img)
			imglbl.image = img
			imglbl.grid(row=5, column=0, padx=(25, 25), pady=(0, 10))
			
			self.stop_lbl = tk.Label(self, text="Stop Screenshot", bg="black", fg='#57cade')
			self.stop_lbl.grid(row=6, column=0, padx=(20, 20), pady=(15, 0), sticky='s')
			
			self.expand_img2 = ImageTk.PhotoImage(Image.open("maximize.png").resize((10, 10)))
			self.expandbtn2 = tk.Button(self, cursor='hand2', image=self.expand_img2, bg='#1f1f1f', command=self.bigstopplz)
			self.expandbtn2.image = self.expand_img2
			self.expandbtn2.grid(row=6, column=0, padx=(5, 190), pady=(15, 0), sticky='e')
			
			imglbl2 = tk.Label(self, image=img2)
			imglbl2.image = img2
			imglbl2.grid(row=10, column=0, padx=(25, 25), pady=(0, 10))
			
			self.button = tk.Button(self, cursor='hand2', text="  OK  ", bg='#c7ffb5')
			self.button['command'] = self.destroy
			self.button.grid(row=11, column=0, padx=(25, 150), pady=(25, 25), sticky='e')
			self.button.focus()
			
			self.deiconify()
			
			self.master.xpvar_start = 0
			self.master.meleevar_start = 0
			self.master.distvar_start = 0
			self.master.magevar_start = 0
			self.master.defvar_start = 0
			self.master.goldvar_start = 0
		except Exception as e:
			pass
			#print('statbox init failed - {}'.format(e))
	
	def on_exit(self):
		os.remove('start{}.png'.format(self.master.ipaddr))
		os.remove('stop{}.png'.format(self.master.ipaddr))
		self.destroy()
	
	def bigstartplz(self):
		img_name = 'start{}.png'.format(self.master.ipaddr)
		
		set_x = self.winfo_toplevel().winfo_rootx()
		set_y = self.winfo_toplevel().winfo_rooty()
		
		_ = PicBox(img_name, set_x, set_y)
	
	def bigstopplz(self):
		img_name = 'stop{}.png'.format(self.master.ipaddr)
		
		set_x = self.winfo_toplevel().winfo_rootx()
		set_y = self.winfo_toplevel().winfo_rooty()
		
		_ = PicBox(img_name, set_x, set_y)
	
	def efficiency_report(self, meleec, distc, magec, defc, start, stop):
		seconds = int(stop - start)
		
		changed_count = 0
		added = 0
		returnme = 'This botting session ran with an efficiency of '
		
		if meleec != 0:
			changed_count += 1
		if distc != 0:
			changed_count += 1
		if magec != 0:
			changed_count += 1
		if defc != 0:
			changed_count += 1
		
		if meleec != 0:
			melee_eff = meleec / seconds
			returnme += '{:.0%} for Melee'.format(melee_eff)
			if distc == 0 and magec == 0 and defc == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		if distc != 0:
			dist_eff = distc / seconds
			returnme += '{:.0%} for Distance'.format(dist_eff)
			if meleec == 0 and magec == 0 and defc == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		if magec != 0:
			mage_eff = magec / seconds
			returnme += '{:.0%} for Mage'.format(mage_eff)
			if meleec == 0 and distc == 0 and defc == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		if defc != 0:
			def_eff = defc / seconds
			returnme += '{:.0%} for Defense'.format(def_eff)
			if meleec == 0 and magec == 0 and distc == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		
		return returnme
	
	def time_report(self, start, stop):
		change = int(stop - start)
		days = change // 86400
		left = change % 86400
		hours = left // 3600
		left = left % 3600
		minutes = left // 60
		seconds = left % 60
		
		changed_count = 0
		added = 0
		returnme = ''
		if days != 0:
			changed_count += 1
		if hours != 0:
			changed_count += 1
		if minutes != 0:
			changed_count += 1
		if seconds != 0:
			changed_count += 1
		
		if days != 0:
			returnme += '{:,d} days'.format(days)
			if hours == 0 and minutes == 0 and seconds == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		if hours != 0:
			returnme += '{:,d} hours'.format(hours)
			if days == 0 and minutes == 0 and seconds == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		if minutes != 0:
			returnme += '{:,d} minutes'.format(minutes)
			if hours == 0 and days == 0 and seconds == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		if seconds != 0:
			returnme += '{:,d} seconds'.format(seconds)
			if hours == 0 and minutes == 0 and days == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		
		return returnme
	
	def xp_report(self, xpc, meleec, distc, magec, defc, goldc):
		returnme = 'You gained '
		changed_count = 0
		added = 0
		if xpc != 0:
			changed_count += 1
		if meleec != 0:
			changed_count += 1
		if distc != 0:
			changed_count += 1
		if magec != 0:
			changed_count += 1
		if defc != 0:
			changed_count += 1
		if goldc != 0:
			changed_count += 1
		if xpc != 0:
			returnme += '{:,d} XP'.format(xpc)
			if meleec == 0 and distc == 0 and magec == 0 and defc == 0 and goldc == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		if meleec != 0:
			returnme += '{:,d} Melee XP'.format(meleec)
			if xpc == 0 and distc == 0 and magec == 0 and defc == 0 and goldc == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		if distc != 0:
			returnme += '{:,d} Distance XP'.format(distc)
			if xpc == 0 and meleec == 0 and magec == 0 and defc == 0 and goldc == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		if magec != 0:
			returnme += '{:,d} Mage XP'.format(magec)
			if xpc == 0 and distc == 0 and meleec == 0 and defc == 0 and goldc == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		if defc != 0:
			returnme += '{:,d} Defense XP'.format(defc)
			if xpc == 0 and distc == 0 and magec == 0 and meleec == 0 and goldc == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		if goldc != 0:
			returnme += '{:,d} Gold'.format(goldc)
			if xpc == 0 and distc == 0 and magec == 0 and defc == 0 and meleec == 0:
				returnme += '.'
				return returnme
			else:
				if changed_count == 2 and added == 0:
					returnme += ' and '
				elif changed_count == 2 and added == 1:
					returnme += '.'
					return returnme
				else:
					if added == changed_count-2:
						returnme += ', and '
					elif added == changed_count-1:
						returnme += '.'
					else:
						returnme += ', '
			added += 1
		
		return returnme

class DeviceBox(tk.Toplevel):
	def __init__(self, master, set_x=0, set_y=0):
		tk.Toplevel.__init__(self)
		self.withdraw()
		self.master = master
		
		self.topx = set_x
		self.topy = set_y
		
		self.title("Rucoy Bot - Choose Device")
		self.iconbitmap('robot.ico')
		self.configure(background="black")
		self.resizable(False, False)
		
		center_x = self.winfo_toplevel().winfo_width()
		center_x = int(center_x /2)
		center_x = 225 - center_x
		
		self.geometry("+{}+{}".format(set_x+center_x, set_y+5))
		
		message = """If you have more than one emulator or device attached, please select the correct device below. \n\nHit refresh to reload available devices and grab fresh screenshots. Note: Turn on 1080p Mode for Bluestacks.\n\nIf your device/emulator doesn't show up, type in just the port or ip and port into the Manual Connect box. Ex.- '5555' or '127.0.0.1:5555'"""
		self.textbox = tk.Text(self, width=60, wrap="word")
		self.textbox.config(bg="#1f1f1f", fg='#57cade')
		self.textbox.insert("end", message)
		self.textbox.configure(state='disabled')
		self.textbox.grid(row=0, column=0, columnspan=4, padx=(25, 25), pady=(25, 10))
		self.textbox.config(height=9)
		
		self.reload_img = ImageTk.PhotoImage(Image.open("reload.png").resize((15, 15)))
		self.reloadbtn = tk.Button(self, cursor='hand2', text=" Reload ", image=self.reload_img, bg='#1f1f1f', compound='right', state='disabled')
		self.reloadbtn['command'] = self.reload
		self.reloadbtn.grid(row=1, column=0, columnspan=4, padx=(25, 25), pady=(5, 10))
		
		#Here is where the buttons for each emulator get generated.
		#Show this label for loading and none found messages.
		self.interim_msg = tk.StringVar()
		self.interim_msg.set(" Loading... ")
		self.interimlbl = tk.Label(self, textvariable=self.interim_msg, bg='#1f1f1f', fg='#57cade', relief='groove')
		self.interimlbl.grid(row=95, column=0, columnspan=4, padx=(20, 20), pady=(40, 40))
		
		#Manual Connect Label and Entry
		self.linelbl = tk.Label(self, text='-'*100, bg='black', fg='#1f1f1f')
		self.linelbl.grid(row=96, column=0, columnspan=4, padx=(20, 20), pady=(15, 0))
		
		self.manuallbl = tk.Label(self, text=" Manual Connect to: ", bg='black', fg='#57cade')
		self.manuallbl.grid(row=97, column=0, columnspan=2, padx=(5, 0), pady=(0, 0), sticky='e')
		self.manualent = tk.Entry(self, bg="#1f1f1f", fg='white', width=15, insertbackground='white')
		self.manualent.grid(row=97, column=2, columnspan=2, padx=(0, 5), pady=(0, 0), sticky='w')
		
		self.manual_img = ImageTk.PhotoImage(Image.open("usb-cable.png").resize((15, 15)))
		self.manualbtn = tk.Button(self, cursor='hand2', text=" Connect ", image=self.manual_img, bg='#57cade', compound='right')
		self.manualbtn['command'] = self.connect
		self.manualbtn.grid(row=98, column=0, columnspan=4, pady=(10, 0))
		
		self.line2lbl = tk.Label(self, text='-'*100, bg='black', fg='#1f1f1f')
		self.line2lbl.grid(row=99, column=0, columnspan=4, padx=(20, 20), pady=(0, 0))
		
		self.phonelbl = tk.Label(self, text=" 1080p Mode: ", bg='black', fg='#57cade')
		self.phonelbl.grid(row=101, column=0, columnspan=2, padx=(60, 0), pady=(0, 0), sticky='w')
		
		self.phone = tk.IntVar()
		if self.master.devratio == 1.5:
			self.phone.set(1)
		self.phone_chkbox = Slider(self, text="", variable=self.phone, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.phone_chkbox.grid(row=101, column=0, columnspan=2, padx=(150, 5), pady=(0, 0), sticky='w')
		
		self.button = tk.Button(self, cursor='hand2', text=" Select ", bg='#c7ffb5')
		self.button['command'] = self.okbutton
		self.button.grid(row=101, column=0, columnspan=4, padx=(25, 150), pady=(25, 25), sticky='e')
		self.button.focus()
		
		self.button2 = tk.Button(self, cursor='hand2', text=" Cancel ", bg='#f73e47')
		self.button2['command'] = self.destroy
		self.button2.grid(row=101, column=0, columnspan=4, padx=(25, 75), pady=(25, 25), sticky='e')
		
		self.device_list = ['']
		self.devices = ['']*len(self.device_list)
		self.device_buttons = ['']*len(self.device_list)
		self.device_images = ['']*len(self.device_list)
		self.selected = 0
		
		self.after(500, self.refresh)
		self.deiconify()
	def refresh(self, after='30'):
		self.reloadbtn.config(state='disabled', bg='#1f1f1f')
		
		if self.device_buttons[0] != '' and after != 'on':
			for device_index in range(len(self.device_buttons)):
				self.device_buttons[device_index].grid_remove()
				self.device_buttons[device_index].destroy()
		
		if after == 'on' or after == '30':
			adb = rucoyadb.AdbLib()
			adb.connect('21503')
			adb.connect('5555')
			self.device_list = adb.devicelist()
			self.devices = ['']*len(self.device_list)
			self.device_buttons = ['']*len(self.device_list)
			self.device_images = ['']*len(self.device_list)
		
		if self.selected > len(self.device_list)-1:
			self.selected = 0
		
		if self.device_list[0] != '':
			self.interimlbl.grid_remove()
			for i in range(len(self.device_list)):
				if after == 'on' or after == '30':
					self.devices[i] = rucoyadb.AdbLib(self.device_list[i])
					self.devices[i].pullscreenshot(f'screen{i}.png')
				if i == self.selected:
					self.device_images[i] = ImageTk.PhotoImage(Image.open(f"screen{i}.png").resize((150, 100)))
					checked = "\u2713 " + self.device_list[i]
				else:
					self.device_images[i] = ImageTk.PhotoImage(Image.open(f"screen{i}.png").resize((150, 100)).convert('LA'))
					checked = self.device_list[i]
				self.device_buttons[i] = tk.Button(self, text=checked, image=self.device_images[i], cursor='hand2', fg='white', bg='#1f1f1f', compound='top', command=partial(self.selectme, i))
				if i == self.selected:
					self.device_buttons[i].config(fg='blue', bg='#bababa')
				self.device_buttons[i].image = self.device_images[i]
				if len(self.device_list) > 5:
					m = 4
					c = (i%m)
				elif len(self.device_list) == 1:
					m = 1
					c = 0
				else:
					m = 2
					c = (i%m)*2
				self.device_buttons[i].grid(row=2+int(i/m), column=c, columnspan=int(4/m), padx=(15, 15), pady=(10, 10))
		else:
			self.interim_msg.set(' None Found. ')
			self.interimlbl.config(fg='#f73e47')
		if after == '30':
			self.after(30000, self.refresh)
		self.reloadbtn.config(state='normal', bg='#57cade')
	
	def reload(self):
		if self.device_buttons[0] != '':
			for device_index in range(len(self.device_buttons)):
				self.device_buttons[device_index].grid_remove()
				self.device_buttons[device_index].destroy()
		
		self.interimlbl.config(fg='#57cade')
		self.interim_msg.set(" Loading... ")
		self.interimlbl.grid(row=95, column=0, columnspan=4, padx=(20, 20), pady=(40, 40))
		
		p = partial(self.refresh, 'on')
		p.__name__ = 'p'
		self.after(200, p)
	
	def connect(self):
		addr = self.manualent.get()
		error = ''
		if addr != '':
			if addr.count(':') == 0:
				if addr.isdigit():
					res = adb.connect(addr)
					if 'connected' not in res:
						error = 'fail'
				else:
					error = 'notint'
			elif addr.count('.') == 3:
				adb.connect(addr)
			else:
				error = 'garbage'
		else:
			error = 'empty'
		
		set_x = self.winfo_toplevel().winfo_rootx()
		set_y = self.winfo_toplevel().winfo_rooty()
		if error != '':
			title = "Invalid Entry"
			if error == 'empty':
				alert_msg = """\nPlease enter in a value before you hit connect."""
			elif error == 'notint':
				alert_msg = """\nPlease supply a valid integer for the port number."""
			elif error == 'fail':
				alert_msg = """\nUnfortunately, this device cannot be connected to at this time."""
				title = "Connection Failed"
			else:
				alert_msg = """Please supply a valid port or IP address/port. Ex- '127.0.0.1:5555'"""
		else:
			if addr.count(':') == 0:
				p_addr = addr
			else:
				p_addr = "127.0.0.1:{}".format(addr)
			alert_msg = f"""The device, {p_addr}, has successfully been added to the device list."""
			title = "Connection Successful"
			self.after(400, self.reload)
		alert = MsgBox(title, alert_msg, 3, set_x-126, set_y)
	
	def selectme(self, device_number):
		self.selected = device_number
		self.refresh('off')
	
	def okbutton(self):
		self.master.devserial = self.device_list[self.selected]
		if self.phone.get() == 1:
			self.master.devratio = 1.5
		else:
			self.master.devratio = 1
		if self.master.botpower:
			warning_msg = """\nThese settings will not be applied til the bot is restarted.\n"""
			warn_msg = MsgBox("Heads Up", warning_msg, 3, self.topx, self.topy)
			warn_msg.wait_window()
		self.destroy()

class FilterBox(tk.Toplevel):
	def __init__(self, master, title="Filter Menu", set_x=0, set_y=0):
		tk.Toplevel.__init__(self, master)
		self.withdraw()
		self.master = master
		
		self.topx = set_x
		self.topy = set_y
		
		self.title("Rucoy Bot - " + title)
		self.iconbitmap('robot.ico')
		self.configure(background="black")
		self.protocol("WM_DELETE_WINDOW", self.nobutton)
		self.resizable(False, False)
		
		center_x = self.winfo_toplevel().winfo_width()
		center_x = int(center_x /2)
		center_x = 140 - center_x
		
		self.geometry("+{}+{}".format(set_x+center_x, set_y+5))
		
		message = """\nPlease select which type of messages from Rucoy Online and my Bot you would like to see in the console box. """
		
		self.textbox = tk.Text(self, width=80, wrap="word")
		self.textbox.config(bg="#1f1f1f", fg='#57cade')
		self.textbox.insert("end", message)
		self.textbox.configure(state='disabled')
		self.textbox.grid(row=0, column=0, columnspan=3, padx=(20, 20), pady=(20, 0))
		self.textbox.config(height=4)
		
		self.allonbtn = tk.Button(self, cursor='hand2', text="All On", bg='#57cade')
		self.allonbtn['command'] = self.selectall
		self.allonbtn.grid(row=1, column=1, padx=(55, 0), pady=(15, 5), sticky='w')
		
		self.alloffbtn = tk.Button(self, cursor='hand2', text="All Off", bg='#57cade')
		self.alloffbtn['command'] = self.deselectall
		self.alloffbtn.grid(row=1, column=1, padx=(0, 55), pady=(15, 5), sticky='e')
		
		#Below are the option widgets...
		#Email label and input widgets
		self.msglbl = tk.Label(self, text=" Messages ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.msglbl.grid(row=2, column=0, padx=(20, 20), pady=(10, 10), sticky='w')
		self.seemsg = tk.IntVar()
		if "messages" in self.master.filters:
			self.seemsg.set(1)
		self.msg_chkbox = Slider(self, text="", variable=self.seemsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.msg_chkbox.grid(row=2, column=0, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.dislbl = tk.Label(self, text=" Disconnect ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.dislbl.grid(row=3, column=0, padx=(20, 20), pady=(10, 10), sticky='w')
		self.dismsg = tk.IntVar()
		if "disconnect" in self.master.filters:
			self.dismsg.set(1)
		self.dis_chkbox = Slider(self, text="", variable=self.dismsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.dis_chkbox.grid(row=3, column=0, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.atklbl = tk.Label(self, text=" Attack ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.atklbl.grid(row=4, column=0, padx=(20, 20), pady=(10, 10), sticky='w')
		self.atkmsg = tk.IntVar()
		if "attack" in self.master.filters:
			self.atkmsg.set(1)
		self.atk_chkbox = Slider(self, text="", variable=self.atkmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.atk_chkbox.grid(row=4, column=0, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.hpmplbl = tk.Label(self, text=" HP/MP ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.hpmplbl.grid(row=5, column=0, padx=(20, 20), pady=(10, 10), sticky='w')
		self.hpmpmsg = tk.IntVar()
		if "hpmpupd" in self.master.filters:
			self.hpmpmsg.set(1)
		self.hpmp_chkbox = Slider(self, text="", variable=self.hpmpmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.hpmp_chkbox.grid(row=5, column=0, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.statlbl = tk.Label(self, text=" Stat Updates ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.statlbl.grid(row=6, column=0, padx=(20, 20), pady=(10, 10), sticky='w')
		self.statmsg = tk.IntVar()
		if "statupd" in self.master.filters:
			self.statmsg.set(1)
		self.stat_chkbox = Slider(self, text="", variable=self.statmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.stat_chkbox.grid(row=6, column=0, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.movelbl = tk.Label(self, text=" Moves ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.movelbl.grid(row=7, column=0, padx=(20, 20), pady=(10, 10), sticky='w')
		self.movemsg = tk.IntVar()
		if "move" in self.master.filters:
			self.movemsg.set(1)
		self.move_chkbox = Slider(self, text="", variable=self.movemsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.move_chkbox.grid(row=7, column=0, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.baglbl = tk.Label(self, text=" Inventory ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.baglbl.grid(row=2, column=1, padx=(20, 20), pady=(10, 10), sticky='w')
		self.bagmsg = tk.IntVar()
		if "bagupd" in self.master.filters:
			self.bagmsg.set(1)
		self.bag_chkbox = Slider(self, text="", variable=self.bagmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.bag_chkbox.grid(row=2, column=1, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.forgetlbl = tk.Label(self, text=" Forget ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.forgetlbl.grid(row=3, column=1, padx=(20, 20), pady=(10, 10), sticky='w')
		self.forgetmsg = tk.IntVar()
		if "forget" in self.master.filters:
			self.forgetmsg.set(1)
		self.forget_chkbox = Slider(self, text="", variable=self.forgetmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.forget_chkbox.grid(row=3, column=1, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.showlbl = tk.Label(self, text=" HP/XP ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.showlbl.grid(row=4, column=1, padx=(20, 20), pady=(10, 10), sticky='w')
		self.showmsg = tk.IntVar()
		if "shownums" in self.master.filters:
			self.showmsg.set(1)
		self.show_chkbox = Slider(self, text="", variable=self.showmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.show_chkbox.grid(row=4, column=1, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.shoplbl = tk.Label(self, text=" Shopable ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.shoplbl.grid(row=5, column=1, padx=(20, 20), pady=(10, 10), sticky='w')
		self.shopmsg = tk.IntVar()
		if "shop" in self.master.filters:
			self.shopmsg.set(1)
		self.shop_chkbox = Slider(self, text="", variable=self.shopmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.shop_chkbox.grid(row=5, column=1, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.selectlbl = tk.Label(self, text=" Selected ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.selectlbl.grid(row=6, column=1, padx=(20, 20), pady=(10, 10), sticky='w')
		self.selectmsg = tk.IntVar()
		if "select" in self.master.filters:
			self.selectmsg.set(1)
		self.select_chkbox = Slider(self, text="", variable=self.selectmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.select_chkbox.grid(row=6, column=1, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.dimalbl = tk.Label(self, text=" Diamonds ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.dimalbl.grid(row=7, column=1, padx=(20, 20), pady=(10, 10), sticky='w')
		self.dimamsg = tk.IntVar()
		if "dimas" in self.master.filters:
			self.dimamsg.set(1)
		self.dima_chkbox = Slider(self, text="", variable=self.dimamsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.dima_chkbox.grid(row=7, column=1, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.redmsglbl = tk.Label(self, text=" Red Alerts ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.redmsglbl.grid(row=2, column=2, padx=(20, 20), pady=(10, 10), sticky='w')
		self.redmsgmsg = tk.IntVar()
		if "redmsg" in self.master.filters:
			self.redmsgmsg.set(1)
		self.redmsg_chkbox = Slider(self, text="", variable=self.redmsgmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.redmsg_chkbox.grid(row=2, column=2, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.whitemsglbl = tk.Label(self, text=" White Alerts ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.whitemsglbl.grid(row=3, column=2, padx=(20, 20), pady=(10, 10), sticky='w')
		self.whitemsgmsg = tk.IntVar()
		if "whitemsg" in self.master.filters:
			self.whitemsgmsg.set(1)
		self.whitemsg_chkbox = Slider(self, text="", variable=self.whitemsgmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.whitemsg_chkbox.grid(row=3, column=2, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.youarelbl = tk.Label(self, text=" Session ID ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.youarelbl.grid(row=4, column=2, padx=(20, 20), pady=(10, 10), sticky='w')
		self.youaremsg = tk.IntVar()
		if "youare" in self.master.filters:
			self.youaremsg.set(1)
		self.youare_chkbox = Slider(self, text="", variable=self.youaremsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.youare_chkbox.grid(row=4, column=2, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.friendlbl = tk.Label(self, text=" Friend List ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.friendlbl.grid(row=5, column=2, padx=(20, 20), pady=(10, 10), sticky='w')
		self.friendmsg = tk.IntVar()
		if "friendlist" in self.master.filters:
			self.friendmsg.set(1)
		self.friend_chkbox = Slider(self, text="", variable=self.friendmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.friend_chkbox.grid(row=5, column=2, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.botlbl = tk.Label(self, text=" Your Bot ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.botlbl.grid(row=6, column=2, padx=(20, 20), pady=(10, 10), sticky='w')
		self.botmsg = tk.IntVar()
		if "bot" in self.master.filters:
			self.botmsg.set(1)
		self.bot_chkbox = Slider(self, text="", variable=self.botmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.bot_chkbox.grid(row=6, column=2, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.clientlbl = tk.Label(self, text=" Client ", bg='#1f1f1f', fg='#57cade', relief='groove')
		self.clientlbl.grid(row=7, column=2, padx=(20, 20), pady=(10, 10), sticky='w')
		self.clientmsg = tk.IntVar()
		if "client" in self.master.filters:
			self.clientmsg.set(1)
		self.client_chkbox = Slider(self, text="", variable=self.clientmsg, offvalue=0, onvalue=1, bd=0, bg='black', fg='#57cade', cursor='hand2')
		self.client_chkbox.grid(row=7, column=2, padx=(20, 20), pady=(10, 10), sticky='e')
		
		self.button = tk.Button(self, cursor='hand2', text="   OK   ", bg='#c7ffb5')
		self.button['command'] = self.okbutton
		self.button.grid(row=10, column=0, columnspan=3, padx=(25, 150), pady=(25, 25), sticky='e')
		self.button.focus()
		
		self.bind('<Return>', self.retbutton)
		
		self.button2 = tk.Button(self, cursor='hand2', text=" Cancel ", bg='#f73e47')
		self.button2['command'] = self.nobutton
		self.button2.grid(row=10, column=0, columnspan=3, padx=(25, 75), pady=(25, 25), sticky='e')
		self.deiconify()
	def okbutton(self):
		future_filters = []
		if self.seemsg.get() == 1:
			future_filters.append("messages")
		
		if self.dismsg.get() == 1:
			future_filters.append("disconnect")
		
		if self.atkmsg.get() == 1:
			future_filters.append("attack")
		
		if self.hpmpmsg.get() == 1:
			future_filters.append("hpmpupd")
		
		if self.statmsg.get() == 1:
			future_filters.append("statupd")
		
		if self.movemsg.get() == 1:
			future_filters.append("move")
		
		if self.bagmsg.get() == 1:
			future_filters.append("bagupd")
		
		if self.forgetmsg.get() == 1:
			future_filters.append("forget")
		
		if self.showmsg.get() == 1:
			future_filters.append("shownums")
		
		if self.shopmsg.get() == 1:
			future_filters.append("shop")
		
		if self.selectmsg.get() == 1:
			future_filters.append("select")
		
		if self.dimamsg.get() == 1:
			future_filters.append("dimas")
		
		if self.redmsgmsg.get() == 1:
			future_filters.append("redmsg")
		
		if self.whitemsgmsg.get() == 1:
			future_filters.append("whitemsg")
		
		if self.youaremsg.get() == 1:
			future_filters.append("youare")
		
		if self.friendmsg.get() == 1:
			future_filters.append("friendlist")
		
		if self.botmsg.get() == 1:
			future_filters.append("bot")
		
		if self.clientmsg.get() == 1:
			future_filters.append("client")
		
		self.master.filters = future_filters
		
		if self.master.botpower:
			warning_msg = """\nThese settings will not be applied til the bot is restarted.\n"""
			warn_msg = MsgBox("Heads Up", warning_msg, 3, self.topx, self.topy)
			warn_msg.wait_window()
		self.destroy()
	def selectall(self):
		if self.seemsg.get() == 0:
			self.msg_chkbox.play()
		
		if self.dismsg.get() == 0:
			self.dis_chkbox.play()
		
		if self.atkmsg.get() == 0:
			self.atk_chkbox.play()
		
		if self.hpmpmsg.get() == 0:
			self.hpmp_chkbox.play()
		
		if self.statmsg.get() == 0:
			self.stat_chkbox.play()
		
		if self.movemsg.get() == 0:
			self.move_chkbox.play()
		
		if self.bagmsg.get() == 0:
			self.bag_chkbox.play()
		
		if self.forgetmsg.get() == 0:
			self.forget_chkbox.play()
		
		if self.showmsg.get() == 0:
			self.show_chkbox.play()
		
		if self.shopmsg.get() == 0:
			self.shop_chkbox.play()
		
		if self.selectmsg.get() == 0:
			self.select_chkbox.play()
		
		if self.dimamsg.get() == 0:
			self.dima_chkbox.play()
		
		if self.redmsgmsg.get() == 0:
			self.redmsg_chkbox.play()
		
		if self.whitemsgmsg.get() == 0:
			self.whitemsg_chkbox.play()
		
		if self.youaremsg.get() == 0:
			self.youare_chkbox.play()
		
		if self.friendmsg.get() == 0:
			self.friend_chkbox.play()
		
		if self.botmsg.get() == 0:
			self.bot_chkbox.play()
		
		if self.clientmsg.get() == 0:
			self.client_chkbox.play()
	def deselectall(self):
		if self.seemsg.get() == 1:
			self.msg_chkbox.play()
		
		if self.dismsg.get() == 1:
			self.dis_chkbox.play()
		
		if self.atkmsg.get() == 1:
			self.atk_chkbox.play()
		
		if self.hpmpmsg.get() == 1:
			self.hpmp_chkbox.play()
		
		if self.statmsg.get() == 1:
			self.stat_chkbox.play()
		
		if self.movemsg.get() == 1:
			self.move_chkbox.play()
		
		if self.bagmsg.get() == 1:
			self.bag_chkbox.play()
		
		if self.forgetmsg.get() == 1:
			self.forget_chkbox.play()
		
		if self.showmsg.get() == 1:
			self.show_chkbox.play()
		
		if self.shopmsg.get() == 1:
			self.shop_chkbox.play()
		
		if self.selectmsg.get() == 1:
			self.select_chkbox.play()
		
		if self.dimamsg.get() == 1:
			self.dima_chkbox.play()
		
		if self.redmsgmsg.get() == 1:
			self.redmsg_chkbox.play()
		
		if self.whitemsgmsg.get() == 1:
			self.whitemsg_chkbox.play()
		
		if self.youaremsg.get() == 1:
			self.youare_chkbox.play()
		
		if self.friendmsg.get() == 1:
			self.friend_chkbox.play()
		
		if self.botmsg.get() == 1:
			self.bot_chkbox.play()
		
		if self.clientmsg.get() == 1:
			self.client_chkbox.play()
	def nobutton(self):
		self.destroy()
	def retbutton(self, event):
		self.okbutton()

class ConsoleBox(tk.Toplevel):

	def __init__(self, master, title="ConsoleBox", set_x=0, set_y=0):
		tk.Toplevel.__init__(self)
		self.withdraw()
		self.title("Rucoy Bot - " + title)
		self.iconbitmap('robot.ico')
		self.configure(background="black")
		self.protocol("WM_DELETE_WINDOW", self.closeme)
		self.geometry("600x400")
		self.minsize(400, 200)
		
		center_x = self.winfo_toplevel().winfo_width()
		center_x = int(center_x /2)
		center_x = 200 - center_x
		
		self.geometry("+{}+{}".format(set_x+center_x, set_y+5))
		
		self.textbox = CustomText(self, width=160, wrap="word")
		self.textbox.config(bg="#1f1f1f", fg='#4fbd5a')
		self.textbox.tag_configure("stderr", foreground="#b22222")
		self.textbox.tag_configure("stdout", foreground="#4fbd5a")
		
		self.scroller = tk.Scrollbar(self, command=self.textbox.yview, orient=tk.VERTICAL)
		self.textbox.grid(row=0, column=0, sticky='nsew')
		self.scroller.grid(row=0, column=1, sticky='nsw')
		self.textbox.configure(yscrollcommand=self.scroller.set)
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=0)
		self.grid_rowconfigure(0, weight=1)
		
		s = str(float(self.textbox.index("insert"))-2)
		self.textbox.insert('end', self.master.text.get('1.0', 'end-1c'))
		self.textbox.tag_configure("blue", foreground="#0345fc")
		self.textbox.tag_configure("red", foreground="#ed2828")
		self.textbox.tag_configure("#57cade", foreground="#9d32a8")
		self.textbox.tag_configure("yellow", foreground="#f8fc03")
		self.textbox.highlight_pattern("^You will now.*$", "blue", regexp=True, start=s)
		self.textbox.highlight_pattern("^Store set up times.*$", "red", regexp=True, start=s)
		self.textbox.highlight_pattern("^You can now.*$", "blue", regexp=True, start=s)
		self.textbox.highlight_pattern("^The time limits.*$", "red", regexp=True, start=s)
		self.textbox.highlight_pattern("^Rucoy Bot .*$", "red", regexp=True, start=s)
		highlight_update(self.textbox)
		self.textbox.see('end')
		self.textbox.configure(state='disabled')
		
		self.focus()
		self.deiconify()
		self.after(100, self.update_textbox)

	def update_textbox(self):
		original = self.master.text.get('1.0', 'end-1c')
		current = self.textbox.get('1.0', 'end-1c')
		if original != current:
			self.textbox.configure(state='normal')
			self.textbox.delete(1.0, 'end')
			s = str(float(self.textbox.index("insert"))-2)
			self.textbox.insert('end', self.master.text.get('1.0', 'end-1c'))
			#highlight_update(self.textbox)
			self.textbox.see('end')
			self.textbox.tag_configure("blue", foreground="#0345fc")
			self.textbox.tag_configure("red", foreground="#ed2828")
			self.textbox.tag_configure("#57cade", foreground="#9d32a8")
			self.textbox.tag_configure("yellow", foreground="#f8fc03")
			self.textbox.highlight_pattern("^You will now.*$", "blue", regexp=True, start=s)
			self.textbox.highlight_pattern("^Store set up times.*$", "red", regexp=True, start=s)
			self.textbox.highlight_pattern("^You can now.*$", "blue", regexp=True, start=s)
			self.textbox.highlight_pattern("^The time limits.*$", "red", regexp=True, start=s)
			self.textbox.highlight_pattern("^Rucoy Bot has .*$", "red", regexp=True, start=s)
			highlight_update(self.textbox)
			self.textbox.configure(state='disabled')
		self.after(100, self.update_textbox)
	def closeme(self):
		self.master.expandbtn.grid(row=20, column=2, padx=(5, 0), pady=(5, 0), sticky='se')
		self.master.expandbtn.configure(state='normal')
		self.destroy()

class Slider(tk.Button):
	def __init__(self, master, filename='final.gif', text="", variable=0, offvalue=0, onvalue=1, command=0, bd=0, bg='black', fg='#57cade', cursor='hand2'):
		im = Image.open(filename)
		seq = []
		self.onvalue = onvalue
		self.offvalue = offvalue
		self.master = master
		self.variable = variable
		self.master.command = command
		try:
			while 1:
				seq.append(im.copy().resize((35, 15)))
				im.seek(len(seq)) 
		except EOFError:
			pass 
		
		self.delay = 10

		first = seq[0].convert('RGBA')
		self.frames = [ImageTk.PhotoImage(first)]

		temp = seq[0]
		for image in seq[1:]:
			temp.paste(image)
			frame = temp.convert('RGBA')
			self.frames.append(ImageTk.PhotoImage(frame))
		
		if self.variable.get() == 0:
			self.idx = int(len(self.frames)/2)
			self.direction = 'forward'
		else:
			self.idx = 0
			self.direction = 'backward'
		
		tk.Button.__init__(self, master, cursor='hand2', image=self.frames[self.idx], command=self.play)
		self.config(bg='black', relief='flat')
		self.a = 1

	def play(self):
		if self.idx >= len(self.frames)-1:
			self.direction = 'backward'
			self.idx = 0
			self.config(command=self.play)
			self.variable.set(self.onvalue)
			if self.master.command != 0:
				self.a = self.master.command()
				if self.a == 0:
					self.after(5, self.play)
		elif self.idx >= len(self.frames)/2 and self.direction == 'backward':
			self.direction = 'forward'
			self.config(command=self.play)
			self.variable.set(self.offvalue)
			if self.master.command != 0 and self.a != 0:
				_ = self.master.command()
			else:
				self.a = 1
		else:
			self.after(self.delay, self.play)
			self.config(command=self.donothing)
		
		self.idx += 1
		self.config(image=self.frames[self.idx])
	
	def donothing(self):
		pass

class Slider2(tk.Button):
	def __init__(self, master, filename='final.gif', text="", variable=0, offvalue=0, onvalue=1, command=0, bd=0, bg='black', fg='#57cade', cursor='hand2'):
		im = Image.open(filename)
		seq = []
		self.onvalue = onvalue
		self.offvalue = offvalue
		self.master = master
		self.variable = variable
		self.master.command2 = command
		try:
			while 1:
				seq.append(im.copy().resize((35, 15)))
				im.seek(len(seq)) 
		except EOFError:
			pass 
		
		self.delay = 10

		first = seq[0].convert('RGBA')
		self.frames = [ImageTk.PhotoImage(first)]

		temp = seq[0]
		for image in seq[1:]:
			temp.paste(image)
			frame = temp.convert('RGBA')
			self.frames.append(ImageTk.PhotoImage(frame))
		
		if self.variable.get() == 0:
			self.idx = int(len(self.frames)/2)
			self.direction = 'forward'
		else:
			self.idx = 0
			self.direction = 'backward'
		
		tk.Button.__init__(self, master, cursor='hand2', image=self.frames[self.idx], command=self.play)
		self.config(bg='black', relief='flat')
		self.a = 1

	def play(self):
		if self.idx >= len(self.frames)-1:
			self.direction = 'backward'
			self.idx = 0
			self.config(command=self.play)
			self.variable.set(self.onvalue)
			if self.master.command2 != 0:
				self.a = self.master.command2()
				if self.a == 0:
					self.after(5, self.play)
		elif self.idx >= len(self.frames)/2 and self.direction == 'backward':
			self.direction = 'forward'
			self.config(command=self.play)
			self.variable.set(self.offvalue)
			if self.master.command2 != 0 and self.a != 0:
				_ = self.master.command2()
			else:
				self.a = 1
		else:
			self.after(self.delay, self.play)
			self.config(command=self.donothing)
		
		self.idx += 1
		self.config(image=self.frames[self.idx])
	
	def donothing(self):
		pass

class TextRedirector(object):
	def __init__(self, widget, tag="stdout"):
		self.widget = widget
		self.tag = tag

	def write(self, str):
		self.widget.configure(state="normal")
		self.widget.insert("end", str, (self.tag,))
		lines = int(float(self.widget.index('end')))
		if  lines > 1000:
			deleterange = float(lines - 1000)
			self.widget.delete(1.0, deleterange)
		self.widget.see("end")
		self.widget.tag_configure("blue", foreground="#0345fc")
		self.widget.tag_configure("red", foreground="#ed2828")
		self.widget.tag_configure("purple", foreground="#9d32a8")
		self.widget.tag_configure("yellow", foreground="#f8fc03")
		self.widget.highlight_pattern("^You will now.*$", "blue", regexp=True)
		self.widget.highlight_pattern("^Store set up times.*$", "red", regexp=True)
		self.widget.highlight_pattern("^You can now.*$", "blue", regexp=True)
		self.widget.highlight_pattern("^The time limits.*$", "red", regexp=True)
		self.widget.update()
		self.widget.configure(state="disabled")
	def flush(self):
		sys.__stdout__.flush()

if __name__ == "__main__":
	freeze_support()
	
	app = RucoyGui()
	app.configure(background="black")
	app.protocol("WM_DELETE_WINDOW", app.on_closing)
	app.iconbitmap('robot.ico')
	app.resizable(False, False)
	app.title("Rucoy Bot")
	app.geometry("785x730")
	app.mainloop()

# Setting options...
#--Email on direct messages, (on/off) & (email to send to)
#--Resolve levels of players when displaying messages
#--Upload store data, e.g. Dragon Bow selling for 50k to rucoybot.com
#--Verbose Level: (Default, Default+Raw, Everything, Everything+Raw)
#--Hp/Mp potion threshhold ([X]%) ([X]%) 