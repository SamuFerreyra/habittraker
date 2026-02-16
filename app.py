import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Mi Habit Tracker Pro", page_icon="🔥")
st.title("Habit Tracker ")

# --- LISTA DE HÁBITOS ---
habitos_lista = [
    "Hacer ejercicio", "Leer", "Meditar", "Devocional", 
    "Beber agua", "Estudiar", "Ayudar en la casa", "Trabajar", "Orar","No caer 🚫"
]

# --- INTENTO DE CONEXIÓN ---
df_historico = pd.DataFrame(columns=["Fecha", "Habito", "Completado"])
modo_nube = False

try:
    # Intentamos conectar con Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    # IMPORTANTE: Cambié el nombre de la hoja al que vi en tu captura
    df_historico = conn.read(worksheet="Configuración del Admin de Django")
    modo_nube = True
except Exception:
    # Si falla (en local sin secretos), intentamos cargar el CSV local
    if os.path.exists("datos_habitos.csv"):
        df_historico = pd.read_csv("datos_habitos.csv")
    st.info("💡 Nota: Usando almacenamiento local (CSV). Configura Secrets para la nube.")

# --- INTERFAZ DE USUARIO ---
hoy = date.today()
st.subheader(f"Tareas para hoy: {hoy.strftime('%d/%m/%Y')}")

cols = st.columns(2)
estados = {}
for i, h in enumerate(habitos_lista):
    col = cols[i % 2]
    estados[h] = col.checkbox(h, key=h)

# --- BOTÓN DE GUARDADO ---
if st.button("Guardar mi día 📱"):
    # Preparamos los nuevos datos
    nuevas_filas = pd.DataFrame([
        {"Fecha": str(hoy), "Habito": h, "Completado": estados[h]} for h in habitos_lista
    ])
    
    # Unir con lo anterior evitando duplicados de hoy
    if not df_historico.empty:
        df_limpio = df_historico[df_historico['Fecha'] != str(hoy)]
        df_actualizado = pd.concat([df_limpio, nuevas_filas], ignore_index=True)
    else:
        df_actualizado = nuevas_filas

    # GUARDAR según el modo
    try:
        if modo_nube:
            conn.update(worksheet="Configuración del Admin de Django", data=df_actualizado)
            st.success("¡Sincronizado con Google Sheets! ✅")
        else:
            df_actualizado.to_csv("datos_habitos.csv", index=False)
            st.success("¡Guardado en el archivo local! ✅")
        st.balloons()
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        # Dentro del bloque: if st.button("Guardar mi día en la nube ☁️"):
    try:
        # Usamos el nombre exacto que le pongas a la pestaña abajo en el Excel
        #    Si le pusiste "Hoja1", aquí debe decir "Hoja1"
        conn.update(worksheet="Hoja1", data=df_actualizado) 
        st.success("¡Guardado en la nube! 📱")
        st.balloons()
    except Exception as e:
        st.error(f"Error al subir: {e}")
        st.info("Asegúrate de que compartiste el Excel con el email de la Service Account como EDITOR.")
    
    

# --- RESUMEN SEMANAL ---
st.divider()
with st.expander("Ver avance semanal"):
    if not df_historico.empty:
        df_stats = df_historico.copy()
        df_stats['Fecha'] = pd.to_datetime(df_stats['Fecha'])
        # Calculamos progreso semanal
        semana_actual = hoy.isocalendar()[1]
        df_stats['Semana'] = df_stats['Fecha'].dt.isocalendar().week
        df_semana = df_stats[df_stats['Semana'] == semana_actual]
        
        if not df_semana.empty:
            df_semana['Completado'] = df_semana['Completado'].astype(int)
            resumen = df_semana.groupby(df_semana['Fecha'].dt.day_name())['Completado'].mean() * 100
            st.bar_chart(resumen)
        else:
            st.write("Aún no hay datos de esta semana.")
    else:
        st.write("Registra tu primer día para ver estadísticas.")