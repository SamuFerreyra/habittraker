import streamlit as st
import pandas as pd
from datetime import date
import os

# Nombre del archivo donde guardaremos todo
DB_FILE = "datos_habitos.csv"

# --- FUNCIÓN PARA CARGAR DATOS ---
def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # Si no existe, creamos un DataFrame vacío con columnas
        return pd.DataFrame(columns=["Fecha", "Habito", "Completado"])

# --- FUNCIÓN PARA GUARDAR DATOS ---
def guardar_progreso(fecha, habitos_estado):
    df = cargar_datos()
    # Filtramos para no duplicar datos del mismo día si ya existen
    df = df[df['Fecha'] != str(fecha)]
    
    # Creamos los nuevos datos
    nuevos_datos = []
    for habito, estado in habitos_estado.items():
        nuevos_datos.append({"Fecha": str(fecha), "Habito": habito, "Completado": estado})
    
    # Unimos y guardamos
    df_actualizado = pd.concat([df, pd.DataFrame(nuevos_datos)], ignore_index=True)
    df_actualizado.to_csv(DB_FILE, index=False)
    st.success("¡Progreso guardado en el disco!")

# --- INTERFAZ ---
st.title("Habit Tracker con Memoria 🧠")

hoy = date.today()
habitos_lista = ["Hacer ejercicio", "Leer", "Meditar","Devocional","bebr agua","estudiar","ayudar en la casa", "trabajar","Orar"]
estados = {}

# Mostrar checkboxes
for h in habitos_lista:
    estados[h] = st.checkbox(h, key=h)

# Botón para guardar manualmente
if st.button("Guardar mi día"):
    guardar_progreso(hoy, estados)

# --- MOSTRAR HISTORIAL ---
st.divider()
st.subheader("Tu historial guardado")
datos_historicos = cargar_datos()
st.dataframe(datos_historicos)




# --- FUNCIÓN PARA CARGAR Y PROCESAR SEMANA ---
def mostrar_resumen_semanal():
    df = pd.read_csv("datos_habitos.csv")
    
    # Convertir la columna Fecha a formato de fecha real para que Python la entienda
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # Obtener el número de la semana actual
    semana_actual = date.today().isocalendar()[1]
    df['Semana'] = df['Fecha'].dt.isocalendar().week
    
    # Filtrar solo los datos de esta semana
    datos_semana = df[df['Semana'] == semana_actual]

    if not datos_semana.empty:
        # Calcular porcentaje por día
        # Agrupamos por fecha y calculamos el promedio de "Completado"
        resumen = datos_semana.groupby(datos_semana['Fecha'].dt.strftime('%A'))['Completado'].mean() * 100
        
        st.write("### 📊 Balance de la Semana")
        st.bar_chart(resumen)
        
        promedio_total = resumen.mean()
        st.metric("Cumplimiento total semanal", f"{promedio_total:.0f}%")
    else:
        st.warning("Aún no hay datos guardados para esta semana.")

# --- LÓGICA PARA MOSTRARLO SOLO LOS DOMINGOS ---
hoy = date.today()
es_domingo = hoy.weekday() == 6 # En Python, 6 es Domingo

if es_domingo:
    st.header("¡Es Domingo! 🍎")
    st.subheader("Aquí tienes el resumen de tu esfuerzo:")
    mostrar_resumen_semanal()
else:
    # Si no es domingo, podemos poner un botón opcional para "ver cómo voy"
    if st.sidebar.button("Ver avance semanal anticipado"):
        mostrar_resumen_semanal()