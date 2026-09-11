# -*- coding: utf-8 -*-
"""
    Integrantes: Guadalupe Cataneo, Máximo Ballestrero y Juana María Leiton
    
    En este archivo de código utilizamos dsitintas funciones para formar los modelos relacionales, consultas y gráficos.
    Dividimos en bloques el código, cada uno de ellos son:
        - Modelo Relacional Habitantes -> dfHabitantes
        - Modelo Relacional Bibliotecas Populares -> dfBibliotecaPopular
        - Modelo Relacional Provincias -> dfProvincias
        - Modelo Relacional Departamentos -> dfDepartamentos
        - Modelo RElacional Establecimientos Educativos -> dfEstablecimientosEducativos
        - Consulta SQL 1 -> consulta1
        - Consulta SQL 2 -> consulta2
        - Consulta SQL 3 -> consulta3
        - Consulta SQL 4 -> consulta4
        - Primer Gráfico
        - Segundo Gráfico
        - Tercer Gráfico
        - Cuarto Gráfico
"""
#%%
import pandas as pd
import duckdb as dd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def guardar_datos_poblacion(archivo):
    df = pd.read_excel(archivo, sheet_name=0, header=None)
    
    resultados = []
    i = 0

    while i < len(df):
        fila = df.iloc[i]

        # Buscamos si es una nueva área
        if isinstance(fila[1], str) and "AREA #" in fila[1]:
            codigo = fila[1].split("#")[1].strip()
            departamento = str(fila[2]).strip() if not pd.isna(fila[2]) else ""

            # Buscamos la fila donde empieza la tabla de edad/casos
            i += 1
            while i < len(df):
                edad_valor = df.iloc[i, 1]
                if pd.notna(edad_valor) and str(edad_valor).strip().isdigit():
                    break
                i += 1

            # Iniciamos los recuentos
            edad_inicial = 0
            edad_primario = 0
            edad_secundario = 0
            total = 0

            # Leemos datos de edades y casos
            while i < len(df):
                fila = df.iloc[i]
                
                # Si detectamos una nueva AREA, salimos del bloque actual
                if isinstance(fila[1], str):
                    texto = fila[1].strip().upper()
                    if "AREA #" in texto or "RESUMEN" in texto:
                        break

                try:
                    if fila[1] == "Total":
                        total = fila[2]
                    else:
                        edad = int(fila[1])
                        casos = fila[2]
                        if pd.isna(casos):
                            i += 1
                            continue

                        # Clasificamos por edad
                        if 0 <= edad <= 5:
                            edad_inicial += casos
                        elif 6 <= edad <= 11:
                            edad_primario += casos
                        elif 12 <= edad <= 18:
                            edad_secundario += casos
                except:
                    pass

                i += 1

            # Guardamos los resultados
            resultados.append({
                "id_depto": codigo,
                "departamento": departamento,
                "jardin": edad_inicial,
                "primaria": edad_primario,
                "secundaria": edad_secundario,
                "total": total
            })
        else:
            i += 1
    # Corregimos los códigos de Rio Grande y Ushuaia de Tierra del Fuego
    res = pd.DataFrame(resultados)
    res.iloc[524,0] = "94007"
    res.iloc[526,0] = "94014"
    return res
#%%
# Modelo Relacional: Habitantes
archivo_poblacion = r"TablasOriginales\padron_poblacion.xlsx"
dfHabitantes = guardar_datos_poblacion(archivo_poblacion)
# Unificamos CABA
dfComunas = dfHabitantes.iloc[:15,:]
dfHabitantes = dfHabitantes.iloc[15:,:]
# Columna nueva con nombre general de Ciudad de Buenos Aires
consultaSQL = """
                SELECT DISTINCT *,
                    CASE 
                        WHEN departamento LIKE 'Comuna%' THEN 'Ciudad de Buenos Aires'
                    END AS deptos_ciudad
                    FROM dfComunas
              """
dfComunas = dd.sql(consultaSQL).df()
# Unimos todos los valores de las comunas en uno mismo -> Ciudad de Buenos Aires
consultaSQL = """
                SELECT DISTINCT deptos_ciudad as departamento,
                        SUM(jardin) as jardin,
                        SUM(primaria) as primaria,
                        SUM(secundaria) as secundaria,
                        SUM(total) as total
                FROM dfComunas
                GROUP BY deptos_ciudad
              """
dfComunas = dd.sql(consultaSQL).df()
# Agregamos el id_depto a Ciudad de Buenos Aires que es 02000
dfComunas.insert(0, "id_depto", "02000")
# Unimos el dfHabitantes con el nuevo dato de Ciudad de Buenos Aires con los datos sumados de todas las comunas
consultaSQL = """
                SELECT DISTINCT *
                FROM dfComunas
                UNION 
                SELECT DISTINCT *
                FROM dfHabitantes
              """
dfHabitantes = dd.sql(consultaSQL).df()
# Creamos copia que usaremos despues (es importante que en esta copia, la columna id_depto es string)
dfHabitantes_con_departamentos = dfHabitantes.copy()
# ELiminamos columna departamento
consultaSQL = """
                SELECT DISTINCT id_depto, jardin, primaria, secundaria, total
                FROM dfHabitantes
              """
dfHabitantes = dd.sql(consultaSQL).df()
# Convertimos el tipo de dato de la columna id_depto a int para poder igualar las claves de la tabla de BP 
# ya que en BP no aparecen los primeros 0 de los id de Ciudad de Buenos Aires y Buenos Aires
dfHabitantes["id_depto"] = dfHabitantes["id_depto"].astype(int)
#%%
# Modelo Relacional: Bibliotecas Populares
archivo_bibliotecas = r"TablasOriginales\bibliotecas-populares.csv"
bibliotecas = pd.read_csv(archivo_bibliotecas)

consultaSQL= """
            SELECT DISTINCT nro_conabip, nombre as nombre_BP, fecha_fundacion, id_departamento as id_depto, mail as email
            FROM bibliotecas
             """
dfBibliotecaPopular = dd.sql(consultaSQL).df()
# En este paso corregimos el id de Chascomús de 6217 a 6218
dfBibliotecaPopular['id_depto'] = np.where(dfBibliotecaPopular['id_depto'] == 6217, 6218,dfBibliotecaPopular['id_depto'] )
#%%
# Modelo Relacional: Provincias
archivo_colegios = r"TablasOriginales\2022_padron_oficial_establecimientos_educativos.xlsx"
colegios = pd.read_excel(archivo_colegios)
# Eliminamos las primeras filas por fuera de la tabla
colegios = colegios.iloc[5:,:]
# Nombramos bien todas las columnas
colegios.columns = colegios.iloc[0]
colegios = colegios.iloc[1:,:]
# Preparamos el dataframe con el nombre correcto de las columnas
consultaSQL= """
                SELECT Distinct Jurisdicción as nombre_prov, "Código de localidad" as id_prov
                FROM colegios
             """
dfProvincias = dd.sql(consultaSQL).df()
# Extraemos el codigo de provincia del codigo de localidad
dfProvincias["id_prov"] = dfProvincias["id_prov"].astype(str).str[:2].astype(int)
# Eliminamos repetidos
consultaSQL= """
                SELECT DISTINCT *
                FROM dfProvincias
             """
dfProvincias = dd.sql(consultaSQL).df()
#%%
# Modelo Relacional: Departamentos
consultaSQL= """
                SELECT DISTINCT id_depto, departamento
                FROM dfHabitantes_con_departamentos
             """
dfDepartamentos = dd.sql(consultaSQL).df()
# Creamos una nueva columna que extrae el codigo de provincia del codigo de departamento que ya tiene.
# Como trabajamos con la copia (que tiene el id_depto como string) lo podemos recortar correctamente:
dfDepartamentos["id_prov"] = dfDepartamentos["id_depto"].astype(str).str[:2].astype(int)

#%%
# Modelo Relacional : Establecimientos Educativos
def guardar_datos_ee(df):
    datos=df.copy()
    datos=datos.iloc[:,0:25] #elimiamoso las ultimas columnas que tienen info de colegios de otras modalidades (no comun)
    datos=dd.sql("""SELECT DISTINCT Cueanexo, Nombre as Nombre_EE, Sector, Ámbito, "Código de localidad", Localidad, "Nivel inicial - Jardín maternal", "Nivel inicial - Jardín de infantes", Primario, Secundario, "Secundario - INET"
             FROM datos
             WHERE Común !~~ ' '
             """).df() #nos quedamos con las columnas que nos importan, y descartamos los EE que no sean modalidad comun
    datos=dd.sql("""
             SELECT DISTINCT *
             FROM datos
             WHERE "Nivel inicial - Jardín maternal" !~~' ' OR "Nivel inicial - Jardín de infantes"!~~' ' OR Primario!~~' ' OR Secundario!~~' ' OR "Secundario - INET"!~~' '
             """).df() #como hay EE que son modalidad comun pero solo SNU o SNU INET, pero no nos interesan esos, eliminamos tambien los EE que no tengan ninguna de las modalidades que si nos interesan.
    
    #esta parte se ocupa de juntar las columnas de Secundario y Secundario INET, y los jardines infantiles y maternales
    datos['sec_combinados'] = ' '
    datos.loc[ (datos["Secundario"]=='1') | (datos["Secundario - INET"]=='1'), "sec_combinados" ]= '1'
    datos['jar_combinados'] = ' '
    datos.loc[ (datos["Nivel inicial - Jardín maternal"]=='1') | (datos["Nivel inicial - Jardín de infantes"]=='1'), "jar_combinados"]='1'
    datos=datos.drop(columns=["Secundario","Secundario - INET", "Nivel inicial - Jardín maternal", "Nivel inicial - Jardín de infantes"])
    datos=datos.rename(columns={'sec_combinados':'Secundario','jar_combinados':'Jardín'})    
    
    #si bien la tabla original venia con vacios (" ") o "1"s para indicar la modalidad de los colegios, nosotros
    #vamos a usar 1s y 0:
    datos.loc[(datos["Secundario"]==" "),"Secundario"]="0"
    datos.loc[(datos["Primario"]==" "),"Primario"]="0"
    datos.loc[(datos["Jardín"]==" "),"Jardín"]="0" 
    #los pasamos a int porque luego nos interesara sumarlos
    datos[["Primario","Secundario","Jardín"]]=datos[["Primario","Secundario","Jardín"]].astype(int)
    
    #aca armo una columna que tenga id_depto, derivado a partir de los primeros 5 digitos del codigo de localidad
    datos['id_depto']=datos['Código de localidad'].astype(str).str[0:5]
    #para CABA, como no podemos diferenciar entre comunas en la tabla de BP, agrupamos todas las comunas bajo un mismo id_depto, 2000.
    datos.loc[ datos['id_depto'].str[0:2]=="02","id_depto"]="2000"
    #cambiamos el dtype de id_depto a int por la misma razon que mencionamos antes
    datos["id_depto"]=datos["id_depto"].astype(int)
    #eliminamos la fila del EE en ANTARTIDA ARGENTINA
    datos=datos[datos["id_depto"]!=94028]
    return datos

dfEstablecimientosEducativos=guardar_datos_ee(colegios)
#%%
# Consula SQL 1


#aca primero queremos obtener la cantidad de colegios de cada nivel, por departamento, a partir de la tabla de EE
consulta1=dd.sql("""
                SELECT id_depto, SUM(Jardín) as Jardines, SUM(Primario) as Primarias, SUM(Secundario) as Secundarios
                FROM dfEstablecimientosEducativos
                GROUP BY id_depto
                """).df()
                
#hacemos join con los habitantes asi ahora tenemos la poblacion por nivel educativo tmb. Va a haber unos nulls en TOLHUIN pues
#no tiene escuelas. Por eso hacemos LEFT OUTER JOIN en lugar de NATURAL JOIN (queremos incluirlo).
consulta1=dd.sql("""
                            SELECT *
                            FROM dfHabitantes
                            LEFT OUTER JOIN consulta1
                            ON dfHabitantes.id_depto = consulta1.id_depto
                            
                            """).df()
                            
#Ahora eliminamos los nulls resultantes (en cantidad de colegios) y la columna repetida de id_depto
consulta1=dd.sql("""
                                   SELECT id_depto, jardin, primaria, secundaria, 
                                   IFNULL(Jardines,0) as Jardines,
                                   IFNULL(Primarias,0) as Primarias,
                                   IFNULL(Secundarios,0) as Secundarios,
                                   FROM consulta1
                                   """).df()


#este natural join lo hacemos para obtener el id provincia de cada departamento (y los nombres de cada departamento)
consulta1=dd.sql("""
                               SELECT *
                               FROM consulta1
                               NATURAL JOIN dfDepartamentos
                               """).df()
#y este natural join es para obtener el nombre de las provincias a partir del id
consulta1=dd.sql("""
                             SELECT *
                             FROM consulta1
                             NATURAL JOIN dfProvincias
                             """).df()       

#nos quedamos solo con las columnas que nos importan
consulta1=dd.sql("""
                       SELECT nombre_prov as Provincia, departamento as Departamento, Jardines, jardin as "Población Jardin", Primarias, primaria as "Población Primaria", Secundarios, secundaria as "Población Secundaria"
                       FROM consulta1
                       ORDER BY Provincia, Primarias DESC
                       """).df()
#%%
# Consulta SQL 2
# Agrego los datos de Provincia y Departamento correspondientemente para cada biblioteca
consultaSQL = """
                SELECT DISTINCT * 
                FROM dfBibliotecaPopular
                NATURAL JOIN dfDepartamentos
              """
consulta2 = dd.sql(consultaSQL).df()

consultaSQL = """
                SELECT DISTINCT *
                FROM consulta2
                NATURAL JOIN dfProvincias
              """
consulta2 = dd.sql(consultaSQL).df()

# Contamos en un nuevo df la cantidad de bibliotecas cuya fecha de fundación sea posterior a 01-01-1950
consultaSQL = """
                SELECT DISTINCT nombre_prov as Provincia, departamento as Departamento, 
                COUNT(CASE WHEN STRPTIME(fecha_fundacion, '%Y-%m-%d') >= DATE '1950-01-01' THEN 1 END) AS "Cantidad de BP fundadas desde 1950"
                FROM consulta2
                GROUP BY nombre_prov, departamento
              """
consulta2 = dd.sql(consultaSQL).df()

# Hacemos un nuevo df con los nombres de cada departamento junto con su provincia
consultaSQL = """
                SELECT DISTINCT nombre_prov as Provincia, departamento as Departamento
                FROM dfDepartamentos
                NATURAL JOIN dfProvincias
              """
deptos_provincias = dd.sql(consultaSQL).df()

# A cada departamento (lo buscamos haciendo coincidir departamento-provincia) le asignamos el total que contamos antes, y si no tiene total (porque no aparecía en bibliotecas)
# le ponemos un 0, así aparecen todos los departamentos como pide la consulta inicial.
consultaSQL = """
                SELECT deptos_provincias.Provincia, deptos_provincias.Departamento,
                CASE WHEN consulta2."Cantidad de BP fundadas desde 1950" IS NULL THEN 0
                     ELSE consulta2."Cantidad de BP fundadas desde 1950"
                END AS "Cantidad de BP fundadas desde 1950"
                FROM deptos_provincias
                LEFT JOIN consulta2
                ON deptos_provincias.Provincia = consulta2.Provincia AND deptos_provincias.Departamento = consulta2.Departamento
                ORDER BY deptos_provincias.Provincia, consulta2."Cantidad de BP fundadas desde 1950" DESC
              """
consulta2 = dd.sql(consultaSQL).df()
#%%
# Consulta SQL 3

#no todos los deptos tienen BP asi que hacemos left outer join para tener una tabla como
#dfBiblioteca popular pero con los deptos faltantes (esto implicara que los campos de la biblioteca seran
#nulos para estos deptos)
bp_con_todos_deptos=dd.sql("""
                           SELECT *
                           FROM dfDepartamentos
                           LEFT OUTER JOIN dfBibliotecaPopular
                           ON dfDepartamentos.id_depto=dfBibliotecaPopular.id_depto
                           """).df()

#ahora hago conteo de las bibliotecas por departamento
bp_por_depto=dd.sql("""
                    SELECT id_depto, SUM(CASE WHEN id_depto_1 IS NULL THEN 0 ELSE 1 END) as Cant_BP
                    FROM bp_con_todos_deptos
                    GROUP BY id_depto
                    """).df()


#quiero ahora agarrar la cant de colegios por depto
#pasa algo parecido que con BP; no hay EE en el departamento 94011. Hay que hacer el mismo procedimiento para
#contemplarlo
ee_con_todos_deptos=dd.sql("""
                                 SELECT *
                                 FROM dfDepartamentos
                                 LEFT OUTER JOIN dfEstablecimientosEducativos
                                 ON dfDepartamentos.id_depto=dfEstablecimientosEducativos.id_depto
                                 """).df()
ee_por_depto=dd.sql("""
                    SELECT id_depto, SUM(CASE WHEN id_depto_1 IS NULL THEN 0 ELSE 1 END) as Cant_EE
                    FROM ee_con_todos_deptos
                    GROUP BY id_depto
                    """).df()

#ahora tenemos por un lado las BP por depto, y los EE por depto por otro. Los podemos unir por NATURAL JOIN (comparten id_depto):

consulta3=dd.sql("""
                       SELECT * 
                       FROM ee_por_depto
                       NATURAL JOIN bp_por_depto
                       """).df()
#a esa tabla le agregamos la columna de poblacion por depto:
consulta3=dd.sql("""
                           SELECT *
                           FROM consulta3
                           NATURAL JOIN dfHabitantes
                           """).df()    
#ahora tenemos cant de establecimientos educativos, cant bibliotecas populares, y poblacion por depto    
#hago natural join con la tabla de departamentos pues ahi estan los nombres de los deptos y los ids provincia, que necesitare    
consulta3=dd.sql("""
                       SELECT *
                       FROM consulta3
                       NATURAL JOIN dfDepartamentos
                       """).df()

#hago natural join con la tabla de provincias
consulta3=dd.sql("""
                      SELECT * 
                      FROM consulta3
                      NATURAL JOIN dfProvincias
                      """).df()

#agarro las columnas que nos importan
consulta3=dd.sql("""
                 SELECT nombre_prov as Provincia, departamento as Departamento, Cant_EE, Cant_BP, total as Población
                 FROM consulta3
                 ORDER BY cant_EE DESC, cant_BP DESC, Provincia, Departamento
                 """).df()


#%%
# Consulta SQL 4
# De dfBibliotecaPopular me quedo solo con id_depto y email
# Pero solo aquellos emails con formato válido (ni nulls ni mails que no contengan @ (dominio) . ) (asi evitamos casos sin dominio)
consultaSQL = """
                SELECT id_depto, email
                FROM dfBibliotecaPopular
                WHERE email IS NOT NULL
                    AND email LIKE '%@%.%'
              """
consulta4 = dd.sql(consultaSQL).df()

# Agregamos columna dominio donde recortamos el dominio (parte entre el @ y el primer . que lo sigue) de cada mail del df
consultaSQL = """
                SELECT id_depto, email,
                SUBSTR(email, INSTR(email, '@') + 1, INSTR(SUBSTR(email, INSTR(email, '@') + 1), '.') - 1)
                AS dominio
                FROM consulta4
               """
consulta4 = dd.sql(consultaSQL).df()

# Contamos la cantidad de apariciones de cada dominio por departamento
consulta4=dd.sql("""
                 SELECT id_depto,dominio, COUNT(*) as apariciones
                 FROM consulta4
                 GROUP BY dominio, id_depto
                 ORDER BY apariciones
                 """).df()

# Extraemos un df de recuento donde, ordenando de mayor a menor las apariciones, borramos a las filas cuyos codigos aparezcan más de una vez
# Solo dejamos la primera aparición, la cual va a estar asociada al dominio más frecuente pues aparecerán primero las de mayor apariciones
# En casos de empate, escogemos dar cualquiera de los dos dominios, ambos serían correctos.
consultaSQL = """
                SELECT c.id_depto,
                       MIN(c.dominio) AS dominio,
                       c.apariciones
                FROM consulta4 c
                JOIN (
                    SELECT id_depto, MAX(apariciones) AS max_apariciones
                    FROM consulta4
                    GROUP BY id_depto
                ) max_valores ON c.id_depto = max_valores.id_depto AND c.apariciones = max_valores.max_apariciones
                GROUP BY c.id_depto, c.apariciones
              """
consulta4 = dd.sql(consultaSQL).df()

# Creamos un df con nombres e id de departamentos con sus provincias para hacer join después
consultaSQL = """
                SELECT *
                FROM dfDepartamentos
                NATURAL JOIN dfProvincias
              """
deptos_provincias_con_id = dd.sql(consultaSQL).df()
consultaSQL = """
                SELECT nombre_prov as Provincia, departamento as Departamento, dominio as "Dominio más frecuente en BP" 
                FROM consulta4
                NATURAL JOIN deptos_provincias_con_id
              """           
consulta4 = dd.sql(consultaSQL).df()

# Buscamos a todos los departamentos, con sus respectivas provincias, y a cada uno de ellos les agregamos en la columna
# Dominio más frecuente en BP, su respectivo dominio. Para aquellas que no tengan mail, les asignamos "Dato Faltante"
# Como la consulta pedía específicamente "para cada departamento" por más que no tengan el dominio que se consulta, los ubicamos en la tabla con ese valor.
consultaSQL = """
                SELECT deptos_provincias.Provincia, deptos_provincias.Departamento,
                CASE WHEN consulta4."Dominio más frecuente en BP" IS NULL THEN 'Dato Faltante'
                    ELSE consulta4."Dominio más frecuente en BP"
                END AS "Dominio más frecuente en BP"
                FROM deptos_provincias
                LEFT JOIN consulta4
                ON deptos_provincias.Provincia = consulta4.Provincia AND deptos_provincias.Departamento = consulta4.Departamento
              """
consulta4 = dd.sql(consultaSQL).df()
#%% #Primer gráfico


fig, ax = plt.subplots()
consulta3_agrupada = consulta3.groupby('Provincia', as_index=False)['Cant_BP'].sum()
consulta3_agrupada_ordenada = consulta3_agrupada.sort_values(by='Cant_BP', ascending= False)

ax.bar(data = consulta3_agrupada_ordenada, x= 'Provincia', height = 'Cant_BP', width=0.6)
ax.set_title('') 
ax.set_xlabel('Provincia')
ax.set_ylabel('Cantidad BP')
plt.xticks(rotation=50, ha='right')
ax.yaxis.grid(True, linestyle='-', alpha = 0.7)
ax.bar_label(ax.containers[0], fontsize=8)
plt.tight_layout()
plt.show()

#%% Segundo gráfico
# Función formatear miles
def formatear_miles(x,_):
    return f'{x:,.0f}'.replace(',','.')

fig, ax = plt.subplots()

ax.scatter(data = consulta1,
           x= 'Población Jardin',
           y= 'Jardines',
           c = 'blue',
           label = 'Nivel inicial (0-5 años)',
           alpha = 0.5)
ax.scatter(data = consulta1,
           x= 'Población Primaria',
           y= 'Primarias',
           c = 'orange',
           label = 'Nivel primario (6-11 años)',
           alpha = 0.5)
ax.scatter(data = consulta1,
           x= 'Población Secundaria',
           y= 'Secundarios',
           c = 'green',
           label = 'Nivel secundario (12-18 años)',
           alpha = 0.5)

ax.set_title('')
ax.set_xlabel('Población')
ax.set_ylabel('Cantidad EE')
plt.gca().yaxis.set_major_formatter(FuncFormatter(formatear_miles))
plt.gca().xaxis.set_major_formatter(FuncFormatter(formatear_miles))
ax.legend()
plt.tight_layout()
plt.grid(True)

# Segundo gráfico con zoom
fig, ax = plt.subplots()

ax.scatter(data = consulta1,
           x= 'Población Jardin',
           y= 'Jardines',
           c = 'blue',
           label = 'Nivel inicial (0-5 años)',
           alpha = 0.5)
ax.scatter(data = consulta1,
           x= 'Población Primaria',
           y= 'Primarias',
           c = 'orange',
           label = 'Nivel primario (6-11 años)',
           alpha = 0.5)
ax.scatter(data = consulta1,
           x= 'Población Secundaria',
           y= 'Secundarios',
           c = 'green',
           label = 'Nivel secundario (12-18 años)',
           alpha = 0.5)

ax.set_title('')
ax.set_xlabel('Población')
ax.set_ylabel('Cantidad EE')
ax.legend()
ax.set_ylim(0,250)
ax.set_xlim(0,80000)
plt.gca().yaxis.set_major_formatter(FuncFormatter(formatear_miles))
plt.gca().xaxis.set_major_formatter(FuncFormatter(formatear_miles))
plt.tight_layout()
plt.grid(True)
plt.show()

#%% Tercer gráfico
# Ordenamos consulta3 según la mediana de cantidad de establecimientos educativos por departamento de cada provincia
orden_provincias = consulta3.groupby('Provincia', observed = False)['Cant_EE'].median().sort_values().index
consulta3['Provincia'] = pd.Categorical(consulta3['Provincia'], categories=orden_provincias, ordered=True)
consulta3_sin_caba = consulta3[consulta3['Provincia'] != 'Ciudad de Buenos Aires']
consulta3_sin_caba['Provincia'] = consulta3_sin_caba['Provincia'].cat.remove_unused_categories()
fig, ax = plt.subplots(figsize=(10,6))
consulta3_sin_caba.boxplot(by='Provincia', column='Cant_EE',ax=ax, grid=False, showmeans=True, meanprops=dict(marker='^', markersize=4, markerfacecolor='black'))
fig.suptitle('')
ax.set_title('')
ax.set_xlabel('Provincias')
ax.set_ylabel('Cantidad de Establecimientos Educativos')
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
ax.spines[['right','top']].set_visible(False)
plt.tight_layout()
plt.show()

#%% Tercer gráfico con zoom
fig, ax = plt.subplots(figsize=(10,6))
consulta3_sin_caba.boxplot(by='Provincia', column='Cant_EE',ax=ax, grid=False, showmeans=True, meanprops=dict(marker='^', markersize=4, markerfacecolor='black'))
consulta3_sin_caba['Provincia'] = consulta3_sin_caba['Provincia'].cat.remove_unused_categories()
fig.suptitle('')
ax.set_title('')
ax.set_xlabel('Provincias')
ax.set_ylabel('Cantidad de Establecimientos Educativos')
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
ax.spines[['right','top']].set_visible(False)
ax.set_ylim(bottom=1, top=400)
plt.tight_layout()
plt.show()
#%% Cuarto grafico

data3=consulta3.copy()
#Calculo cantidad de BP y EE cada 1000 habitantes para cada depto
data3["BP_c/1000"]=data3["Cant_BP"]*1000 / data3["Población"]
data3["EE_c/1000"]=data3["Cant_EE"]*1000 / data3["Población"]

fig, ax = plt.subplots()

ax.scatter(data = data3,
           x= 'EE_c/1000',
           y= 'BP_c/1000',
           alpha = 0.5)


ax.set_title('',fontsize=11)
ax.set_xlabel('Establecimientos educativos cada 1000 habitantes',fontsize=8)
ax.set_ylabel('Bibliotecas populares cada 1000 habitantes',fontsize=8)
ax.legend().remove()
plt.tight_layout()
plt.grid(True)
plt.show()
#%% Cuarto grafico con zoom

data3=consulta3.copy()
#Calculo cantidad de BP y EE cada 1000 habitantes para cada depto
data3["BP_c/1000"]=data3["Cant_BP"]*1000 / data3["Población"]
data3["EE_c/1000"]=data3["Cant_EE"]*1000 / data3["Población"]

fig, ax = plt.subplots()

ax.scatter(data = data3,
           x= 'EE_c/1000',
           y= 'BP_c/1000',
           alpha = 0.5)


ax.set_title('',fontsize=11)
ax.set_xlabel('Establecimientos educativos cada 1000 habitantes',fontsize=12)
ax.set_ylabel('Bibliotecas populares cada 1000 habitantes',fontsize=12)
ax.set_xlim(0,5)
ax.set_ylim(-0.01,0.5)
ax.legend().remove()
plt.tight_layout()
plt.grid(True)
plt.show()
#%%

#GRAFICOS ADICIONALES:


#OBTENGO La data que quiero con consultas:
#cant de bps por depto    
Nbp_con_todos_deptos_sucio=dd.sql("""
                           SELECT *
                           FROM dfDepartamentos
                           LEFT OUTER JOIN dfBibliotecaPopular
                           ON dfDepartamentos.id_depto=dfBibliotecaPopular.id_depto
                           """).df()

Nbp_por_depto=dd.sql("""
                    SELECT id_depto, SUM(CASE WHEN id_depto_1 IS NULL THEN 0 ELSE 1 END) as Cant_BP
                    FROM Nbp_con_todos_deptos_sucio
                    GROUP BY id_depto
                    """).df()

#para cant de ee publicos

EE_estatales=dd.sql("""
                    SELECT *
                    FROM dfEstablecimientosEducativos
                    WHERE Sector= 'Estatal'
                    """)

estatales_con_todos_deptos_sucio=dd.sql("""
                                 SELECT *
                                 FROM dfDepartamentos
                                 LEFT OUTER JOIN EE_estatales
                                 ON dfDepartamentos.id_depto=EE_estatales.id_depto
                                 """).df()
Estatales_por_depto=dd.sql("""
                    SELECT id_depto, SUM(CASE WHEN Cueanexo IS NULL THEN 0 ELSE 1 END) as Cant_EE
                    FROM estatales_con_todos_deptos_sucio
                    GROUP BY id_depto
                    """).df()
consultaEstatal=dd.sql("""
                       SELECT * 
                       FROM Estatales_por_depto
                       NATURAL JOIN Nbp_por_depto
                       """).df()
consultaEstatal=dd.sql("""
                           SELECT *
                           FROM consultaEstatal
                           NATURAL JOIN dfHabitantes
                           """).df()     
                    
consultaEstatal=dd.sql("""
                 SELECT id_depto, Cant_EE, Cant_BP, total as Población
                 FROM consultaEstatal
                 """).df()


#ahora para cant de ee privados
EE_privados=dd.sql("""
                    SELECT *
                    FROM dfEstablecimientosEducativos
                    WHERE Sector= 'Privado'
                    """)

privados_con_todos_deptos_sucio=dd.sql("""
                                 SELECT *
                                 FROM dfDepartamentos
                                 LEFT OUTER JOIN EE_privados
                                 ON dfDepartamentos.id_depto=EE_privados.id_depto
                                 """).df()
privados_por_depto=dd.sql("""
                    SELECT id_depto, SUM(CASE WHEN Cueanexo IS NULL THEN 0 ELSE 1 END) as Cant_EE
                    FROM privados_con_todos_deptos_sucio
                    GROUP BY id_depto
                    """).df()
consultaPrivado=dd.sql("""
                       SELECT * 
                       FROM privados_por_depto
                       NATURAL JOIN Nbp_por_depto
                       """).df()
consultaPrivado=dd.sql("""
                           SELECT *
                           FROM consultaPrivado
                           NATURAL JOIN dfHabitantes
                           """).df()     
                    
consultaPrivado=dd.sql("""
                 SELECT id_depto, Cant_EE, Cant_BP, total as Población
                 FROM consultaPrivado
                 """).df()


dataE=consultaEstatal.copy()
dataE["BP_c/1000"]=dataE["Cant_BP"]*1000/ dataE["Población"]
dataE["EE_c/1000"]=dataE["Cant_EE"]*1000/ dataE["Población"]
dataE=dd.sql("""
             SELECT *
             FROM dataE
             
             """).df()

dataP=consultaPrivado.copy()
dataP["BP_c/1000"]=dataP["Cant_BP"]*1000 / dataP["Población"]
dataP["EE_c/1000"]=dataP["Cant_EE"]*1000/ dataP["Población"]
dataP=dd.sql("""
             SELECT *
             FROM dataP
             
             """).df()

fig, ax = plt.subplots()

#PLOTEA LA RELACION ENTRE EE CADA 1000 HABITANTES (SEPARANDO POR SECTOR) Y BP CADA 1000 HABITANTES
ax.scatter(data = dataE,
           x= 'EE_c/1000',
           y= 'BP_c/1000',
           c="green",
           label="Estatales",
           alpha = 0.3)
ax.scatter(data=dataP,
           x= 'EE_c/1000',
           y= 'BP_c/1000',
           c="orange",
           label="Privados",
           alpha = 0.3)

ax.set_xlabel('EE cada 1000 habitantes')
ax.set_ylabel('BP cada 1000 habitantes')
ax.legend()
plt.tight_layout()
plt.grid(True)
plt.show()
#%% con zoom
fig, ax = plt.subplots()

#PLOTEA LA RELACION ENTRE EE CADA 1000 HABITANTES (SEPARANDO POR SECTOR) Y BP CADA 1000 HABITANTES
ax.scatter(data = dataE,
           x= 'EE_c/1000',
           y= 'BP_c/1000',
           c="green",
           label="Estatales",
           alpha = 0.3)
ax.scatter(data=dataP,
           x= 'EE_c/1000',
           y= 'BP_c/1000',
           c="orange",
           label="Privados",
           alpha = 0.3)

#ax.set_title('Relacion entre cantidad de BP y EE cada 1000 habitantes por depto')
ax.set_xlabel('EE cada 1000 habitantes')
ax.set_ylabel('BP cada 1000 habitantes')
ax.set_ylim(-0.01,0.7)
ax.set_xlim(-0.05,5)
ax.legend()
plt.tight_layout()
plt.grid(True)
plt.show()

#%%
#LO MISMO PERO RURAL VS URBANO
#OBTENGO La data que quiero con consultas:
#cant de bps por depto    
Nbp_con_todos_deptos_sucio=dd.sql("""
                           SELECT *
                           FROM dfDepartamentos
                           LEFT OUTER JOIN dfBibliotecaPopular
                           ON dfDepartamentos.id_depto=dfBibliotecaPopular.id_depto
                           """).df()

Nbp_por_depto=dd.sql("""
                    SELECT id_depto, SUM(CASE WHEN id_depto_1 IS NULL THEN 0 ELSE 1 END) as Cant_BP
                    FROM Nbp_con_todos_deptos_sucio
                    GROUP BY id_depto
                    """).df()

#para cant de ee publicos

EE_rurales=dd.sql("""
                    SELECT *
                    FROM dfEstablecimientosEducativos
                    WHERE Ámbito= 'Rural'
                    """)

rurales_con_todos_deptos_sucio=dd.sql("""
                                 SELECT *
                                 FROM dfDepartamentos
                                 LEFT OUTER JOIN EE_rurales
                                 ON dfDepartamentos.id_depto=EE_rurales.id_depto
                                 """).df()
rurales_por_depto=dd.sql("""
                    SELECT id_depto, SUM(CASE WHEN Cueanexo IS NULL THEN 0 ELSE 1 END) as Cant_EE
                    FROM rurales_con_todos_deptos_sucio
                    GROUP BY id_depto
                    """).df()
consultaRural=dd.sql("""
                       SELECT * 
                       FROM rurales_por_depto
                       NATURAL JOIN Nbp_por_depto
                       """).df()
consultaRural=dd.sql("""
                           SELECT *
                           FROM consultaRural
                           NATURAL JOIN dfHabitantes
                           """).df()     
                    
consultaRural=dd.sql("""
                 SELECT id_depto, Cant_EE, Cant_BP, total as Población
                 FROM consultaRural
                 """).df()


#ahora para cant de ee privados
EE_urbanos=dd.sql("""
                    SELECT *
                    FROM dfEstablecimientosEducativos
                    WHERE Ámbito= 'Urbano'
                    """)

urbanos_con_todos_deptos_sucio=dd.sql("""
                                 SELECT *
                                 FROM dfDepartamentos
                                 LEFT OUTER JOIN EE_urbanos
                                 ON dfDepartamentos.id_depto=EE_urbanos.id_depto
                                 """).df()
urbanos_por_depto=dd.sql("""
                    SELECT id_depto, SUM(CASE WHEN Cueanexo IS NULL THEN 0 ELSE 1 END) as Cant_EE
                    FROM urbanos_con_todos_deptos_sucio
                    GROUP BY id_depto
                    """).df()
consultaUrbano=dd.sql("""
                       SELECT * 
                       FROM urbanos_por_depto
                       NATURAL JOIN Nbp_por_depto
                       """).df()
consultaUrbano=dd.sql("""
                           SELECT *
                           FROM consultaUrbano
                           NATURAL JOIN dfHabitantes
                           """).df()     
                    
consultaUrbano=dd.sql("""
                 SELECT id_depto, Cant_EE, Cant_BP, total as Población
                 FROM consultaUrbano
                 """).df()


dataR=consultaRural.copy()
dataR["BP_c/1000"]=dataR["Cant_BP"]*1000/ dataR["Población"]
dataR["EE_c/1000"]=dataR["Cant_EE"]*1000/ dataR["Población"]
dataR=dd.sql("""
             SELECT *
             FROM dataR

             """).df()

dataU=consultaUrbano.copy()
dataU["BP_c/1000"]=dataU["Cant_BP"]*1000 / dataU["Población"]
dataU["EE_c/1000"]=dataU["Cant_EE"]*1000 / dataU["Población"]
dataU=dd.sql("""
             SELECT *
             FROM dataU

             """).df()

fig, ax = plt.subplots()

ax.scatter(data = dataR,
           x= 'EE_c/1000',
           y= 'BP_c/1000',
           c="red",
           label="Rurales",
           alpha = 0.5)
ax.scatter(data=dataU,
           x= 'EE_c/1000',
           y= 'BP_c/1000',
           c="blue",
           label="Urbanos",
           alpha = 0.2)

ax.set_xlabel('EE cada 1000 habitantes')
ax.set_ylabel('BP cada 1000 habitantes')
ax.legend()
plt.tight_layout()
plt.grid(True)
plt.show()

#%% con zoom
fig, ax = plt.subplots()

ax.scatter(data = dataR,
           x= 'EE_c/1000',
           y= 'BP_c/1000',
           c="red",
           label="Rurales",
           alpha = 0.5)
ax.scatter(data=dataU,
           x= 'EE_c/1000',
           y= 'BP_c/1000',
           c="blue",
           label="Urbanos",
           alpha = 0.2)

ax.set_xlabel('EE cada 1000 habitantes')
ax.set_ylabel('BP cada 1000 habitantes')
ax.set_ylim(-0.01,1)
ax.set_xlim(-0.05,6)
ax.legend()
plt.tight_layout()
plt.grid(True)
plt.show()

#%% chequeo si existe algun depto con mas privados que publicos
chequeo=dd.sql("""
               SELECT p.id_depto, p.Cant_EE as EE_privados, e.Cant_EE as EE_estatales
               FROM consultaPrivado AS p
               INNER JOIN consultaEstatal AS e
               ON p.id_depto=e.id_depto
               WHERE p.cant_EE > e.cant_EE
               """).df()
#obtenemos los nombres de los departamentos
chequeo_con_nombre_deptos=dd.sql("""
                                 SELECT *
                                 FROM chequeo
                                 INNER JOIN dfDepartamentos
                                 ON chequeo.id_depto=dfDepartamentos.id_depto
                                 """).df()
