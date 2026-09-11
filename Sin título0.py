# -*- coding: utf-8 -*-
"""
Created on Tue May 20 21:20:49 2025

@author: juana
"""

import matplotlib.pyplot as plt



fig, ax = plt.subplots()

consulta3_ordenada = consulta2.sort_values(by='Cantidad de BP fundadas desde 1950', ascending= False)

ax.bar(data = consulta3_ordenada, x= 'Provincia', height = 'Cantidad de BP fundadas desde 1950', width=0.6)
ax.set_title('Cantidad de BP por provincia') 
ax.set_xlabel('Provincia')
ax.set_ylabel('Cantidad BP')
plt.xticks(rotation=90)

#%%

fig, ax = plt.subplots()

ax.scatter(data = primer_consulta,
           x= 'Población Jardin',
           y= 'Jardines',
           c = 'blue',
           label = 'Nivel inicial (0-5 años)',
           alpha = 0.5)
ax.scatter(data = primer_consulta,
           x= 'Población Primaria',
           y= 'Primarias',
           c = 'orange',
           label = 'Nivel primario (6-11 años)',
           alpha = 0.5)
ax.scatter(data = primer_consulta,
           x= 'Población Secundaria',
           y= 'Secundarios',
           c = 'green',
           label = 'Nivel secundario (12-18 años)',
           alpha = 0.5)

ax.set_title('Cantidad EE en función de la población por nivel educativo')
ax.set_xlabel('Población')
ax.set_ylabel('Cantidad EE')
ax.legend()
plt.tight_layout()
plt.grid(True)
#%%
#%%
#Primer gráfico
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

consulta3_ordenada = consulta3.sort_values(by='Cant_BP', ascending= False)

ax.bar(data = consulta3_ordenada, x= 'Provincia', height = 'Cant_BP', width=0.6)
ax.set_title('Cantidad de BP por provincia') 
ax.set_xlabel('Provincia')
ax.set_ylabel('Cantidad BP')
plt.xticks(rotation=50, ha='right')
ax.yaxis.grid(True, linestyle='-', alpha = 0.7)
#%% Segundo gráfico
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

ax.scatter(data = primer_consulta,
           x= 'Población Jardin',
           y= 'Jardines',
           c = 'blue',
           label = 'Nivel inicial (0-5 años)',
           alpha = 0.5)
ax.scatter(data = primer_consulta,
           x= 'Población Primaria',
           y= 'Primarias',
           c = 'orange',
           label = 'Nivel primario (6-11 años)',
           alpha = 0.5)
ax.scatter(data = primer_consulta,
           x= 'Población Secundaria',
           y= 'Secundarios',
           c = 'green',
           label = 'Nivel secundario (12-18 años)',
           alpha = 0.5)

ax.set_title('Cantidad EE en función de la población por nivel educativo')
ax.set_xlabel('Población')
ax.set_ylabel('Cantidad EE')
ax.legend()
plt.tight_layout()
plt.grid(True)

#%% Tercer gráfico