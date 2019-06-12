#! /usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import tkinter.filedialog

import math
import datetime
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import RectangleSelector
from matplotlib.backend_bases import cursors
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.figure import Figure

from utils.prosimu import prosimu
from utils.infomassifs import infomassifs
import proReader_mini

import pickle

constante_sampling = proReader_mini.constante_sampling

class GraphStandard(Toplevel):
    def __init__(self,**Arguments):
        Toplevel.__init__(self, **Arguments)
        self.title('GUI PROreader CEN')
        
        self.taille_x=900
        self.taille_y=700
        self.geometry('900x700')

        self.x=''
        self.y=''
        self.test=''
        self.variable=''
        self.variable_souris=''
        self.date=''
        self.datedeb=''
        self.datefin=''
        self.date1_zoom=''
        self.date1_zoom_old=''
        self.boolzoom=False
        #self.boolzoomdate=False
        self.bool_profil=False
        self.bool_layer=False
        self.figclear=True
        self.first_profil=True
        self.width_rect=0.01
        self.rectangle_choix=''
        self.filename=''
        self.list_choix=[None,None,None,None]
        self.list_massif_num=[]
        self.list_massif_nom=[]
        self.liste_variable=[]
        self.liste_variable_for_pres=[]
        self.pro=''
        self.Tableau=''
        self.point_choisi=''
        self.var_choix1=''
        self.var_choix2=''
        self.var_sup=[]
        self.valeur_choisie1=''
        self.valeur_choisie2=''
        self.message_filedialog='Importer un fichier PRO'
        self.type_graphique=1
        
        self.menubar = Menu()
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='French', command=self.toFrench)
        self.filemenu.add_command(label='English', command=self.toEnglish)
        self.menubar.add_cascade(label='Change Language', menu=self.filemenu)
        self.config(menu=self.menubar)
        
        self.buttonQuit = Button(self,text='Quitter', command = quit)
        self.buttonPlot = Button(self,  text='Tracer graphe', state='disabled')
        self.buttonRaz = Button(self,  text='Remise à zéro', state='disabled')
        self.buttonSave1 = Button(self,  text='Sauver graphe', state='disabled')
        self.buttonSave2 = Button(self,  text='Sauver profil', state='disabled')
        self.buttonSave3 = Button(self,  text='Pickle graphe', state='disabled')
        self.buttonSave4 = Button(self,  text='Pickle profil', state='disabled')
        self.label_var=Label(self,text='2: Variable à tracer')
        self.combobox = ttk.Combobox(self, state = 'disabled', values = '')
        style = ttk.Style()
        style.configure('TCombobox', postoffset=(0,0,200,0))
        self.label_choix_profil=Label(self,text='3: Choix variable profil')
        self.combobox_choix_profil = ttk.Combobox(self, state = 'disabled', values = '')
        self.label_reduce1=Label(self,text='4: Choix massif')
        self.combobox_reduce1 = ttk.Combobox(self, state = 'disabled', values = '')
        self.label_reduce2=Label(self,text='5: Choix altitude')
        self.combobox_reduce2 = ttk.Combobox(self, state = 'disabled', values = '')
        self.label_reduce3=Label(self,text='6: Choix angle de pente')
        self.combobox_reduce3 = ttk.Combobox(self, state = 'disabled', values = '')
        self.label_reduce4=Label(self,text='7: Choix orientation')
        self.combobox_reduce4 = ttk.Combobox(self, state = 'disabled', values = '')
        self.fig1, self.ax1 = plt.subplots(1, 1, sharex=True, sharey=True)
        self.Canevas = FigureCanvasTkAgg(self.fig1,self)
        self.fig2, self.ax2 = plt.subplots(1, 1, sharex=True, sharey=True)
        self.ax3=self.ax2.twiny()
        self.Canevas2 = FigureCanvasTkAgg(self.fig2,self)
        self.buttonOpenFile = Button(self,  text='1: Ouvrir un fichier',command=self.Ouvrir)
        self.scale_date = Scale(self, orient='horizontal', state='disabled',label='Echelle de dates')

        self.bind('<Configure>', self.onsize_test)
        self.make_list_massif()
        
    ##########################################################
    # PLACEMENT BOUTONS, LISTES DEFILANTES, ETC...
    ##########################################################
     
    def onsize_test(self,event):
        largeur = self.winfo_width()/self.taille_x
        hauteur = self.winfo_height()/self.taille_y
        self.buttonQuit.place(x=750*largeur, y=660*hauteur)
        self.buttonOpenFile.place(x=5*largeur, y=5*hauteur)
        self.buttonPlot.place(x=750*largeur, y=100*hauteur)
        self.buttonRaz.place(x=750*largeur, y=5*hauteur)
        self.buttonSave1.place(x=5*largeur, y=660*hauteur)
        self.buttonSave2.place(x=155*largeur, y=660*hauteur)
        self.buttonSave3.place(x=305*largeur, y=660*hauteur)
        self.buttonSave4.place(x=455*largeur, y=660*hauteur)
        self.label_var.place(x=200*largeur,y=5*hauteur)
        self.combobox.place(x=200*largeur, y=20*hauteur)
        self.label_choix_profil.place(x=400*largeur,y=5*hauteur)
        self.combobox_choix_profil.place(x=400*largeur, y=20*hauteur)
        self.Canevas.get_tk_widget().place(x=3*largeur,y=150*hauteur,width=502*largeur, height=500*hauteur)
        self.Canevas2.get_tk_widget().place(x=504*largeur,y=150*hauteur,width=390*largeur, height=500*hauteur)
        self.label_reduce1.place(x=75*largeur,y=50*hauteur)
        self.combobox_reduce1.place(x=75*largeur, y=65*hauteur)
        self.label_reduce2.place(x=270*largeur,y=50*hauteur)
        self.combobox_reduce2.place(x=270*largeur, y=65*hauteur)
        self.label_reduce3.place(x=470*largeur,y=50*hauteur)
        self.combobox_reduce3.place(x=470*largeur, y=65*hauteur)
        self.label_reduce4.place(x=670*largeur,y=50*hauteur)
        self.combobox_reduce4.place(x=670*largeur, y=65*hauteur)
        self.scale_date.place(x=30*largeur,y=100*hauteur)
        self.scale_date.config(length=380*largeur)   

    ##########################################################
    # TRADUCTION
    ##########################################################
    def toFrench(self):
        self.buttonQuit.config(text='Quitter')
        self.buttonOpenFile.config(text='1: Ouvrir un fichier')
        self.buttonPlot.config(text='Tracer graphe')
        self.buttonRaz.config(text='Remise à zéro')
        self.buttonSave1.config(text='Sauver graphe')
        self.buttonSave2.config(text='Sauver profil')
        self.buttonSave3.config(text='Pickle graphe')
        self.buttonSave4.config(text='Pickle profil')
        self.label_var.config(text='2: Variable à tracer')
        self.label_choix_profil.config(text='3: Choix variable profil')
        self.label_reduce1.config(text='4: Choix massif')
        self.label_reduce2.config(text='5: Choix altitude')
        self.label_reduce3.config(text='6: Choix angle de pente')
        self.label_reduce4.config(text='7: Choix orientation')
        self.scale_date.config(label='Echelle de dates')
        
        self.message_filedialog='Importer un fichier PRO'

    def toEnglish(self):
        self.buttonQuit.config(text='Exit')
        self.buttonOpenFile.config(text='1: Open File')
        self.buttonPlot.config(text='Plot')
        self.buttonRaz.config(text='Reset')
        self.buttonSave1.config(text='Save graph')
        self.buttonSave2.config(text='Save profile')
        self.buttonSave3.config(text='Pickle graph')
        self.buttonSave4.config(text='Pickle profile')
        self.label_var.config(text='2: Variable to plot')
        self.label_choix_profil.config(text='3: Variable for Profile')
        self.label_reduce1.config(text='4: Choose massif')
        self.label_reduce2.config(text='5: Choose altitude')
        self.label_reduce3.config(text='6: Choose slope')
        self.label_reduce4.config(text='7: Choose orientation')
        self.scale_date.config(label='Dates scale')
        
        self.message_filedialog='Import a PRO File'
        
    ##########################################################
    # GESTION DU PROFIL INTERACTIF
    ##########################################################
    def motion(self,event):
        if self.bool_desactive_motion:
            return
        if (event.inaxes == self.ax1):
            #date_souris=self.date[min(math.floor(event.xdata),len(self.date)-1)]
            date_souris=self.date[min(np.where(self.intime)[0][int(math.floor(event.xdata))],len(self.date)-1)]
            hauteur_souris=event.ydata
            self.ax2.clear()
            if self.profil_complet:
                self.ax3.clear()
                self.pro.plot_date_complet(self.ax2, self.ax3, self.variable_souris, date_souris, hauteur_souris, cbar_show=self.first_profil, bool_layer=self.bool_layer)    
            else:
                self.pro.plot_date(self.ax2, self.variable_souris, date_souris, hauteur_souris, bool_layer=self.bool_layer)
            self.Canevas2.draw()
            self.buttonSave2.config(state='normal',command=self.Save_profil)
            self.buttonSave4.config(state='normal',command=self.Pickle_profil)
            plt.close(self.fig2)
            self.first_profil=False
            
    def motion_zoom(self,event):
        if self.bool_desactive_motion:
            return
        if (event.inaxes == self.ax1):
            hauteur_souris=event.ydata
            '''if self.boolzoom:
                ecart=self.datedeb-self.date1_zoom_old
                date_souris=self.date[min(math.floor(event.xdata),len(self.date)-1)]-ecart
            else:
                ecart=self.datedeb-self.date1_zoom
                date_souris=self.date[min(math.floor(event.xdata),len(self.date)-1)]-ecart'''
            date_souris=self.date[min(np.where(self.intime)[0][int(math.floor(event.xdata))],len(self.date)-1)]
            self.ax2.clear()
            top_zoom=self.pro.get_topplot(self.variable, self.date1_zoom, self.date2_zoom)

            if self.profil_complet:
                self.ax3.clear()
                self.pro.plot_date_complet(self.ax2, self.ax3, self.variable_souris, date_souris, hauteur_souris, cbar_show=self.first_profil, top=top_zoom, bool_layer=self.bool_layer)
            else:    
                self.pro.plot_date(self.ax2, self.variable_souris, date_souris, hauteur_souris, top=top_zoom, bool_layer=self.bool_layer)

            self.Canevas2.draw()
            plt.close(self.fig2)
            self.first_profil=False
            
    def on_button_press(self, event):
        if self.bool_desactive_motion:
            return
        if (event.inaxes == self.ax1):
            self.boolzoom=True
            self.x_date1_zoom=event.xdata
            self.date1_zoom = self.date[min(np.where(self.intime)[0][int(math.floor(event.xdata))],len(self.date)-1)]
            '''if self.boolzoomdate:
                ecart=self.datedeb-self.date1_zoom
                self.date1_zoom_old=self.date1_zoom
                self.date1_zoom=self.date[min(math.floor(event.xdata),len(self.date)-1)]-ecart
            else:
                self.date1_zoom=self.date[min(math.floor(event.xdata),len(self.date)-1)]'''
            bottom, top = self.ax1.get_ylim()
            self.rectangle_choix=self.ax1.add_patch(matplotlib.patches.Rectangle((self.x_date1_zoom, bottom), self.width_rect, top-bottom,alpha=0.1))
            self.Canevas.draw()

    def on_move_press(self, event):
        if self.bool_desactive_motion:
            return
        if self.boolzoom is False:
            return
        if (event.inaxes == self.ax1):
            hauteur = self.winfo_height()/self.taille_y
            self.width_rect=abs(event.xdata-self.x_date1_zoom)
            height_rect=500*hauteur
            self.rectangle_choix.set_width(self.width_rect)
            if event.xdata-self.x_date1_zoom <0:
                self.rectangle_choix.set_x(event.xdata)
            self.Canevas.draw()
            self.Canevas.flush_events()

    def on_button_release(self, event):
        if self.bool_desactive_motion:
            return
        if (event.inaxes == self.ax1):
            self.width_rect=0.01
            
            self.date2_zoom = self.date[min(np.where(self.intime)[0][int(math.floor(event.xdata))],len(self.date)-1)]

            '''if self.boolzoomdate:
                ecart=self.datedeb-self.date1_zoom_old
                self.date2_zoom=self.date[min(math.floor(event.xdata),len(self.date)-1)]-ecart
            else:
                self.date2_zoom=self.date[min(math.floor(event.xdata),len(self.date)-1)]

            self.boolzoomdate=True'''
            
            largeur = self.winfo_width()/self.taille_x
            hauteur = self.winfo_height()/self.taille_y
            
            self.fig1.clear()
            self.fig1, self.ax1 = plt.subplots(1, 1, sharex=True, sharey=True)
            self.Canevas.get_tk_widget().destroy()
            self.Canevas = FigureCanvasTkAgg(self.fig1,self)
            self.Canevas.get_tk_widget().place(x=5*largeur,y=150*hauteur,width=500*largeur, height=500*hauteur)
            
            self.fig2.clear()
            self.fig2, self.ax2 = plt.subplots(1, 1, sharex=True, sharey=True)
            self.ax3=self.ax2.twiny()
            self.first_profil=True
            self.Canevas2.get_tk_widget().destroy()
            self.Canevas2 = FigureCanvasTkAgg(self.fig2,self)
            self.Canevas2.get_tk_widget().place(x=505*largeur,y=150*hauteur,width=200*largeur, height=500*hauteur)
        
            if self.date1_zoom>self.date2_zoom:
                self.date1_zoom,self.date2_zoom=self.date2_zoom,self.date1_zoom
                
            ff = prosimu(self.filename)
            if ('snow_layer' in ff.getdimvar(self.variable)):
                self.intime = self.pro.plot(self.ax1, self.variable, self.date1_zoom, self.date2_zoom, real_layers=True,legend=self.variable)
            else:
                self.intime = self.pro.plot1D(self.ax1, self.variable, self.date1_zoom, self.date2_zoom, legend=self.variable)
            self.Canevas.draw()
            self.boolzoom=False
            self.Canevas.mpl_connect('motion_notify_event', self.motion_zoom)
            self.Canevas.mpl_connect('button_press_event', self.on_button_press)
            self.Canevas.mpl_connect('motion_notify_event', self.on_move_press)
            self.Canevas.mpl_connect('button_release_event', self.on_button_release)
            
            plt.close(self.fig1)
    
    def update_plot(self,value):
        if self.bool_desactive_motion:
            ff = prosimu(self.filename)
            self.date_motion=self.date[int(value)]
            self.ax1.clear()
            self.pro.plot1D_bande(self.ax1, self.variable, date=self.date_motion, legend=self.variable)
            self.Canevas.draw()
            plt.close(self.fig1)
            self.ax2.clear()
            if self.profil_complet:
                self.ax3.clear()
                self.pro.plot_date_complet(self.ax2, self.ax3, self.variable_souris, date=self.date_motion, cbar_show=self.first_profil, bool_layer=self.bool_layer)    
            else:
                self.pro.plot_date(self.ax2, self.variable_souris, date=self.date_motion, bool_layer=self.bool_layer)
            self.Canevas2.draw()
            self.buttonSave2.config(state='normal',command=self.Save_profil)
            self.buttonSave4.config(state='normal',command=self.Pickle_profil)
            plt.close(self.fig2)
            self.clik_zoom=False
    
    ##########################################################
    # REMISE À ZERO
    ##########################################################
    def refresh_all_combo(self):
        self.combobox.config(state = 'disabled',values='')
        self.combobox.set('')
        self.combobox_choix_profil.config(state = 'disabled',values='')
        self.combobox_choix_profil.set('')
        self.combobox_reduce1.config(state = 'disabled', values = '')
        self.combobox_reduce1.set('')
        self.combobox_reduce2.config(state = 'disabled', values = '')
        self.combobox_reduce2.set('')
        self.combobox_reduce3.config(state = 'disabled', values = '')
        self.combobox_reduce3.set('')
        self.combobox_reduce4.config(state = 'disabled', values = '')
        self.combobox_reduce4.set('')
        self.list_choix=[None,None,None,None]
        self.var_sup=[]
        self.bool_profil=False

    def refresh_all_plot(self):
        largeur = self.winfo_width()/self.taille_x
        hauteur = self.winfo_height()/self.taille_y
        
        if (self.figclear == False):
            self.fig1.clear()
            self.fig1, self.ax1 = plt.subplots(1, 1, sharex=True, sharey=True)
            self.Canevas.get_tk_widget().destroy()
            self.Canevas = FigureCanvasTkAgg(self.fig1,self)
            self.Canevas.get_tk_widget().place(x=5*largeur,y=150*hauteur,width=500*largeur, height=500*hauteur)  
            self.fig2.clear()
            self.fig2, self.ax2 = plt.subplots(1, 1, sharex=True, sharey=True)
            self.ax3=self.ax2.twiny()
            self.Canevas2.get_tk_widget().destroy()
            self.Canevas2 = FigureCanvasTkAgg(self.fig2,self)
            self.Canevas2.get_tk_widget().place(x=505*largeur,y=150*hauteur,width=200*largeur, height=500*hauteur)
        
        self.buttonPlot.config(state='disabled')
        self.buttonSave1.config(state='disabled')
        self.buttonSave2.config(state='disabled')
        self.buttonSave3.config(state='disabled')
        self.buttonSave4.config(state='disabled')
        self.scale_date.config(from_=0, to=0,state='disabled')
        self.figclear=True
        self.first_profil=True
        
    def raz(self):
        self.refresh_all_combo()
        self.refresh_all_plot()
        self.liste_variable=[]
        self.liste_variable_for_pres=[]
        
    ##########################################################
    # RECUPERATION FICHIER
    ##########################################################
    def Ouvrir(self):
        
        
        try:
            # call a dummy dialog with an impossible option to initialize the file
            # dialog without really getting a dialog window; this will throw a
            # TclError, so we need a try...except :
            try:
                tk.call('tk_getOpenFile', '-foobarbaz')
            except TclError:
                pass
            # now set the magic variables accordingly
            tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
            tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
        except:
            pass
        
        
        
        
        self.filename = tkinter.filedialog.askopenfilename(title=self.message_filedialog,filetypes=[('PRO files','.nc'),('all files','.*')])
        print(self.filename)
        self.raz()

        ff = prosimu(self.filename)
        self.date=ff.readtime()
        self.datedeb=self.date[0]
        self.datefin=self.date[len(self.date)-1]
        if len(self.date) > constante_sampling: 
            messagebox.showinfo('Time > '+str(constante_sampling), 'automatic sampling to avoid too long treatment')
        
        self.pro = proReader_mini.ProReader_mini(ncfile=self.filename)
        listvariables = ff.listvar()
        self.Tableau=self.pro.get_choix(self.filename)

        for i in range(len(listvariables)):
            if(listvariables[i]==(listvariables[i].upper()) and listvariables[i]!='ZS'):
                if ff.getattr(listvariables[i],'long_name')!='':
                    self.liste_variable_for_pres.append(ff.getattr(listvariables[i],'long_name'))
                    self.liste_variable.append(listvariables[i])
                else:
                    self.liste_variable_for_pres.append(listvariables[i])
                    self.liste_variable.append(listvariables[i])
                    
        self.recup(self)
        
    ##########################################################
    # CHOIX VARIABLE
    ##########################################################
    def recup(self,event):
        def suite(event):
            variable_for_pres=self.combobox.get()
            self.variable=self.liste_variable[self.liste_variable_for_pres.index(variable_for_pres)]
            self.var_sup.append(self.variable)
            print(self.variable)
            if self.bool_profil:
                self.pro = proReader_mini.ProReader_mini(ncfile=self.filename, var=self.variable, point=int(self.point_choisi),var_sup=self.var_sup)
            '''self.reduce1(self)'''
                
            ff = prosimu(self.filename)
            self.profil_complet=False
            if ({'SNOWTYPE','SNOWRAM'}.issubset(set(ff.listvar()))):
                self.profil_complet=True
            
            liste_pres=[]
            liste=list(set(ff.listvar())-{'SNOWTYPE','SNOWRAM'})
            for var in liste:
                if 'snow_layer' in list(ff.getdimvar(var)):
                    liste_pres.append(self.liste_variable_for_pres[self.liste_variable.index(var)])

            self.combobox_choix_profil.config(values = liste_pres)
            self.combobox_choix_profil.config(state = "readonly")
            self.combobox_choix_profil.bind('<<ComboboxSelected>>', self.choix_profil)
            
        self.combobox.config(state ='readonly', values=self.liste_variable_for_pres)
        self.combobox.bind('<<ComboboxSelected>>', suite)

    def make_list_massif(self):
        self.list_massif_num=[]
        self.list_massif_nom=[]
        IM=infomassifs()
        listmassif = IM.getListMassif_of_region('all')
        for massif in listmassif:
            self.list_massif_num.append(massif)
            self.list_massif_nom.append(str(IM.getMassifName(massif).decode('UTF-8')))
            
    ##########################################################
    # CHOIX POINT
    ##########################################################
    def reduce1(self,event):
        self.combobox_reduce1.config(state = "readonly")
        liste=[]
        for it_massif in list(set(self.Tableau[0,:])):
            indice=self.list_massif_num.index(it_massif)
            liste.append(self.list_massif_nom[indice])
        self.combobox_reduce1.config(values = liste)
        self.combobox_reduce1.bind('<<ComboboxSelected>>', self.reduce2)
        if self.bool_profil:
            self.choix_point()

    def reduce2(self,event):
        self.combobox_reduce2.config(state = "readonly")
        nom_massif=self.combobox_reduce1.get()
        indice=self.list_massif_nom.index(nom_massif)
        num_massif=self.list_massif_num[indice]
        self.list_choix[0]=float(num_massif)
        liste=list(set(self.Tableau[1,self.Tableau[0,:]==num_massif]))
        self.combobox_reduce2.config(values = liste)
        self.combobox_reduce2.bind('<<ComboboxSelected>>', self.reduce3)
        if self.bool_profil:       
            self.choix_point()    
        
    def reduce3(self,event):
        self.combobox_reduce3.config(state = "readonly")
        altitude=self.combobox_reduce2.get()
        self.list_choix[1]=float(altitude)
        n=len(self.Tableau[0,:])
        A=self.Tableau[0,:]==[self.list_choix[0]]*n
        B=self.Tableau[1,:]==[self.list_choix[1]]*n
        indices = A & B
        
        liste=list(set(self.Tableau[2,indices]))
        self.combobox_reduce3.config(values = liste)
        self.combobox_reduce3.bind('<<ComboboxSelected>>', self.reduce4)
        if self.bool_profil:
            self.choix_point()
        
    def reduce4(self,event):
        self.combobox_reduce4.config(state = "readonly")
        pente=self.combobox_reduce3.get()
        self.list_choix[2]=float(pente)
        n=len(self.Tableau[0,:])
        A=self.Tableau[0,:]==[self.list_choix[0]]*n
        B=self.Tableau[1,:]==[self.list_choix[1]]*n
        C=self.Tableau[2,:]==[self.list_choix[2]]*n
        indices = A & B & C

        liste=list(set(self.Tableau[3,indices]))
        self.combobox_reduce4.config(values = liste)
        self.combobox_reduce4.bind('<<ComboboxSelected>>', self.finalisation_reduce)
        if self.bool_profil:
            self.choix_point()

    def choix_point(self):
        n=len(self.Tableau[0,:])
        A=self.Tableau[0,:]==[self.list_choix[0]]*n
        B=self.Tableau[1,:]==[self.list_choix[1]]*n
        C=self.Tableau[2,:]==[self.list_choix[2]]*n
        D=self.Tableau[3,:]==[self.list_choix[3]]*n
        indices = A & B & C & D
        if True not in list(indices):
            self.buttonPlot.config(state='disabled')
        else:
            self.point_choisi = list(indices).index(True)
            if self.bool_profil==True:
                self.buttonPlot.config(state='normal',command=self.Plotage)
        
    def finalisation_reduce(self,event):
        orientation=self.combobox_reduce4.get()
        self.list_choix[3]=float(orientation)
        self.choix_point()
        
    ##########################################################
    # CHOIX VARIABLE PROFIL
    ##########################################################
    def choix_profil(self,event):
        variable_souris_for_pres=self.combobox_choix_profil.get()
        self.variable_souris=self.liste_variable[self.liste_variable_for_pres.index(variable_souris_for_pres)]
        if self.profil_complet:
            self.var_sup.extend([self.variable_souris,'SNOWTYPE','SNOWRAM'])
        else:
            self.var_sup.append(self.variable_souris)
        self.bool_profil=True
        
        if (len(self.Tableau[0])+len(self.Tableau[1])+len(self.Tableau[2])+len(self.Tableau[3])==4):
            self.point_choisi=0
            self.combobox_reduce1.config(state = 'disabled', values = '')
            self.combobox_reduce2.config(state = 'disabled', values = '')
            self.combobox_reduce3.config(state = 'disabled', values = '')
            self.combobox_reduce4.config(state = 'disabled', values = '')
            if self.Tableau[0]==[-10.]:
                self.combobox_reduce1.set('inconnu')
            else:
                self.combobox_reduce1.set(self.Tableau[0][0])
            if self.Tableau[1]==[-10.]:
                self.combobox_reduce2.set('inconnu')
            else:
                self.combobox_reduce2.set(self.Tableau[1][0])
            if self.Tableau[2]==[-10.]:
                self.combobox_reduce3.set('inconnu')
            else:
                self.combobox_reduce3.set(self.Tableau[2][0])
            if self.Tableau[3]==[-10.]:
                self.combobox_reduce4.set('inconnu')
            else:
                self.combobox_reduce4.set(self.Tableau[3][0])
            self.buttonPlot.config(state='normal',command=self.Plotage)
        else:
            self.reduce1(self)
        
    ##########################################################
    # TRACE
    ##########################################################
    def Plotage(self):
        self.boolzoom=False
        #self.boolzoomdate=False
        self.pro = proReader_mini.ProReader_mini(ncfile=self.filename, var=self.variable, point=int(self.point_choisi),var_sup=self.var_sup)
        largeur = self.winfo_width()/self.taille_x
        hauteur = self.winfo_height()/self.taille_y
        self.fig1.clear()
        self.ax1.clear()
        self.fig1, self.ax1 = plt.subplots(1, 1, sharex=True, sharey=True)
        self.Canevas.get_tk_widget().destroy()
        self.Canevas = FigureCanvasTkAgg(self.fig1,self)
        self.Canevas.get_tk_widget().place(x=5*largeur,y=150*hauteur,width=500*largeur, height=500*hauteur)
        ff = prosimu(self.filename)
        print(self.variable)
        if ('snow_layer' in ff.getdimvar(self.variable)):
            self.intime = self.pro.plot(self.ax1, self.variable, self.datedeb, self.datefin, real_layers=True,legend=self.variable)
            self.bool_layer=True
            self.scale_date.config(from_=0, to=0,state='disabled')
            self.bool_desactive_motion = False
        elif('bands' in ff.getdimvar(self.variable)):
            self.pro.plot1D_bande(self.ax1, self.variable, self.datedeb, legend=self.variable)
            self.bool_layer=False
            if self.profil_complet:
                self.pro.plot_date_complet(self.ax2, self.ax3, self.variable_souris, self.datedeb, cbar_show=self.first_profil, bool_layer=self.bool_layer)    
            else:
                self.pro.plot_date(self.ax2, self.variable_souris, self.datedeb, bool_layer=self.bool_layer)
            self.Canevas2.draw()
            self.buttonSave2.config(state='normal',command=self.Save_profil)
            self.buttonSave4.config(state='normal',command=self.Pickle_profil)
            plt.close(self.fig2)
            self.scale_date.config(from_=0, to=(len(self.date)-1),state='normal',showvalue=0,command=self.update_plot, variable=IntVar)
            self.bool_desactive_motion = True
        else:
            self.intime = self.pro.plot1D(self.ax1, self.variable, self.datedeb, self.datefin, legend=self.variable)
            self.bool_layer=False
            self.scale_date.config(from_=0, to=0,state='disabled')
            self.bool_desactive_motion = False
        self.Canevas.draw()
        self.Canevas.mpl_connect('motion_notify_event', self.motion)
        self.Canevas.mpl_connect('button_press_event', self.on_button_press)
        self.Canevas.mpl_connect('motion_notify_event', self.on_move_press)
        self.Canevas.mpl_connect('button_release_event', self.on_button_release)
        plt.close(self.fig1)
        self.buttonRaz.config(state='normal',command=self.raz)
        self.buttonSave1.config(state='normal',command=self.Save_plot)
        #self.buttonSave3.config(state='normal',command=self.Pickle_plot)
        self.figclear=False
        
    ##########################################################
    # SAUVEGARDE
    ##########################################################
    def Save_plot(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*'),
                                ('jpeg image', '.jpg'), ('png image', '.png'),
                                ('tiff image', '.tiff'), ('bmp image', '.bmp')]

        options['initialfile'] = 'graph_proreader.png'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return self.fig1.savefig(filename,bbox_inches='tight')
        
    def Save_profil(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*'),
                                ('jpeg image', '.jpg'), ('png image', '.png'),
                                ('tiff image', '.tiff'), ('bmp image', '.bmp')]

        options['initialfile'] = 'profil_proreader.png'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return self.fig2.savefig(filename,bbox_inches='tight')
        
    def Pickle_plot(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*')]

        options['initialfile'] = 'mypicklefile'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return pickle.dump(self.fig1, open(filename, 'wb'))
        
    def Pickle_profil(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*')]

        options['initialfile'] = 'mypicklefile'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return pickle.dump(self.fig2, open(filename, 'wb'))
        
'''#############################################################################################
################################################################################################
#
#
#
#
#
################################################################################################
#############################################################################################'''        
class GraphMassif(Toplevel):
    def __init__(self,**Arguments):
        Toplevel.__init__(self, **Arguments)
        self.title('GUI PROreader CEN')
        
        self.taille_x=900
        self.taille_y=700
        self.geometry('900x700')

        self.x=''
        self.y=''
        self.test=''
        self.variable=''
        self.variable_souris=''
        self.date=''
        self.datedeb=''
        self.datefin=''
        self.date1_zoom=''
        self.date1_zoom_old=''
        self.date_motion=None
        #self.boolzoom=False
        #self.boolzoomdate=False
        self.bool_profil=False
        self.bool_layer=False
        self.figclear=True
        self.first_profil=True
        self.width_rect=0.01
        self.rectangle_choix=''
        self.filename=''
        self.list_choix=[None,None,None]
        self.list_massif_num=[]
        self.list_massif_nom=[]
        self.liste_variable=[]
        self.liste_variable_for_pres=[]
        self.pro=''
        self.Tableau=''
        self.liste_points=''
        self.var_choix1=''
        self.var_choix2=''
        self.var_sup=[]
        self.valeur_choisie1=''
        self.valeur_choisie2=''
        self.message_filedialog='Importer un fichier PRO'
        self.type_graphique=1
        
        self.menubar = Menu()
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='French', command=self.toFrench)
        self.filemenu.add_command(label='English', command=self.toEnglish)
        self.menubar.add_cascade(label='Change Language', menu=self.filemenu)
        self.config(menu=self.menubar)
        
        self.buttonQuit = Button(self,text='Quitter', command = quit)
        self.buttonPlot = Button(self,  text='Tracer graphe', state='disabled')
        self.buttonRaz = Button(self,  text='Remise à zéro', state='disabled')
        self.buttonSave1 = Button(self,  text='Sauver graphe', state='disabled')
        self.buttonSave2 = Button(self,  text='Sauver profil', state='disabled')
        self.buttonSave3 = Button(self,  text='Pickle graphe', state='disabled')
        self.buttonSave4 = Button(self,  text='Pickle profil', state='disabled')
        self.label_var=Label(self,text='2: Variable à tracer')
        self.combobox = ttk.Combobox(self, state = 'disabled', values = '')
        style = ttk.Style()
        style.configure('TCombobox', postoffset=(0,0,200,0))
        self.label_choix_profil=Label(self,text='3: Choix variable profil')
        self.combobox_choix_profil = ttk.Combobox(self, state = 'disabled', values = '')
        self.label_reduce2=Label(self,text='4: Choix altitude')
        self.combobox_reduce2 = ttk.Combobox(self, state = 'disabled', values = '')
        self.label_reduce3=Label(self,text='5: Choix angle de pente')
        self.combobox_reduce3 = ttk.Combobox(self, state = 'disabled', values = '')
        self.label_reduce4=Label(self,text='6: Choix orientation')
        self.combobox_reduce4 = ttk.Combobox(self, state = 'disabled', values = '')
        self.fig1, self.ax1 = plt.subplots(1, 1, sharex=True, sharey=True)
        self.Canevas = FigureCanvasTkAgg(self.fig1,self)
        self.fig2, self.ax2 = plt.subplots(1, 1, sharex=True, sharey=True)
        self.ax3=self.ax2.twiny()
        self.Canevas2 = FigureCanvasTkAgg(self.fig2,self)
        self.scale_date = Scale(self, orient='horizontal', state='disabled',label='Echelle de dates')
        self.buttonOpenFile = Button(self,  text='1: Ouvrir un fichier',command=self.Ouvrir)

        self.bind('<Configure>', self.onsize_test)
        self.make_list_massif()
        
    ##########################################################
    # PLACEMENT BOUTONS, LISTES DEFILANTES, ETC...
    ##########################################################
     
    def onsize_test(self,event):
        largeur = self.winfo_width()/self.taille_x
        hauteur = self.winfo_height()/self.taille_y
        self.buttonQuit.place(x=750*largeur, y=660*hauteur)
        self.buttonOpenFile.place(x=5*largeur, y=5*hauteur)
        self.buttonPlot.place(x=750*largeur, y=100*hauteur)
        self.buttonRaz.place(x=750*largeur, y=5*hauteur)
        self.buttonSave1.place(x=5*largeur, y=660*hauteur)
        self.buttonSave2.place(x=155*largeur, y=660*hauteur)
        self.buttonSave3.place(x=305*largeur, y=660*hauteur)
        self.buttonSave4.place(x=455*largeur, y=660*hauteur)
        self.label_var.place(x=200*largeur,y=5*hauteur)
        self.combobox.place(x=200*largeur, y=20*hauteur)
        self.label_choix_profil.place(x=400*largeur,y=5*hauteur)
        self.combobox_choix_profil.place(x=400*largeur, y=20*hauteur)
        self.Canevas.get_tk_widget().place(x=3*largeur,y=160*hauteur,width=502*largeur, height=500*hauteur)
        self.Canevas2.get_tk_widget().place(x=504*largeur,y=160*hauteur,width=390*largeur, height=500*hauteur)
        self.label_reduce2.place(x=75*largeur,y=45*hauteur)
        self.combobox_reduce2.place(x=75*largeur, y=60*hauteur)
        self.label_reduce3.place(x=270*largeur,y=45*hauteur)
        self.combobox_reduce3.place(x=270*largeur, y=60*hauteur)
        self.label_reduce4.place(x=470*largeur,y=45*hauteur)
        self.combobox_reduce4.place(x=470*largeur, y=60*hauteur)   
        self.scale_date.place(x=30*largeur,y=100*hauteur)
        self.scale_date.config(length=380*largeur)
    ##########################################################
    # TRADUCTION
    ##########################################################
    def toFrench(self):
        self.buttonQuit.config(text='Quitter')
        self.buttonOpenFile.config(text='1: Ouvrir un fichier')
        self.buttonPlot.config(text='Tracer graphe')
        self.buttonRaz.config(text='Remise à zéro')
        self.buttonSave1.config(text='Sauver graphe')
        self.buttonSave2.config(text='Sauver profil')
        self.buttonSave3.config(text='Pickle graphe')
        self.buttonSave4.config(text='Pickle profil')
        self.label_var.config(text='2: Variable à tracer')
        self.label_choix_profil.config(text='3: Choix variable profil')
        self.label_reduce2.config(text='4: Choix altitude')
        self.label_reduce3.config(text='5: Choix angle de pente')
        self.label_reduce4.config(text='6: Choix orientation')
        self.scale_date.config(label='Echelle de dates')
        
        self.message_filedialog='Importer un fichier PRO'

    def toEnglish(self):
        self.buttonQuit.config(text='Exit')
        self.buttonOpenFile.config(text='1: Open File')
        self.buttonPlot.config(text='Plot')
        self.buttonRaz.config(text='Reset')
        self.buttonSave1.config(text='Save graph')
        self.buttonSave2.config(text='Save profile')
        self.buttonSave3.config(text='Pickle graph')
        self.buttonSave4.config(text='Pickle profile')
        self.label_var.config(text='2: Variable to plot')
        self.label_choix_profil.config(text='3: Variable for Profile')
        self.label_reduce2.config(text='4: Choose altitude')
        self.label_reduce3.config(text='5: Choose slope')
        self.label_reduce4.config(text='6: Choose orientation')
        self.scale_date.config(label='Dates scale')
        
        self.message_filedialog='Import a PRO File'
        
    ##########################################################
    # GESTION DU PROFIL INTERACTIF
    ##########################################################
        
    def click_for_zoom(self,event):
        ff = prosimu(self.filename)
        self.ax1.clear()
        if ('snow_layer' in ff.getdimvar(self.variable)):
            self.pro.plot_massif(self.ax1, self.variable, date=self.date_motion, real_layers=True, legend=self.variable, legend_x=self.liste_massif_pour_legende, cbar_show=False, top_zoom=True)
        else:
            self.pro.plot1D_massif(self.ax1, self.variable, date=self.date_motion, legend=self.variable, legend_x=self.liste_massif_pour_legende)
        self.Canevas.draw()
        plt.close(self.fig1)
        self.clik_zoom=True
    
    def update_plot(self,value):
        ff = prosimu(self.filename)
        self.date_motion=self.date[int(value)]
        self.ax1.clear()
        if ('snow_layer' in ff.getdimvar(self.variable)):
            self.pro.plot_massif(self.ax1, self.variable, date=self.date_motion, real_layers=True, legend=self.variable, legend_x=self.liste_massif_pour_legende, cbar_show=False)
        else:
            self.pro.plot1D_massif(self.ax1, self.variable, date=self.date_motion, legend=self.variable, legend_x=self.liste_massif_pour_legende)
        self.Canevas.draw()
        plt.close(self.fig1)
        self.clik_zoom=False
    
    def motion(self,event):
        if (event.inaxes == self.ax1):
            massif_souris=min(math.floor(event.xdata),len(self.liste_points)-1)
            hauteur_souris=event.ydata
            self.ax2.clear()
            if self.profil_complet:
                self.ax3.clear()
                self.pro.plot_profil_complet_massif(self.ax2, self.ax3, self.variable_souris, self.date_motion, massif_souris, hauteur_souris, cbar_show=self.first_profil, bool_layer=self.bool_layer, liste_nom=self.liste_massif_pour_legende, top=self.clik_zoom)    
            else:
                self.pro.plot_profil_massif(self.ax2, self.variable_souris, self.date_motion, massif_souris, hauteur_souris, bool_layer=self.bool_layer, liste_nom=self.liste_massif_pour_legende, top=self.clik_zoom)
            self.Canevas2.draw()
            self.buttonSave2.config(state='normal',command=self.Save_profil)
            self.buttonSave4.config(state='normal',command=self.Pickle_profil)
            plt.close(self.fig2)
            self.first_profil=False
    
    ##########################################################
    # REMISE À ZERO
    ##########################################################
    def refresh_all_combo(self):
        self.combobox.config(state = 'disabled',values='')
        self.combobox.set('')
        self.combobox_choix_profil.config(state = 'disabled',values='')
        self.combobox_choix_profil.set('')
        self.combobox_reduce2.config(state = 'disabled', values = '')
        self.combobox_reduce2.set('')
        self.combobox_reduce3.config(state = 'disabled', values = '')
        self.combobox_reduce3.set('')
        self.combobox_reduce4.config(state = 'disabled', values = '')
        self.combobox_reduce4.set('')
        self.list_choix=[None,None,None]
        self.var_sup=[]
        self.bool_profil=False

    def refresh_all_plot(self):
        largeur = self.winfo_width()/self.taille_x
        hauteur = self.winfo_height()/self.taille_y
        
        if (self.figclear == False):
            self.fig1.clear()
            self.fig1, self.ax1 = plt.subplots(1, 1, sharex=True, sharey=True)
            self.Canevas.get_tk_widget().destroy()
            self.Canevas = FigureCanvasTkAgg(self.fig1,self)
            self.Canevas.get_tk_widget().place(x=5*largeur,y=150*hauteur,width=500*largeur, height=500*hauteur)  
            self.fig2.clear()
            self.fig2, self.ax2 = plt.subplots(1, 1, sharex=True, sharey=True)
            self.ax3=self.ax2.twiny()
            self.Canevas2.get_tk_widget().destroy()
            self.Canevas2 = FigureCanvasTkAgg(self.fig2,self)
            self.Canevas2.get_tk_widget().place(x=505*largeur,y=150*hauteur,width=200*largeur, height=500*hauteur)
        
        self.buttonPlot.config(state='disabled')
        self.buttonSave1.config(state='disabled')
        self.buttonSave2.config(state='disabled')
        self.buttonSave3.config(state='disabled')
        self.buttonSave4.config(state='disabled')
        self.scale_date.config(state='disabled')
        self.figclear=True
        self.first_profil=True
        
    def raz(self):
        self.refresh_all_combo()
        self.refresh_all_plot()
        self.liste_variable=[]
        self.liste_variable_for_pres=[]
        
    ##########################################################
    # RECUPERATION FICHIER
    ##########################################################
    def Ouvrir(self):
        self.filename = tkinter.filedialog.askopenfilename(title=self.message_filedialog,filetypes=[('PRO files','.nc'),('all files','.*')])
        print(self.filename)
        self.raz()

        ff = prosimu(self.filename)
        self.date=ff.readtime()
        self.datedeb=self.date[0]
        self.datefin=self.date[len(self.date)-1]
        
        if len(self.date) > 1000: 
            messagebox.showinfo('Time > 1000', 'automatic sampling to avoid too long treatment')
        
        self.pro = proReader_mini.ProReader_mini(ncfile=self.filename)
        listvariables = ff.listvar()
        self.Tableau=self.pro.get_choix_ss_massif(self.filename)

        for i in range(len(listvariables)):
            if(listvariables[i]==(listvariables[i].upper()) and listvariables[i]!='ZS'):
                if ff.getattr(listvariables[i],'long_name')!='':
                    self.liste_variable_for_pres.append(ff.getattr(listvariables[i],'long_name'))
                    self.liste_variable.append(listvariables[i])
                else:
                    self.liste_variable_for_pres.append(listvariables[i])
                    self.liste_variable.append(listvariables[i])

        self.recup(self)
        
    ##########################################################
    # CHOIX VARIABLE
    ##########################################################
    def recup(self,event):
        def suite(event):
            variable_for_pres=self.combobox.get()
            self.variable=self.liste_variable[self.liste_variable_for_pres.index(variable_for_pres)]
            self.var_sup.append(self.variable)
            print(self.variable)
            if self.bool_profil:
                #self.pro = proReader_mini.ProReader_massif(ncfile=self.filename, var=self.variable, point=int(self.point_choisi),var_sup=self.var_sup)
                self.pro = proReader_mini.ProReader_massif(ncfile=self.filename, var=self.variable, liste_points=self.liste_points, var_sup=self.var_sup)
                
            ff = prosimu(self.filename)
            self.profil_complet=False
            if ({'SNOWTYPE','SNOWRAM'}.issubset(set(ff.listvar()))):
                self.profil_complet=True
            
            liste_pres=[]
            liste=list(set(ff.listvar())-{'SNOWTYPE','SNOWRAM'})
            for var in liste:
                if 'snow_layer' in list(ff.getdimvar(var)):
                    liste_pres.append(self.liste_variable_for_pres[self.liste_variable.index(var)])

            self.combobox_choix_profil.config(values = liste_pres)
            self.combobox_choix_profil.config(state = "readonly")
            self.combobox_choix_profil.bind('<<ComboboxSelected>>', self.choix_profil)
            
        self.combobox.config(state ='readonly', values=self.liste_variable_for_pres)
        self.combobox.bind('<<ComboboxSelected>>', suite)

    def make_list_massif(self):
        self.list_massif_num=[]
        self.list_massif_nom=[]
        IM=infomassifs()
        listmassif = IM.getListMassif_of_region('all')
        for massif in listmassif:
            self.list_massif_num.append(massif)
            self.list_massif_nom.append(str(IM.getMassifName(massif).decode('UTF-8')))
            
    ##########################################################
    # CHOIX POINT
    ##########################################################

    def reduce2(self,event):
        self.combobox_reduce2.config(state = "readonly")
        liste=list(set(self.Tableau[0,:])) 
        self.combobox_reduce2.config(values = liste)
        self.combobox_reduce2.bind('<<ComboboxSelected>>', self.reduce3)
        if self.bool_profil:       
            self.choix_point()    
        
    def reduce3(self,event):
        self.combobox_reduce3.config(state = "readonly")
        altitude=self.combobox_reduce2.get()
        self.list_choix[0]=float(altitude)
        n=len(self.Tableau[0,:])
        A=self.Tableau[0,:]==[self.list_choix[0]]*n
        indices = A
        
        liste=list(set(self.Tableau[1,indices]))
        self.combobox_reduce3.config(values = liste)
        self.combobox_reduce3.bind('<<ComboboxSelected>>', self.reduce4)
        if self.bool_profil:
            self.choix_point()
        
    def reduce4(self,event):
        self.combobox_reduce4.config(state = "readonly")
        pente=self.combobox_reduce3.get()
        self.list_choix[1]=float(pente)
        n=len(self.Tableau[0,:])
        A=self.Tableau[0,:]==[self.list_choix[0]]*n
        B=self.Tableau[1,:]==[self.list_choix[1]]*n
        indices = A & B

        liste=list(set(self.Tableau[2,indices]))
        self.combobox_reduce4.config(values = liste)
        self.combobox_reduce4.bind('<<ComboboxSelected>>', self.finalisation_reduce)
        if self.bool_profil:
            self.choix_point()

    def choix_point(self):
        n=len(self.Tableau[0,:])
        A=self.Tableau[0,:]==[self.list_choix[0]]*n
        B=self.Tableau[1,:]==[self.list_choix[1]]*n
        C=self.Tableau[2,:]==[self.list_choix[2]]*n
        indices = A & B & C
        if True not in list(indices):
            self.buttonPlot.config(state='disabled')
        else:
            self.liste_points = [i for i, x in enumerate(indices) if x == True]
            if self.bool_profil==True:
                self.buttonPlot.config(state='normal',command=self.Plotage)
        
    def finalisation_reduce(self,event):
        orientation=self.combobox_reduce4.get()
        self.list_choix[2]=float(orientation)
        self.choix_point()
        
    ##########################################################
    # CHOIX VARIABLE PROFIL
    ##########################################################
    def choix_profil(self,event):
        variable_souris_for_pres=self.combobox_choix_profil.get()
        self.variable_souris=self.liste_variable[self.liste_variable_for_pres.index(variable_souris_for_pres)]
        if self.profil_complet:
            self.var_sup.extend([self.variable_souris,'SNOWTYPE','SNOWRAM'])
        else:
            self.var_sup.append(self.variable_souris)
        self.bool_profil=True
        
        if (len(self.Tableau[0])+len(self.Tableau[1])+len(self.Tableau[2])==3):
            self.combobox_reduce2.config(state = 'disabled', values = '')
            self.combobox_reduce3.config(state = 'disabled', values = '')
            self.combobox_reduce4.config(state = 'disabled', values = '')
            if self.Tableau[0]==[-10.]:
                self.combobox_reduce2.set('inconnu')
            else:
                self.combobox_reduce2.set(self.Tableau[0][0])
            if self.Tableau[1]==[-10.]:
                self.combobox_reduce3.set('inconnu')
            else:
                self.combobox_reduce3.set(self.Tableau[1][0])
            if self.Tableau[2]==[-10.]:
                self.combobox_reduce4.set('inconnu')
            else:
                self.combobox_reduce4.set(self.Tableau[2][0])
            self.buttonPlot.config(state='normal',command=self.Plotage)
        else:
            self.reduce2(self)
        
    ##########################################################
    # TRACE
    ##########################################################
    def Plotage(self):
        #self.boolzoom=False
        #self.boolzoomdate=False
        self.pro = proReader_mini.ProReader_massif(ncfile=self.filename, var=self.variable, liste_points=self.liste_points, var_sup=self.var_sup)
        largeur = self.winfo_width()/self.taille_x
        hauteur = self.winfo_height()/self.taille_y
        self.fig1.clear()
        self.ax1.clear()
        self.fig1, self.ax1 = plt.subplots(1, 1, sharex=True, sharey=True)
        self.Canevas.get_tk_widget().destroy()
        self.Canevas = FigureCanvasTkAgg(self.fig1,self)
        self.Canevas.get_tk_widget().place(x=5*largeur,y=150*hauteur,width=500*largeur, height=500*hauteur)
        ff = prosimu(self.filename)
        print(self.variable)
        self.liste_massif_pour_legende=[]
        if ('massif_num' in ff.listvar()):
            nrstationtab = ff.read('massif_num')[:]
            for num in self.liste_points:
                indice=self.list_massif_num.index(nrstationtab[num])
                self.liste_massif_pour_legende.append(self.list_massif_nom[indice])
        if ('snow_layer' in ff.getdimvar(self.variable)):
            self.pro.plot_massif(self.ax1, self.variable, date=None, real_layers=True, legend=self.variable, legend_x=self.liste_massif_pour_legende, cbar_show=True)
            self.bool_layer=True
        else:
            self.pro.plot1D_massif(self.ax1, self.variable, date=None, legend=self.variable, legend_x=self.liste_massif_pour_legende)
            self.bool_layer=False
        self.Canevas.draw()
        self.Canevas.mpl_connect('motion_notify_event', self.motion)
        self.scale_date.config(from_=0, to=(len(self.date)-1),state='normal',showvalue=0,command=self.update_plot, variable=IntVar)
        self.Canevas.mpl_connect('button_press_event', self.click_for_zoom)
        plt.close(self.fig1)
        self.buttonRaz.config(state='normal',command=self.raz)
        self.buttonSave1.config(state='normal',command=self.Save_plot)
        #self.buttonSave3.config(state='normal',command=self.Pickle_plot)
        self.figclear=False
        self.clik_zoom=False
        
    ##########################################################
    # SAUVEGARDE
    ##########################################################
    def Save_plot(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*'),
                                ('jpeg image', '.jpg'), ('png image', '.png'),
                                ('tiff image', '.tiff'), ('bmp image', '.bmp')]

        options['initialfile'] = 'graph_proreader.png'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return self.fig1.savefig(filename,bbox_inches='tight')
        
    def Save_profil(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*'),
                                ('jpeg image', '.jpg'), ('png image', '.png'),
                                ('tiff image', '.tiff'), ('bmp image', '.bmp')]

        options['initialfile'] = 'profil_proreader.png'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return self.fig2.savefig(filename,bbox_inches='tight')
        
    def Pickle_plot(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*')]

        options['initialfile'] = 'mypicklefile'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return pickle.dump(self.fig1, open(filename, 'wb'))
        
    def Pickle_profil(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*')]

        options['initialfile'] = 'mypicklefile'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return pickle.dump(self.fig2, open(filename, 'wb'))

'''#############################################################################################
################################################################################################
#
#
#
#
#
################################################################################################
#############################################################################################'''
class GraphMembre(Toplevel):
    def __init__(self,**Arguments):
        Toplevel.__init__(self, **Arguments)
        self.title('GUI PROreader CEN')
        
        self.taille_x=900
        self.taille_y=700
        self.geometry('900x700')

        self.x=''
        self.y=''
        self.test=''
        self.variable=''
        self.variable_souris=''
        self.date=''
        self.datedeb=''
        self.datefin=''
        self.date1_zoom=''
        self.date1_zoom_old=''
        self.date_motion=None
        #self.boolzoom=False
        #self.boolzoomdate=False
        self.bool_profil=False
        self.bool_layer=False
        self.figclear=True
        self.first_profil=True
        self.width_rect=0.01
        self.rectangle_choix=''
        self.filename=''
        self.list_choix=[None,None,None,None]
        self.list_massif_num=[]
        self.list_massif_nom=[]
        self.liste_variable=[]
        self.liste_variable_for_pres=[]
        self.pro=''
        self.Tableau=''
        self.var_choix1=''
        self.var_choix2=''
        self.var_sup=[]
        self.valeur_choisie1=''
        self.valeur_choisie2=''
        self.message_filedialog='Importer un fichier PRO'
        self.type_graphique=1
        
        self.menubar = Menu()
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='French', command=self.toFrench)
        self.filemenu.add_command(label='English', command=self.toEnglish)
        self.menubar.add_cascade(label='Change Language', menu=self.filemenu)
        self.config(menu=self.menubar)
        
        self.buttonQuit = Button(self,text='Quitter', command = quit)
        self.buttonPlot = Button(self,  text='Tracer graphe', state='disabled')
        self.buttonRaz = Button(self,  text='Remise à zéro', state='disabled')
        self.buttonSave1 = Button(self,  text='Sauver graphe', state='disabled')
        self.buttonSave2 = Button(self,  text='Sauver profil', state='disabled')
        self.buttonSave3 = Button(self,  text='Pickle graphe', state='disabled')
        self.buttonSave4 = Button(self,  text='Pickle profil', state='disabled')
        self.label_var=Label(self,text='2: Variable à tracer')
        self.combobox = ttk.Combobox(self, state = 'disabled', values = '')
        style = ttk.Style()
        style.configure('TCombobox', postoffset=(0,0,200,0))
        self.label_choix_profil=Label(self,text='3: Choix variable profil')
        self.combobox_choix_profil = ttk.Combobox(self, state = 'disabled', values = '')
        self.label_reduce1=Label(self,text='4: Choix massif')
        self.combobox_reduce1 = ttk.Combobox(self, state = 'disabled', values = '')
        self.label_reduce2=Label(self,text='5: Choix altitude')
        self.combobox_reduce2 = ttk.Combobox(self, state = 'disabled', values = '')
        self.label_reduce3=Label(self,text='6: Choix angle de pente')
        self.combobox_reduce3 = ttk.Combobox(self, state = 'disabled', values = '')
        self.label_reduce4=Label(self,text='7: Choix orientation')
        self.combobox_reduce4 = ttk.Combobox(self, state = 'disabled', values = '')
        self.fig1, self.ax1 = plt.subplots(1, 1, sharex=True, sharey=True)
        self.Canevas = FigureCanvasTkAgg(self.fig1,self)
        self.fig2, self.ax2 = plt.subplots(1, 1, sharex=True, sharey=True)
        self.ax3=self.ax2.twiny()
        self.Canevas2 = FigureCanvasTkAgg(self.fig2,self)
        self.scale_date = Scale(self, orient='horizontal', state='disabled',label='Echelle de dates')
        self.buttonOpenFile = Button(self,  text='1: Ouvrir un fichier',command=self.Ouvrir)

        self.bind('<Configure>', self.onsize_test)
        self.make_list_massif()
        
    ##########################################################
    # PLACEMENT BOUTONS, LISTES DEFILANTES, ETC...
    ##########################################################
     
    def onsize_test(self,event):
        largeur = self.winfo_width()/self.taille_x
        hauteur = self.winfo_height()/self.taille_y
        self.buttonQuit.place(x=750*largeur, y=660*hauteur)
        self.buttonOpenFile.place(x=5*largeur, y=5*hauteur)
        self.buttonPlot.place(x=750*largeur, y=100*hauteur)
        self.buttonRaz.place(x=750*largeur, y=5*hauteur)
        self.buttonSave1.place(x=5*largeur, y=660*hauteur)
        self.buttonSave2.place(x=155*largeur, y=660*hauteur)
        self.buttonSave3.place(x=305*largeur, y=660*hauteur)
        self.buttonSave4.place(x=455*largeur, y=660*hauteur)
        self.label_var.place(x=200*largeur,y=5*hauteur)
        self.combobox.place(x=200*largeur, y=20*hauteur)
        self.label_choix_profil.place(x=400*largeur,y=5*hauteur)
        self.combobox_choix_profil.place(x=400*largeur, y=20*hauteur)
        self.Canevas.get_tk_widget().place(x=3*largeur,y=160*hauteur,width=502*largeur, height=500*hauteur)
        self.Canevas2.get_tk_widget().place(x=504*largeur,y=160*hauteur,width=390*largeur, height=500*hauteur)
        self.label_reduce1.place(x=75*largeur,y=45*hauteur)
        self.combobox_reduce1.place(x=75*largeur, y=60*hauteur)
        self.label_reduce2.place(x=270*largeur,y=45*hauteur)
        self.combobox_reduce2.place(x=270*largeur, y=60*hauteur)
        self.label_reduce3.place(x=470*largeur,y=45*hauteur)
        self.combobox_reduce3.place(x=470*largeur, y=60*hauteur)
        self.label_reduce4.place(x=670*largeur,y=45*hauteur)
        self.combobox_reduce4.place(x=670*largeur, y=60*hauteur)
        self.scale_date.place(x=30*largeur,y=100*hauteur)
        self.scale_date.config(length=380*largeur)

    ##########################################################
    # TRADUCTION
    ##########################################################
    def toFrench(self):
        self.buttonQuit.config(text='Quitter')
        self.buttonOpenFile.config(text='1: Ouvrir un fichier')
        self.buttonPlot.config(text='Tracer graphe')
        self.buttonRaz.config(text='Remise à zéro')
        self.buttonSave1.config(text='Sauver graphe')
        self.buttonSave2.config(text='Sauver profil')
        self.buttonSave3.config(text='Pickle graphe')
        self.buttonSave4.config(text='Pickle profil')
        self.label_var.config(text='2: Variable à tracer')
        self.label_choix_profil.config(text='3: Choix variable profil')
        self.label_reduce1.config(text='4: Choix massif')
        self.label_reduce2.config(text='5: Choix altitude')
        self.label_reduce3.config(text='6: Choix angle de pente')
        self.label_reduce4.config(text='7: Choix orientation')
        self.scale_date.config(label='Echelle de dates')
        
        self.message_filedialog='Importer un fichier PRO'

    def toEnglish(self):
        self.buttonQuit.config(text='Exit')
        self.buttonOpenFile.config(text='1: Open File')
        self.buttonPlot.config(text='Plot')
        self.buttonRaz.config(text='Reset')
        self.buttonSave1.config(text='Save graph')
        self.buttonSave2.config(text='Save profile')
        self.buttonSave3.config(text='Pickle graph')
        self.buttonSave4.config(text='Pickle profile')
        self.label_var.config(text='2: Variable to plot')
        self.label_choix_profil.config(text='3: Variable for Profile')
        self.label_reduce1.config(text='4: Choose massif')
        self.label_reduce2.config(text='5: Choose altitude')
        self.label_reduce3.config(text='6: Choose slope')
        self.label_reduce4.config(text='7: Choose orientation')
        self.scale_date.config(label='Dates scale')
        
        self.message_filedialog='Import a PRO File'
        
    ##########################################################
    # GESTION DU PROFIL INTERACTIF
    ##########################################################
        
    def click_for_zoom(self,event):
        ff = prosimu(self.filename)
        self.ax1.clear()
        if ('snow_layer' in ff.getdimvar(self.variable)):
            self.pro.plot_membre(self.ax1, self.variable, date=self.date_motion, real_layers=True, legend=self.variable, cbar_show=False, top_zoom=True)
        else:
            self.pro.plot1D_membre(self.ax1, self.variable, date=self.date_motion, legend=self.variable)
        self.Canevas.draw()
        plt.close(self.fig1)
        self.clik_zoom=True
    
    def update_plot(self,value):
        ff = prosimu(self.filename)
        self.date_motion=self.date[int(value)]
        self.ax1.clear()
        if ('snow_layer' in ff.getdimvar(self.variable)):
            self.pro.plot_membre(self.ax1, self.variable, date=self.date_motion, real_layers=True, legend=self.variable, cbar_show=False)
        else:
            self.pro.plot1D_membre(self.ax1, self.variable, date=self.date_motion, legend=self.variable)
        self.Canevas.draw()
        plt.close(self.fig1)
        self.clik_zoom=False
    
    def motion(self,event):
        if (event.inaxes == self.ax1):
            membre_souris=min(math.floor(event.xdata),self.nmembre-1)
            hauteur_souris=event.ydata
            self.ax2.clear()
            if self.profil_complet:
                self.ax3.clear()
                self.pro.plot_profil_complet_membre(self.ax2, self.ax3, self.variable_souris, self.date_motion, membre_souris, hauteur_souris, cbar_show=self.first_profil, bool_layer=self.bool_layer, top=self.clik_zoom)    
            else:
                self.pro.plot_profil_membre(self.ax2, self.variable_souris, self.date_motion, membre_souris, hauteur_souris, bool_layer=self.bool_layer, top=self.clik_zoom)
            self.Canevas2.draw()
            self.buttonSave2.config(state='normal',command=self.Save_profil)
            self.buttonSave4.config(state='normal',command=self.Pickle_profil)
            plt.close(self.fig2)
            self.first_profil=False
    
    ##########################################################
    # REMISE À ZERO
    ##########################################################
    def refresh_all_combo(self):
        self.combobox.config(state = 'disabled',values='')
        self.combobox.set('')
        self.combobox_choix_profil.config(state = 'disabled',values='')
        self.combobox_choix_profil.set('')
        self.combobox_reduce1.config(state = 'disabled', values = '')
        self.combobox_reduce1.set('')
        self.combobox_reduce2.config(state = 'disabled', values = '')
        self.combobox_reduce2.set('')
        self.combobox_reduce3.config(state = 'disabled', values = '')
        self.combobox_reduce3.set('')
        self.combobox_reduce4.config(state = 'disabled', values = '')
        self.combobox_reduce4.set('')
        self.list_choix=[None,None,None,None]
        self.var_sup=[]
        self.bool_profil=False

    def refresh_all_plot(self):
        largeur = self.winfo_width()/self.taille_x
        hauteur = self.winfo_height()/self.taille_y
        
        if (self.figclear == False):
            self.fig1.clear()
            self.fig1, self.ax1 = plt.subplots(1, 1, sharex=True, sharey=True)
            self.Canevas.get_tk_widget().destroy()
            self.Canevas = FigureCanvasTkAgg(self.fig1,self)
            self.Canevas.get_tk_widget().place(x=5*largeur,y=150*hauteur,width=500*largeur, height=500*hauteur)  
            self.fig2.clear()
            self.fig2, self.ax2 = plt.subplots(1, 1, sharex=True, sharey=True)
            self.ax3=self.ax2.twiny()
            self.Canevas2.get_tk_widget().destroy()
            self.Canevas2 = FigureCanvasTkAgg(self.fig2,self)
            self.Canevas2.get_tk_widget().place(x=505*largeur,y=150*hauteur,width=200*largeur, height=500*hauteur)
        
        self.buttonPlot.config(state='disabled')
        self.buttonSave1.config(state='disabled')
        self.buttonSave2.config(state='disabled')
        self.buttonSave3.config(state='disabled')
        self.buttonSave4.config(state='disabled')
        self.figclear=True
        self.first_profil=True
        
    def raz(self):
        self.refresh_all_combo()
        self.refresh_all_plot()
        self.liste_variable=[]
        self.liste_variable_for_pres=[]
        
    ##########################################################
    # RECUPERATION FICHIER
    ##########################################################
    def Ouvrir(self):
        self.filename = tkinter.filedialog.askopenfilename(title=self.message_filedialog,filetypes=[('PRO files','.nc'),('all files','.*')])
        print(self.filename)
        self.raz()

        ff = prosimu(self.filename)
        self.date=ff.readtime()
        self.datedeb=self.date[0]
        self.datefin=self.date[len(self.date)-1]
        
        if len(self.date) > 1000: 
            messagebox.showinfo('Time > 1000', 'automatic sampling to avoid too long treatment')

        self.pro = proReader_mini.ProReader_membre(ncfile=self.filename)
        self.nmembre = self.pro.nb_membre
        listvariables = ff.listvar()
        self.Tableau=self.pro.get_choix(self.filename)

        for i in range(len(listvariables)):
            if(listvariables[i]==(listvariables[i].upper()) and listvariables[i]!='ZS'):
                if ff.getattr(listvariables[i],'long_name')!='':
                    self.liste_variable_for_pres.append(ff.getattr(listvariables[i],'long_name'))
                    self.liste_variable.append(listvariables[i])
                else:
                    self.liste_variable_for_pres.append(listvariables[i])
                    self.liste_variable.append(listvariables[i])

        self.recup(self)
        
    ##########################################################
    # CHOIX VARIABLE
    ##########################################################
    def recup(self,event):
        def suite(event):
            variable_for_pres=self.combobox.get()
            self.variable=self.liste_variable[self.liste_variable_for_pres.index(variable_for_pres)]
            self.var_sup.append(self.variable)
            print(self.variable)
            if self.bool_profil:
                self.pro = proReader_mini.ProReader_membre(ncfile=self.filename, var=self.variable, point=int(self.point_choisi),var_sup=self.var_sup)
                
            ff = prosimu(self.filename)
            self.profil_complet=False
            if ({'SNOWTYPE','SNOWRAM'}.issubset(set(ff.listvar()))):
                self.profil_complet=True
            
            liste_pres=[]
            liste=list(set(ff.listvar())-{'SNOWTYPE','SNOWRAM'})
            for var in liste:
                if 'snow_layer' in list(ff.getdimvar(var)):
                    liste_pres.append(self.liste_variable_for_pres[self.liste_variable.index(var)])

            self.combobox_choix_profil.config(values = liste_pres)
            self.combobox_choix_profil.config(state = "readonly")
            self.combobox_choix_profil.bind('<<ComboboxSelected>>', self.choix_profil)
            
        self.combobox.config(state ='readonly', values=self.liste_variable_for_pres)
        self.combobox.bind('<<ComboboxSelected>>', suite)

    def make_list_massif(self):
        self.list_massif_num=[]
        self.list_massif_nom=[]
        IM=infomassifs()
        listmassif = IM.getListMassif_of_region('all')
        for massif in listmassif:
            self.list_massif_num.append(massif)
            self.list_massif_nom.append(str(IM.getMassifName(massif).decode('UTF-8')))
            
    ##########################################################
    # CHOIX POINT
    ##########################################################
    def reduce1(self,event):
        self.combobox_reduce1.config(state = "readonly")
        liste=[]
        for it_massif in list(set(self.Tableau[0,:])):
            indice=self.list_massif_num.index(it_massif)
            liste.append(self.list_massif_nom[indice])
        self.combobox_reduce1.config(values = liste)
        self.combobox_reduce1.bind('<<ComboboxSelected>>', self.reduce2)
        if self.bool_profil:
            self.choix_point()

    def reduce2(self,event):
        self.combobox_reduce2.config(state = "readonly")
        nom_massif=self.combobox_reduce1.get()
        indice=self.list_massif_nom.index(nom_massif)
        num_massif=self.list_massif_num[indice]
        self.list_choix[0]=float(num_massif)
        liste=list(set(self.Tableau[1,self.Tableau[0,:]==num_massif]))
        self.combobox_reduce2.config(values = liste)
        self.combobox_reduce2.bind('<<ComboboxSelected>>', self.reduce3)
        if self.bool_profil:       
            self.choix_point()    
        
    def reduce3(self,event):
        self.combobox_reduce3.config(state = "readonly")
        altitude=self.combobox_reduce2.get()
        self.list_choix[1]=float(altitude)
        n=len(self.Tableau[0,:])
        A=self.Tableau[0,:]==[self.list_choix[0]]*n
        B=self.Tableau[1,:]==[self.list_choix[1]]*n
        indices = A & B
        
        liste=list(set(self.Tableau[2,indices]))
        self.combobox_reduce3.config(values = liste)
        self.combobox_reduce3.bind('<<ComboboxSelected>>', self.reduce4)
        if self.bool_profil:
            self.choix_point()
        
    def reduce4(self,event):
        self.combobox_reduce4.config(state = "readonly")
        pente=self.combobox_reduce3.get()
        self.list_choix[2]=float(pente)
        n=len(self.Tableau[0,:])
        A=self.Tableau[0,:]==[self.list_choix[0]]*n
        B=self.Tableau[1,:]==[self.list_choix[1]]*n
        C=self.Tableau[2,:]==[self.list_choix[2]]*n
        indices = A & B & C

        liste=list(set(self.Tableau[3,indices]))
        self.combobox_reduce4.config(values = liste)
        self.combobox_reduce4.bind('<<ComboboxSelected>>', self.finalisation_reduce)
        if self.bool_profil:
            self.choix_point()

    def choix_point(self):
        n=len(self.Tableau[0,:])
        A=self.Tableau[0,:]==[self.list_choix[0]]*n
        B=self.Tableau[1,:]==[self.list_choix[1]]*n
        C=self.Tableau[2,:]==[self.list_choix[2]]*n
        D=self.Tableau[3,:]==[self.list_choix[3]]*n
        indices = A & B & C & D
        if True not in list(indices):
            self.buttonPlot.config(state='disabled')
        else:
            self.point_choisi = list(indices).index(True)
            if self.bool_profil==True:
                self.buttonPlot.config(state='normal',command=self.Plotage)
        
    def finalisation_reduce(self,event):
        orientation=self.combobox_reduce4.get()
        self.list_choix[3]=float(orientation)
        self.choix_point()
        
    ##########################################################
    # CHOIX VARIABLE PROFIL
    ##########################################################
    def choix_profil(self,event):
        variable_souris_for_pres=self.combobox_choix_profil.get()
        self.variable_souris=self.liste_variable[self.liste_variable_for_pres.index(variable_souris_for_pres)]
        if self.profil_complet:
            self.var_sup.extend([self.variable_souris,'SNOWTYPE','SNOWRAM'])
        else:
            self.var_sup.append(self.variable_souris)
        self.bool_profil=True
        
        if (len(self.Tableau[0])+len(self.Tableau[1])+len(self.Tableau[2])+len(self.Tableau[3])==4):
            self.point_choisi=0
            self.combobox_reduce1.config(state = 'disabled', values = '')
            self.combobox_reduce2.config(state = 'disabled', values = '')
            self.combobox_reduce3.config(state = 'disabled', values = '')
            self.combobox_reduce4.config(state = 'disabled', values = '')
            if self.Tableau[0]==[-10.]:
                self.combobox_reduce1.set('inconnu')
            else:
                self.combobox_reduce1.set(self.Tableau[0][0])
            if self.Tableau[1]==[-10.]:
                self.combobox_reduce2.set('inconnu')
            else:
                self.combobox_reduce2.set(self.Tableau[1][0])
            if self.Tableau[2]==[-10.]:
                self.combobox_reduce3.set('inconnu')
            else:
                self.combobox_reduce3.set(self.Tableau[2][0])
            if self.Tableau[3]==[-10.]:
                self.combobox_reduce4.set('inconnu')
            else:
                self.combobox_reduce4.set(self.Tableau[3][0])
            self.buttonPlot.config(state='normal',command=self.Plotage)
        else:
            self.reduce1(self)
        
    ##########################################################
    # TRACE
    ##########################################################
    def Plotage(self):
        #self.boolzoom=False
        #self.boolzoomdate=False
        self.pro = proReader_mini.ProReader_membre(ncfile=self.filename, var=self.variable, point=int(self.point_choisi), var_sup=self.var_sup)
        largeur = self.winfo_width()/self.taille_x
        hauteur = self.winfo_height()/self.taille_y
        self.fig1.clear()
        self.ax1.clear()
        self.fig1, self.ax1 = plt.subplots(1, 1, sharex=True, sharey=True)
        self.Canevas.get_tk_widget().destroy()
        self.Canevas = FigureCanvasTkAgg(self.fig1,self)
        self.Canevas.get_tk_widget().place(x=5*largeur,y=150*hauteur,width=500*largeur, height=500*hauteur)
        ff = prosimu(self.filename)
        print(self.variable)
        if ('snow_layer' in ff.getdimvar(self.variable)):
            self.pro.plot_membre(self.ax1, self.variable, date=None, real_layers=True, legend=self.variable, cbar_show=True)
            self.bool_layer=True
        else:
            self.pro.plot1D_membre(self.ax1, self.variable, date=None, legend=self.variable)
            self.bool_layer=False
        self.Canevas.draw()
        self.Canevas.mpl_connect('motion_notify_event', self.motion)
        self.scale_date.config(from_=0, to=(len(self.date)-1),state='normal',showvalue=0,command=self.update_plot, variable=IntVar)
        self.Canevas.mpl_connect('button_press_event', self.click_for_zoom)
        plt.close(self.fig1)
        self.buttonRaz.config(state='normal',command=self.raz)
        self.buttonSave1.config(state='normal',command=self.Save_plot)
        #self.buttonSave3.config(state='normal',command=self.Pickle_plot)
        self.figclear=False
        self.clik_zoom=False
        
    ##########################################################
    # SAUVEGARDE
    ##########################################################
    def Save_plot(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*'),
                                ('jpeg image', '.jpg'), ('png image', '.png'),
                                ('tiff image', '.tiff'), ('bmp image', '.bmp')]

        options['initialfile'] = 'graph_proreader.png'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return self.fig1.savefig(filename,bbox_inches='tight')
        
    def Save_profil(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*'),
                                ('jpeg image', '.jpg'), ('png image', '.png'),
                                ('tiff image', '.tiff'), ('bmp image', '.bmp')]

        options['initialfile'] = 'profil_proreader.png'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return self.fig2.savefig(filename,bbox_inches='tight')
        
    def Pickle_plot(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*')]

        options['initialfile'] = 'mypicklefile'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return pickle.dump(self.fig1, open(filename, 'wb'))
        
    def Pickle_profil(self):
        self.file_opt = options = {}
        options['filetypes'] = [('all files', '.*')]

        options['initialfile'] = 'mypicklefile'
        filename = tkinter.filedialog.asksaveasfilename(**self.file_opt)

        if filename:
            return pickle.dump(self.fig2, open(filename, 'wb'))

'''#############################################################################################
################################################################################################
#
#
#
#
#
################################################################################################
#############################################################################################'''

class GestionFenetre(Frame):
    'In order to choose which graph will be drawn: standard, by massif, by members'
    def __init__(self):
        Frame.__init__(self)
        self.master.title('GUI PROreader CEN')
        self.master.geometry('250x200+200+200')
        self.master.taille_x_master = 250
        self.master.taille_y_master = 200
    
        self.master.buttongraphe_standard = Button(self.master,text='Standard Graph', command = self.graphe1)
        self.master.buttongraphe_massif = Button(self.master,text='Massif Graph', command = self.graphe2)
        self.master.buttongraphe_membre = Button(self.master,text='Member Graph', command = self.graphe3)
        
        self.master.bind('<Configure>', self.onsize_master)
        
    def onsize_master(self,event):
        largeur_master = self.master.winfo_width()/self.master.taille_x_master
        hauteur_master = self.master.winfo_height()/self.master.taille_y_master
        self.master.buttongraphe_standard.place(x=20*largeur_master, y=20*hauteur_master)
        self.master.buttongraphe_massif.place(x=20*largeur_master, y= 80*hauteur_master)
        self.master.buttongraphe_membre.place(x=20*largeur_master, y=140*hauteur_master)
        
    def graphe1(self):
        self.fen1=GraphStandard()
            
    def graphe2(self):
        self.fen2=GraphMassif()
            
    def graphe3(self):
        self.fen3=GraphMembre()
        

if __name__ == '__main__':
    # Lancement du gestionnaire d'événements
    GestionFenetre().mainloop()
    
