import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from time import sleep
import base64
import sys
import time


def helper(que, printqu):
	scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
	credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
	gc = gspread.authorize(credentials)
	wks = gc.open("Rucoy Store Prices").sheet1
	
	refresh_time = time.time()+(60*30)
	
	global qu
	qu = printqu
	sys.stdout = qu
	
	new_data_points = 0
	
	#A_column not needed...
	#A_column = wks.range('A1:A501')
	B_column = wks.range('B1:B501')
	C_column = wks.range('C1:C501')
	D_column = wks.range('D1:D501')
	E_column = wks.range('E1:E501')
	F_column = wks.range('F1:F501')
	while True:
		try:
			thingtoprocess = que.get()
			things = thingtoprocess.split('|')
			if refresh_time <= time.time():
				scope = ['https://spreadsheets.google.com/feeds',
					 'https://www.googleapis.com/auth/drive']
				credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
				gc = gspread.authorize(credentials)
				wks = gc.open("Rucoy Store Prices").sheet1
				refresh_time = time.time()+(60*30)
			if things[0] == 'send':
				if things[3][:-2] == ',' or things[3][:-2] == ', ':
					continue
				#expects 'send|example@gmail.com|Username|Hall Pots: Hi Person!'
				sender_email = "your.rucoybot@gmail.com"
				encoded_password = b"censored"
				decodeme = encoded_password[::-1]
				password = base64.b64decode(decodeme).decode('ascii')

				message = MIMEMultipart("alternative")
				message["Subject"] = "Rucoy Bot - You've Received a Message."
				message["From"] = sender_email
				message["To"] = things[1]
				
				if things[2] == 'idk':
					name = 'User'
				else:
					name = things[2]
				
				# Create the plain-text and HTML version of your message
				if name != 'Developer' and things[3].find(':') > 0:
					text = """Dear {},\n\nYou've received the following message on Rucoy while botting-\n\n{}\n\nThank you,\nYour Friendly, Neighborhood Robot""".format(name, things[3])
				else:
					text = """{}\n\nThank you,\nYour Friendly, Neighborhood Robot""".format(things[3])

				# Turn these into plain/html MIMEText objects
				part1 = MIMEText(text, "plain")

				# Add HTML/plain-text parts to MIMEMultipart message
				# The email client will try to render the last part first
				message.attach(part1)

				# Create secure connection with server and send email
				context = ssl.create_default_context()
				with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
					server.login(sender_email, password)
					server.sendmail(sender_email, things[1], message.as_string())
				if name != 'Developer':
					prettyprint("Sent email with update to {}. ".format(things[1]))
			else:
				# expects '19|Steel Belt|19000'
				if things[0] == 'done':
					wks.update_cells(B_column)
					wks.update_cells(C_column)
					wks.update_cells(D_column)
					wks.update_cells(E_column)
					wks.update_cells(F_column)
					sleep(6)
					B_column = wks.range('B1:B501')
					C_column = wks.range('C1:C501')
					D_column = wks.range('D1:D501')
					E_column = wks.range('E1:E501')
					F_column = wks.range('F1:F501')
					prettyprint('{} new data points have been added to the Rucoy Store Prices\nb      >>> database. Visit rucoybot.com/prices for more info. '.format(new_data_points))
					new_data_points = 0
					continue
				
				itemid = int(things[0])
				itemname = things[1]
				price = int(things[2])
				#Google Sheets- Item ID, Name, Min, Max, Avg, Data Points
				pre_min = C_column[itemid].value
				pre_max = D_column[itemid].value
				pre_avg = E_column[itemid].value
				pre_dat = F_column[itemid].value
				
				if itemname.find('#') == -1:
					B_column[itemid].value = itemname
				if pre_min != '':
					pre_min = int(pre_min.replace(',', ''))
					pre_max = int(pre_max.replace(',', ''))
					if price < pre_min:
						C_column[itemid].value = '{:,d}'.format(price)
					if price > pre_max:
						D_column[itemid].value = '{:,d}'.format(price)
				else:
					C_column[itemid].value = '{:,d}'.format(price)
					D_column[itemid].value = '{:,d}'.format(price)
				if pre_dat != '':
					if type(pre_dat) == type('a'):
						pre_dat = int(pre_dat.replace(',', ''))
					pre_avg = int(pre_avg.replace(',', ''))
					new_avg = (pre_avg*pre_dat+price)/(pre_dat+1)
					new_avg = int(new_avg)
					E_column[itemid].value = '{:,d}'.format(new_avg)
					F_column[itemid].value = '{:,d}'.format(pre_dat+1)
				else:
					E_column[itemid].value = '{:,d}'.format(price)
					F_column[itemid].value = 1
				new_data_points += 1
		except Exception as e:
			prettyprint("An unknown error occurred - rucoynethelp - {}. ".format(e))
			

def prettyprint(message):
	forwardthis = "Bot    >>> {}".format(message)
	if message != '':
		print(forwardthis)