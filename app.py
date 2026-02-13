import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Mi Habit Tracker Pro", page_icon="🔥")

st.title("Habit Tracker con Memoria 🧠☁️")

# 1. CONEXIÓN A GOOGLE SHEETS
# Nota: Debes configurar el enlace de tu Google Sheet en .streamlit/secrets.toml
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_historico = conn.read()
except Exception:
    # Si falla la conexión (por falta de configuración), crea un DF vacío para no romper la app
    df_historico = pd.DataFrame(columns=["Fecha", "Habito", "Completado"])

# --- INTERFAZ DE REGISTRO DIARIO ---
hoy = date.today()
habitos_lista = [
    "Hacer ejercicio", "Leer", "Meditar", "Devocional", 
    "Beber agua", "Estudiar", "Ayudar en la casa", "Trabajar", "Orar"
]

st.subheader(f"Tareas para hoy: {hoy.strftime('%d/%m/%Y')}")

# Usamos columnas para que los checkboxes se vean más ordenados
cols = st.columns(2)
estados = {}

for i, h in enumerate(habitos_lista):
    col = cols[i % 2] # Alterna entre columna 1 y 2
    estados[h] = col.checkbox(h, key=h)

# Botón para guardar en la nube
if st.button("Guardar mi día en la nube ☁️"):
    # Preparamos los nuevos datos
    nuevas_filas = pd.DataFrame([
        {"Fecha": str(hoy), "Habito": h, "Completado": estados[h]} for h in habitos_lista
    ])
    
    # Filtramos el historial para eliminar registros viejos del mismo día (evitar duplicados)
    if not df_historico.empty:
        df_historico = df_historico[df_historico['Fecha'] != str(hoy)]
    
    # Unimos lo viejo con lo nuevo
    df_actualizado = pd.concat([df_historico, nuevas_filas], ignore_index=True)
    
    # SUBIR A GOOGLE SHEETS
    conn.update(data=df_actualizado)
    st.success("¡Progreso guardado y sincronizado!")
    st.balloons()

# --- SECCIÓN DE RESUMEN ---
st.divider()

def mostrar_resumen_semanal(datos):
    if datos.empty:
        st.warning("No hay datos suficientes para mostrar estadísticas.")
        return

    # Convertir fechas y calcular semana
    df = datos.copy()
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    semana_actual = date.today().isocalendar()[1]
    df['Semana'] = df['Fecha'].dt.isocalendar().week
    
    # Filtrar semana actual
    df_semana = df[df['Semana'] == semana_actual]

    if not df_semana.empty:
        # Agrupar por nombre de día
        # Aseguramos que 'Completado' sea numérico para sacar el promedio
        df_semana['Completado'] = df_semana['Completado'].astype(int)
        resumen = df_semana.groupby(df_semana['Fecha'].dt.day_name())['Completado'].mean() * 100
        
        st.write("### 📊 Balance de la Semana")
        st.bar_chart(resumen)
        
        promedio_total = resumen.mean()
        st.metric("Cumplimiento total semanal", f"{promedio_total:.0f}%")
    else:
        st.info("Aún no tienes registros de esta semana.")

# Lógica de visualización (Domingo o Botón)
es_domingo = hoy.weekday() == 6

if es_domingo:
    st.header("¡Es Domingo! 🍎")
    mostrar_resumen_semanal(df_historico)
else:
    with st.expander("Ver avance semanal anticipado"):
        mostrar_resumen_semanal(df_historico)

# Mostrar tabla de datos crudos (opcional)
if st.sidebar.checkbox("Mostrar historial completo"):
    st.sidebar.write(df_historico)