#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Created by Alberto Martínez Alba.
# Shared under GNU GPL v2
# 2015

import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi, random, sqrt, cos, sin, log, exp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler

import matplotlib.pyplot as plt

from matplotlib.figure import Figure

import sys
import tkFileDialog, tkMessageBox
if sys.version_info[0] < 3:
	from Tkinter import *
else:
	from tkinter import *
from ttk import Style, Frame, Button, Radiobutton, Entry, Checkbutton

import csv
from itertools import izip


class Principal(Frame):

	# Class for helping Tooltips
	class ToolTip(object):

		def __init__(self, widget):
			self.widget = widget
			self.tipwindow = None
			self.id = None
			self.x = self.y = 0

		def showtip(self, text, lang):
			self.text = text
			if self.tipwindow or not self.text:
				return
			x, y, cx, cy = self.widget.bbox("insert")
			x = x + self.widget.winfo_rootx() + 27
			y = y + cy + self.widget.winfo_rooty() +27
			self.tipwindow = tw = Toplevel(self.widget)
			tw.wm_overrideredirect(1)
			tw.wm_geometry("+%d+%d" % (x, y))
			try:
				# For Mac OS
				tw.tk.call("::tk::unsupported::MacWindowStyle",
						   "style", tw._w,
						   "help", "noActivates")
			except TclError:
				pass
			label = Label(tw, text=self.text[lang], justify=LEFT,
						  background="#ffffe0", relief=SOLID, borderwidth=1,
						  font=("tahoma", "8", "normal"))
			label.pack(ipadx=1)

		def hidetip(self):
			tw = self.tipwindow
			self.tipwindow = None
			if tw:
				tw.destroy()

	# Initialization function
	def __init__(self, parent):

		Frame.__init__(self, parent)   
		 
		self.parent = parent

		# Spiral parameters (defined as StringVars for convenience)
		self.a = StringVar()
		self.a.set('0')

		self.b = StringVar()
		self.b.set('0.5')

		self.c = StringVar()
		self.c.set('1')

		self.lMax = StringVar()
		self.lMax.set(158)

		self.frec = StringVar()
		self.frec.set(500)

		self.StringLongitud = StringVar()
		self.StringRadio = StringVar()

		# Help mode flag
		self.ayuda = False

		# Figure object
		self.f = Figure(figsize=(5,5))
		
		self.initUI()

	# Tooltip creator function (allowed by help mode flag)
	def createToolTip(self, widget, text):
		toolTip = self.ToolTip(widget)
		def enter(event):
			if self.ayuda:
				toolTip.showtip(text, self.lang)
		def leave(event):
			toolTip.hidetip()
		widget.bind('<Enter>', enter)
		widget.bind('<Leave>', leave)

	# Euclidean distance calculator function
	def distancia( self, r1, phi1, r2, phi2 ):
		return sqrt(r1**2 + r2**2 - 2*r1*r2*cos(phi1-phi2))

	# Polar to Cartesian coordinates
	def pol2cart(self, rho, phi):
		x = rho*cos(phi)
		y = rho*sin(phi)
		return(x, y)

	# 
	def grafico(self):

		# Set figure size
		self.f = Figure(figsize=(5,5))

		# Check whether negative parameters are present and show an error
		if float(self.c.get()) < 0 or float(self.b.get()) < 0:
			print self.lang
			tkMessageBox.showerror("Error", self.error.get())
			return

		# Set figure axis
		ax = self.f.add_subplot(111, polar=True)

		# Initialize r and theta lists at the center point
		self.theta_disc = [0]
		self.r_disc = [0]
		self.theta_disc_n = [0]

		# Initialize length value and list
		l = 0
		l_vec = []

		# Loop limited by antenna length
		while l < int(self.lMax.get()):

			# Length of each antenna segment in cm, computed as 1/15 of the wave length
			lseg = 300/float(self.frec.get())*100/15

			if self.tipoCurva.get() == 1:
				# Archimedean spiral

				# New theta values are calculated according to the following:
				# In an Archimedean spiral
				# 		          /r  -  a\ c 
				# 		theta  =  |-------|   
				# 		          \   b   /   

				# In order to get an approximately equally spaced segments, new theta values are computed according to the next formula. This formula has been worked
				# out gradually, not basing on any well-known expression.
				# 		                          /0.5 * lseg  -  a\ c                   
				# 		                          |----------------|    -  lseg          
				# 		                          \        b       /                     
				# 		                          ------------------------------  +  lseg
				# 		                                 10 * theta   +  1               
				# 		                                           n                     
				# 		theta       =  theta   +  ---------------------------------------
				# 		     n + 1          n                    r   +  1                
				# 		                                          n                      

				self.theta_disc.append(self.theta_disc[-1] + \
					(( ((0.5*lseg - float(self.a.get()))/float(self.b.get()))**(float(self.c.get())) - lseg) / (10*self.theta_disc[-1] + 1) + lseg) \
					 / (self.r_disc[-1] + 1))
				# print str(lseg)
				# print str(self.r_disc[-1])
			else:
				# print "Eh: " + str(self.theta_disc[-1])
				# print "Ra: " + str(self.r_disc[-1])
				# print "Ls: " + str(lseg)
				# print "Ot: " + str(log(0.5*lseg/float(self.a.get()))/float(self.b.get()))
				self.theta_disc.append(self.theta_disc[-1] + \
					(( max(log(0.5*lseg/float(self.a.get()))/float(self.b.get()),float(self.a.get())) - lseg) * exp(-1*self.theta_disc[-1]) + lseg) \
					 / (self.r_disc[-1] + 1))
				#print str(lseg)
				#print str(self.r_disc[-1])

			if self.tipoCurva.get() == 1:
				self.r_disc.append(float(self.b.get())*self.theta_disc[-1]**(1/float(self.c.get())) + float(self.a.get()))
			elif self.tipoCurva.get() == 2:
				self.r_disc.append(float(self.a.get())*exp(float(self.b.get())*self.theta_disc[-1]))

			self.theta_disc_n.append(pi + self.theta_disc[-1])
			
			l_vec.append(self.distancia(self.r_disc[-1],self.theta_disc[-1],self.r_disc[-2],self.theta_disc[-2]))

			l += l_vec[-1]

		if self.fuente.get() and str(self.checkFuente.cget('state')) == 'normal':
			self.theta_disc.remove(0)
			self.r_disc.remove(0)
			self.theta_disc_n.remove(0)
			ax.plot([self.theta_disc[0],self.theta_disc_n[0]], [self.r_disc[0], self.r_disc[0]], color='r')
			ax.plot([0],[0], color='m', marker='o', markersize=5)

		self.StringLongitud.set("%#.1f cm" % l)
		self.StringRadio.set("%#.1f cm" % max(self.r_disc))

		ax.plot(self.theta_disc, self.r_disc, color='b', marker='.', markersize=4)
		if self.espejar.get():
			ax.plot(self.theta_disc_n, self.r_disc, color='g', marker='.', markersize=4)

		ax.set_rmax(max(self.r_disc))
		ax.grid(True)

		#with open('distancias.csv', 'wb') as f:
		#	writer = csv.writer(f)
		#	writer.writerows(izip(self.theta_disc, l_vec))


	def regraficar(self):
		self.grafico()
		self.canvas.get_tk_widget().pack_forget()
		self.canvas = FigureCanvasTkAgg(self.f, master=self.frame2)
		#canvas.show()
		self.canvas.get_tk_widget().pack(side=TOP,fill=BOTH, expand=1, padx=10, pady=10)

	def cambiaFormula(self):
		curvas = ['''R0lGODlhbAAWAOMPAAwMDLa2thYWFiIiIlBQUJ6enubm5gQEBGJiYszMzEBAQDAwMHR0dIqKigAAAP///yH5BAEKAA8ALAAAAABsABYAAAT+8MlJq7046817ToYnjmRpXsqpriw3JGgrz2pDHHDFFHTvezjL4kcsWoKUBIHCQDQQxmhy4EhZDATGkoKcEHIPwjIBkJoljsZVEFIwuGDJUJJwhM7ngN0i4D0YcxJdDwVqEg0CeC0DHQhlOokSCJGCcVYSAYyHiiaaGwOXEwCGDwqRBQgOC28PBqEPCAgMDDANgH8MCnEzAQSxCFufHQ6xuSF6FACeFgwBG1AHCwYGaSgC19jZAssViHQOrMIbelsIQwoHCuoLDsFCGwUgDn67LXVgDvUX3BeOEw0OHgCAcmgeBgME4QUssoBSgQMe+Am5lOqBQQkKHq0gIHEGMS9yHU1lO6CN34FwDamBOZBQhYCWGERqyyaxjp8HLyNuoOYMDYI6//awcNDzh0oJ1HiEy9CRwsIHDSBanCBg6YkCT4kA8EPAToGiTDkIgGEAQM8XsAKtuGUkgRsoYqxiaDrBbS4wbmNx2iuBLt+/HNQCfhABADs=''',
		'''R0lGODlhQwASAOMPAAwMDLa2thYWFiIiIlBQUJ6enubm5gQEBGJiYszMzEBAQDAwMHR0dIqKigAAAP///yH5BAEKAA8ALAAAAABDABIAAATn8MlJq70463ZSJQyhjWSpGUe1BM/imXCcNQvVDNLQyHz/KAOGgiXYPQAsn7IEKDwKg4SDgCA4DMtsBiVpCAqALk5LrhRqPwIt5yy7H4GaAWBIKJ7391uBULyoIhMNDDUMQi9uAVQIVRQJCAyMMAgPBwsGBg5GFAoCnp+gAmMXXhJSDBOEE3kkBQmZbYhkUogOLwEHWHCBJgUOehMLAhMFKTlBkG0wBKN6DpQSzBMOqD4C0BmdoaHNE1LK1xKwSg5Jepkv46gOyk+yGr7AE03RVwUsCrwF1SWq8g92Ij0gAGIClUjmSEQAADs=''',
		'''''']
		formula = PhotoImage(data=curvas[self.tipoCurva.get()-1])
		self.formulaLabel.configure(image=formula)
		self.formulaLabel.image = formula

		if self.tipoCurva.get() == 1:
			self.parC.config(state=NORMAL)
			self.labelC.config(state=NORMAL)
		else:
			self.parC.config(state=DISABLED)
			self.labelC.config(state=DISABLED)

	def activarFuente(self):
		if self.espejar.get():
			self.checkFuente.config(state=NORMAL)
		else:
			self.checkFuente.config(state=DISABLED)

	def escribirFichero(self):
		tipoCurva = ['Arq', 'Log']
		c = [self.c.get() + ' ', '']

		self.file_opt = options = {}
		options['defaultextension'] = '.nec'
		options['filetypes'] = [('NEC2 files', '.nec'),('all files', '.*')]
		options['initialdir'] = '~/Documentos/Antenas/Espirales'
		options['initialfile'] = 'Spiral ' + tipoCurva[int(self.tipoCurva.get())-1] + ' ' + \
									self.a.get() + ' ' + self.b.get() + ' ' + c[int(self.tipoCurva.get())-1] + self.lMax.get() + ' ' + self.frec.get() + '.nec'
		options['parent'] = self.parent
		options['title'] = 'Save NEC'

		fich = tkFileDialog.asksaveasfile(mode='w', **self.file_opt)

		r_final = list(reversed(self.r_disc)) + self.r_disc
		theta_final = list(reversed(self.theta_disc_n)) + self.theta_disc

		x_ant, y_ant = self.pol2cart(r_final[0], theta_final[0])

		tipoCurvaExt = ['Archimedean', 'Logarithmic']
		fich.write('CM Created with PySAD\n')
		fich.write('CM L = %#.1f\n' % float(self.lMax.get()))
		fich.write('CM ' + tipoCurvaExt[int(self.tipoCurva.get())-1] + ' spiral')
		fich.write('CM a = ' + self.a.get())
		fich.write('CM b = ' + self.b.get())
		if int(self.tipoCurva.get()) == 0 :
			fich.write('CM c = ' + self.c.get())
		fich.write('CE\n')

		print len(r_final)

		for i in range(len(r_final)-1):
			x, y = self.pol2cart(r_final[i+1], theta_final[i+1])
			linea = 'GW\t%#d\t%#d\t%#.5f\t%#.5f\t%#.5f\t%#.5f\t%#.5f\t%#.5f\t%#.5f\n' % (i+1,1,x_ant/100,y_ant/100,0,x/100,y/100,0,0.001)
			fich.write(linea)
			x_ant, y_ant = x, y
			
		fich.write('GE\t0\nGN\t-1\nEK\n')
		fich.write('EX\t%#d\t%#d\t%#d\t%#d\t%#d\t%#d\n' % (0,len(r_final)/2,1,0,1,0))
		fich.write('FR\t0\t0\t0\t0\t299.8\t0\nEN')

		fich.close()

	def escribirPDF(self):
		tipoCurva = ['Arq', 'Log']
		c = [self.c.get() + ' ', '']
		self.file_opt = options = {}
		options['defaultextension'] = '.pdf'
		options['filetypes'] = [('PDF files', '.pdf'),('all files', '.*')]
		options['initialdir'] = '~'
		options['initialfile'] = 'Spiral ' + tipoCurva[int(self.tipoCurva.get())-1] + ' ' + \
									self.a.get() + ' ' + self.b.get() + ' ' + c[int(self.tipoCurva.get())-1] + self.lMax.get() + ' ' + self.frec.get() + '.nec'
		options['parent'] = self.parent
		options['title'] = 'Save PDF'

		fich = tkFileDialog.asksaveasfile(mode='w', **self.file_opt)

		#self.f.axis('off')
		matplotlib.rcParams.update({'font.size': 1})

		self.f.gca().axes.get_xaxis().set_visible(False)
		self.f.gca().axes.get_yaxis().set_visible(False)

		papeles_w = [21, 29.7, 42, 59.4, 84.1]
		papeles_h = [29.7, 42, 59.4, 84.1, 118.9]

		for i_pap in range(0, len(papeles_w)-1):
			if 2*max(self.r_disc) < papeles_w[i_pap]:
				break

		
		print i_pap

		self.f.set_size_inches(papeles_w[i_pap]/2.54, papeles_h[i_pap]/2.54)
		noMargen = dict(pad=72*(papeles_w[i_pap] - 2*max(self.r_disc))/2/2.54, h_pad=0, w_pad=0)
		self.f.set_tight_layout(noMargen)
		self.f.suptitle('test title')
		self.f.savefig(fich, format='pdf', dpi='90')
		fich.close()

	def mostrarAyuda(self):
		self.ayuda = not self.ayuda
		if self.ayuda:
			self.helpButton.state(["pressed"])
			self.config(cursor="question_arrow")
		else:
			self.helpButton.state(["!pressed"])
			self.config(cursor="")

	def initText(self):
		self.curTip = StringVar()
		self.ArcSpi = StringVar()
		self.LogSpi = StringVar()
		self.aaa = StringVar()
		self.bbb = StringVar()
		self.ccc = StringVar()
		self.Lma = StringVar()
		self.fre = StringVar()
		self.Mir = StringVar()
		self.Sou = StringVar()
		self.Gen = StringVar()
		self.lenlen = StringVar()
		self.radrad = StringVar()
		self.error = StringVar()

	def updateText(self, lang):

		self.lang = lang

		if lang == 0:
			self.espButton.state(["pressed"])
			self.engButton.state(["!pressed"])
		else:
			self.engButton.state(["pressed"])
			self.espButton.state(["!pressed"])


		self.stringText = {'curTip': ["Tipo de curva", "Curve type"],'ArcSpi': ["Espiral de Arquímedes", "Archimedean spiral     "],'LogSpi': ["Espiral logarítmica", "Logarithmic spiral"],'aaa': ["a (cm)", "a (cm)"],'bbb': ["b (cm/rad)", "b (cm/rad)"],'ccc': ["c", "c"],'Lma': ["Lmax (cm)", "Lmax (cm)"],'fre': ["frec (MHz)", "freq (MHz)"],'LmaToo': ["Longitud máxima de cada brazo de la antena", "Maximum length of each antenna's branch"],'FreToo': ["Frecuencia de diseño (aumentar para disminuir la longitud de los segmentos)", "Design frequency (increase for decreasing segment length)"],'Mir': ["Espejar", "Mirror"],'MirToo': ["Crea otra rama de la espiral girada 180º", "Create another spiral branch, twisted 180º"],'Sou': ["Colocar fuente", "Put source"],'SouToo': ["Une las dos mitades y crea una fuente NEC2 en el centro", "Join both halves and create a NEC2 source at the middle"],'Gen': ["Generar", "Generate"],'GenToo': ["Genera la espiral con los parámetros indicados", "Generate spiral following given parameters"],'NEC': ["NEC", "NEC"],'NECToo': ["Guarda la espiral como archivo NEC2", "Save the spiral as a NEC2 file"],'PDF': ["PDF", "PDF"],'PDFToo': ["Imprime la espiral a tamaño real en un documento PDF (máximo A0)", "Print the real sized spiral into a PDF document (A0 maximum)"],'HHH': ["H", "H"], 'lenlen': ["Longitud:", "Length:"], 'radrad': ["Radio:", "Radius:"], 'error': ["No se permiten valores negativos de b o c", "Negative values of b or c are not allowed"]}

		self.curTip.set(self.stringText['curTip'][self.lang])
		self.ArcSpi.set(self.stringText['ArcSpi'][self.lang])
		self.LogSpi.set(self.stringText['LogSpi'][self.lang])
		self.aaa.set(self.stringText['aaa'][self.lang])
		self.bbb.set(self.stringText['bbb'][self.lang])
		self.ccc.set(self.stringText['ccc'][self.lang])
		self.Lma.set(self.stringText['Lma'][self.lang])
		self.fre.set(self.stringText['fre'][self.lang])
		self.Mir.set(self.stringText['Mir'][self.lang])
		self.Sou.set(self.stringText['Sou'][self.lang])
		self.Gen.set(self.stringText['Gen'][self.lang])
		self.lenlen.set(self.stringText['lenlen'][self.lang])
		self.radrad.set(self.stringText['radrad'][self.lang])
		self.error.set(self.stringText['error'][self.lang])

	def initUI(self):

		self.initText()

		self.parent.title("PySAD")
		self.style = Style()
		self.style.theme_use("clam")

		self.pack(fill=BOTH, expand=1)

		barraLateral = Frame(self, borderwidth=1)
		barraLateral.pack(side=RIGHT, padx=5, pady=5)

		idiomaFrame = Frame(barraLateral, relief=FLAT)
		idiomaFrame.pack(side=TOP)

		self.espButton = Button(idiomaFrame, text="es", width=0, command=lambda: self.updateText(0))
		self.espButton.grid(row=0, column=0)
		self.engButton = Button(idiomaFrame, text="en", width=0, command=lambda: self.updateText(1))
		self.engButton.grid(row=0, column=1)

		self.updateText(0)

		editarFrame = Frame(barraLateral, relief=RAISED, borderwidth=1, width=1000)
		editarFrame.pack(fill=BOTH, expand=1, side=TOP, padx=5, pady=5)

		self.tipoCurva = IntVar()

		tituloSelector = Label(editarFrame, textvariable=self.curTip)
		tituloSelector.grid(row=0,columnspan=2, padx=2, pady=4)	
		Radiobutton(editarFrame, textvariable=self.ArcSpi, variable=self.tipoCurva , value=1, command=self.cambiaFormula, width=17).grid(row=1,columnspan=2,sticky=W,padx=4)
		Radiobutton(editarFrame, textvariable=self.LogSpi, variable=self.tipoCurva , value=2, command=self.cambiaFormula).grid(row=2,columnspan=2,sticky=W,padx=4)

		self.formulaLabel = Label(editarFrame)
		self.formulaLabel.grid(row=4, columnspan=2, pady=4)

		Label(editarFrame,textvariable=self.aaa).grid(row=5, column=0,pady=2)
		Label(editarFrame,textvariable=self.bbb).grid(row=6, column=0,pady=2)
		self.labelC = Label(editarFrame,textvariable=self.ccc)
		self.labelC.grid(row=7, column=0,pady=2)
		self.labelC.config(state=DISABLED)
		Label(editarFrame,textvariable=self.Lma).grid(row=8, column=0,pady=2)
		Label(editarFrame,textvariable=self.fre).grid(row=9, column=0,pady=2)

		parA = Entry(editarFrame,width=4,textvariable=self.a)
		parA.grid(row=5, column=1, sticky=W)

		parB = Entry(editarFrame,width=4,textvariable=self.b)
		parB.grid(row=6, column=1, sticky=W)

		self.parC = Entry(editarFrame,width=4,textvariable=self.c)
		self.parC.grid(row=7, column=1, sticky=W)
		self.parC.config(state=DISABLED)

		lMax = Entry(editarFrame,width=4,textvariable=self.lMax)
		lMax.grid(row=8, column=1, sticky=W)
		self.createToolTip(lMax, self.stringText['LmaToo'])	

		frec = Entry(editarFrame,width=4,textvariable=self.frec)
		frec.grid(row=9, column=1, sticky=W)
		self.createToolTip(frec, self.stringText['FreToo'])	

		self.espejar = IntVar()
		checkEspejar = Checkbutton(editarFrame, textvariable=self.Mir, variable=self.espejar, command=self.activarFuente)
		checkEspejar.grid(row=10, columnspan=2, pady=2, sticky=W, padx=4)
		self.createToolTip(checkEspejar, self.stringText['MirToo'])

		self.fuente = IntVar()
		self.checkFuente = Checkbutton(editarFrame, textvariable=self.Sou, state=DISABLED, variable=self.fuente)
		self.checkFuente.grid(row=11, columnspan=2, pady=2, sticky=W, padx=4)
		self.createToolTip(self.checkFuente, self.stringText['SouToo'])
		
		okButton = Button(editarFrame, textvariable=self.Gen, command=self.regraficar)
		okButton.grid(row=12, columnspan=2, pady=5)
		self.createToolTip(okButton, self.stringText['GenToo'])

		self.frame2 = Frame(self, borderwidth=1)
		self.frame2.pack(fill=BOTH, expand=1, side=LEFT, padx=5, pady=5)

		self.canvas = FigureCanvasTkAgg(self.f, master=self.frame2)
		self.canvas.get_tk_widget().pack(side=TOP,fill=BOTH, expand=1, padx=10, pady=10)

		frameGuardar = Frame(barraLateral, relief=FLAT, borderwidth=1)
		frameGuardar.pack(fill=BOTH, expand=1, side=BOTTOM, padx=5, pady=5)

		icGuardar = PhotoImage(data='''R0lGODlhEAAQAIABADMzM////yH5BAEKAAEALAAAAAAQABAAAAIlDI55wchvQJQOxontUktTbkHcSJZkGCao161N5U5SLNM1vZlOAQA7''')
		saveButtonNEC = Button(frameGuardar, text=self.stringText['NEC'][0], image=icGuardar, compound=LEFT, command=self.escribirFichero, width=3)
		saveButtonNEC.image = icGuardar
		saveButtonNEC.grid(row=0, column=0, pady=2, padx=2, sticky=W)
		self.createToolTip(saveButtonNEC, self.stringText['NECToo'])

		saveButtonPDF = Button(frameGuardar, text=self.stringText['PDF'][0], image=icGuardar, compound=LEFT, command=self.escribirPDF, width=3)
		saveButtonPDF.image = icGuardar
		saveButtonPDF.grid(row=0, column=2, pady=2, padx=2, sticky=E)
		self.createToolTip(saveButtonPDF, self.stringText['PDFToo'])

		self.helpButton = Button(frameGuardar, text="?", command=self.mostrarAyuda, width=2)
		self.helpButton.grid(row=0, column=3, pady=2, padx=2, sticky=E)

		frame3 = Frame(barraLateral, relief=RAISED, borderwidth=1)
		frame3.pack(fill=BOTH, expand=1, side=BOTTOM, padx=5, pady=5)

		Label(frame3,textvariable=self.lenlen).grid(row=1, column=0,pady=4,padx=12)
		Label(frame3,textvariable=self.radrad).grid(row=2, column=0,pady=4,padx=12)
		Label(frame3,textvariable=self.StringLongitud).grid(row=1, column=1,pady=4)
		Label(frame3,textvariable=self.StringRadio).grid(row=2, column=1,pady=4)

	def onExit(self):
		self.quit()




def main():
  
	root = Tk()
	#root.geometry("600x600+300+300")
	app = Principal(root)
	root.mainloop()  


if __name__ == '__main__':
	main()
