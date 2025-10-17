import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# ===========================================
# CONFIGURACIÓN GENERAL Y CONTRASEÑA
# ===========================================
st.set_page_config(page_title="Escuela Regenerativa Ambiental AUCCA", layout="wide")

# --- Encabezado con logo ---
logo_path = "logo_aucca.png"
col1, col2 = st.columns([1, 5])
with col1:
    logo = Image.open(logo_path)
    st.image(logo, use_column_width=True)
with col2:
    st.markdown("""
        <div style='padding-top:10px;'>
            <p style='font-size:22px; color:#444; margin-bottom:0;'>
                Escuela Regenerativa Ambiental de Talagante
            </p>
            <p style='font-size:16px; color:#777; margin-top:0;'>
                Visualizador de participantes · 2025
            </p>
        </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# --- Sistema de contraseña ---
st.markdown("### 🔐 Acceso restringido")
password = st.text_input("Introduce el código de acceso:", type="password")
if password != "compost":
    st.warning("⚠️ Ingrese el código correcto para acceder a la información.")
    st.stop()

# ===========================================
# CARGA DE DATOS
# ===========================================
sheet_url = "https://docs.google.com/spreadsheets/d/1aY3yE7h2Q_PvUVzTG55rWmaiSybk4qKDblvPDp2PWgo/edit?usp=sharing"
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

df = load_data(csv_url)

# ===========================================
# DEFINICIÓN DE VARIABLES CLAVE
# ===========================================
COL_CUIDADORA = "¿Eres cuidadora o cuidador de niños, niñas, personas mayores u otras personas dependientes?\n(En caso afirmativo, te contamos que durante los talleres habrá un espacio paralelo de actividades para infancias entre 5 y 12 años, para que puedas participar con tranquilidad)."
COL_INFANCIAS = "Nombre y edad de cada niño/a"
COL_MOTIVOS = "¿Qué te motiva a participar en la Escuela Regenerativa Ambiental de Talagante y qué dudas o comentarios quieres compartirnos?\n(Esta respuesta es abierta y nos ayudará a mejorar la experiencia y acompañar mejor tu proceso)."

TALLERES = {
    "Taller 1: Compostaje y Lombricultura":
        "Taller 1: Compostaje y Lombricultura\n📅 Sábado 18 de octubre de 2025 – 11:00 a 13:00 hrs\n📝 Este taller entrega herramientas para transformar los residuos orgánicos de la cocina y el jardín en abono natural. Aprenderás el paso a paso del compostaje y cómo criar lombrices californianas que ayudan a producir un humus rico en nutrientes para la tierra.",
    "Taller 2: Reproducción de especies vegetales":
        "Taller 2: Reproducción de especies vegetales\n📅 Sábado 25 de octubre de 2025 – 11:00 a 13:00 hrs\n📝 Conoceremos distintas técnicas para multiplicar plantas, como esquejes, estacas y división de raíces. Este taller busca entregar conocimientos básicos para aumentar la diversidad de especies en tu huerto o jardín, favoreciendo la soberanía alimentaria.",
    "Taller 3: Guardado de semillas":
        "Taller 3: Guardado de semillas\n📅 Sábado 25 de octubre de 2025 – 16:00 a 18:00 hrs\n📝 Aprenderás cómo cosechar, limpiar, seleccionar y conservar semillas para la siguiente temporada de cultivo. Este taller busca rescatar prácticas tradicionales y comunitarias de resguardo de semillas, fundamentales para mantener la biodiversidad agrícola y la autonomía en la producción de alimentos.",
    "Taller 4: Carpintería (Punto limpio con enfoque de género)":
        "Taller 4: Carpintería para la construcción de punto limpio (con enfoque de género)\n📅 Sábado 01 de noviembre de 2025 – 11:00 a 13:00 hrs\n📝 Aprenderemos técnicas básicas de carpintería para fabricar estructuras de madera que permitan separar y almacenar residuos reciclables en el hogar.",
    "Taller 5: Construcción de invernadero":
        "Taller 5: Construcción de invernadero para viverismo\n📅 Sábado 8 de noviembre de 2025 – 11:00 a 18:00 hrs (jornada completa)\n📝 Durante una jornada completa trabajaremos en equipo para levantar un invernadero en el centro eco pedagógico AUCCA.",
    "Taller 6: Cosecha de aguas lluvias":
        "Taller 6: Cosecha de aguas lluvias\n📅 Sábado 15 de Noviembre de 2025 – 11:00 a 13:00 hrs\n📝 Exploraremos métodos simples y prácticos para captar y almacenar agua de lluvia en nuestras casas y huertos."
}


# ===========================================
# FILTRO PRINCIPAL ROBUSTO POR NÚMERO DE TALLER
# ===========================================
st.header("🎯 Filtro principal")

taller_options = list(TALLERES.keys()) + ["📊 Ver todo (todos los talleres)"]
selected_taller = st.selectbox("Selecciona un taller para analizar", taller_options)

def find_taller_column(df, taller_num):
    for col in df.columns:
        if col.strip().lower().startswith(f"taller {taller_num}:"):
            return col
    return None

taller_columna_real = None  # Variable global para usar en las siguientes secciones

if selected_taller != "📊 Ver todo (todos los talleres)":
    taller_num = selected_taller.split(":")[0].split()[-1]
    taller_columna_real = find_taller_column(df, taller_num)

    if taller_columna_real is None:
        st.error(f"No se encontró la columna del {selected_taller}.")
        st.write("Columnas detectadas:")
        st.write([c for c in df.columns if c.lower().startswith("taller")])
        st.stop()

    df[taller_columna_real] = df[taller_columna_real].astype(str).str.strip()
    mask = df[taller_columna_real].str.contains("Participaré|Asistiré", case=False, na=False)
    df_filtered = df[mask]
else:
    df_filtered = df.copy()

st.markdown(f"Mostrando resultados para: **{selected_taller}**")
if taller_columna_real:
    st.caption(f"Columna real detectada: `{taller_columna_real}`")

# ===========================================
# PARTICIPACIÓN POR RESPUESTA (para taller seleccionado)
# ===========================================
st.subheader("Participación declarada en el taller")

if selected_taller != "📊 Ver todo (todos los talleres)":
    if taller_columna_real is None or taller_columna_real not in df.columns:
        st.error("No se pudo identificar la columna del taller en la base de datos.")
        st.stop()

    df[taller_columna_real] = df[taller_columna_real].astype(str).str.strip()

    # --- Contar respuestas ---
    opciones = ["Participaré", "Asistiré con infancias", "No participaré", "No estoy seguro/a todavía"]
    conteo = df[taller_columna_real].value_counts().reindex(opciones, fill_value=0).reset_index()
    conteo.columns = ["Respuesta", "Frecuencia"]
    total = conteo["Frecuencia"].sum()
    conteo["Porcentaje"] = (conteo["Frecuencia"] / total * 100).round(1) if total > 0 else 0

    # --- Calcular totales ---
    asistentes_sin_inf = int(conteo.loc[conteo["Respuesta"] == "Participaré", "Frecuencia"])
    asistentes_con_inf = int(conteo.loc[conteo["Respuesta"] == "Asistiré con infancias", "Frecuencia"])
    asistentes_totales = asistentes_sin_inf + asistentes_con_inf
    no_participa = int(conteo.loc[conteo["Respuesta"] == "No participaré", "Frecuencia"])
    no_seguro = int(conteo.loc[conteo["Respuesta"] == "No estoy seguro/a todavía", "Frecuencia"])

    # --- Métricas principales ---
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Asistentes", asistentes_totales)
    col2.metric("Asiste sin infancias", asistentes_sin_inf)
    col3.metric("Asiste con infancias", asistentes_con_inf)
    col4.metric("No participará", no_participa)
    col5.metric("No está seguro/a", no_seguro)

    # --- Gráfico de barras ---
    fig_part = px.bar(
        conteo,
        x="Respuesta",
        y="Frecuencia",
        text=conteo.apply(lambda x: f"{x['Frecuencia']} personas ({x['Porcentaje']}%)", axis=1),
        title=f"Distribución de respuestas – {selected_taller}",
        color="Respuesta",
        color_discrete_map={
            "Participaré": "#4CAF50",
            "Asistiré con infancias": "#81C784",
            "No participaré": "#B0B0B0",
            "No estoy seguro/a todavía": "#FFB74D"
        },
        labels={"Respuesta": "Tipo de respuesta", "Frecuencia": "Cantidad de personas"}
    )
    fig_part.update_traces(textposition="outside")
    fig_part.update_layout(yaxis=dict(range=[0, max(conteo["Frecuencia"]) * 1.3 if total > 0 else 1]))
    st.plotly_chart(fig_part, use_container_width=True)

    # --- Mostrar lista de indecisos ---
    df_indecisos = df[df[taller_columna_real].str.contains("No estoy seguro", case=False, na=False)][
        ["Nombre completo", "Teléfono", "Dirección de correo electrónico", "Territorio donde vives:"]
    ]
    if not df_indecisos.empty:
        st.markdown("#### Personas que aún no confirman su participación")
        st.dataframe(
            df_indecisos.rename(columns={
                "Nombre completo": "Participante",
                "Teléfono": "Contacto",
                "Dirección de correo electrónico": "Correo",
                "Territorio donde vives:": "Territorio"
            }),
            use_container_width=True
        )
    else:
        st.info("No hay personas que hayan respondido 'No estoy seguro/a todavía' en este taller.")

else:
    st.info("Selecciona un taller específico para analizar la participación declarada.")











# ===========================================
# PARTICIPACIÓN DE INFANCIAS
# ===========================================
st.subheader("Participación de infancias")

# Calcular quién viene con infancias
df_filtered["Viene con infancias"] = df_filtered[COL_CUIDADORA].str.contains("Sí", case=False, na=False)

total_personas = len(df_filtered)
con_infancias = df_filtered["Viene con infancias"].sum()
sin_infancias = total_personas - con_infancias

porcentaje_si = round((con_infancias / total_personas) * 100, 1) if total_personas > 0 else 0
porcentaje_no = 100 - porcentaje_si if total_personas > 0 else 0

# --- Métricas ---
col1, col2, col3 = st.columns(3)
col1.metric("Personas con infancias", f"{con_infancias}", f"{porcentaje_si}%")
col2.metric("Personas sin infancias", f"{sin_infancias}", f"{porcentaje_no}%")
col3.metric("Total de participantes", f"{total_personas}")

# --- Preparar datos para gráfico ---
conteo = pd.DataFrame({
    "Categoría": ["Con infancias (Sí)", "Sin infancias (No)"],
    "Frecuencia": [con_infancias, sin_infancias],
    "Porcentaje": [porcentaje_si, porcentaje_no]
})

# --- Gráfico de barras ---
fig_inf = px.bar(
    conteo,
    x="Categoría",
    y="Frecuencia",
    text=conteo.apply(lambda x: f"{x['Frecuencia']} personas ({x['Porcentaje']}%)", axis=1),
    title="Distribución de participantes según presencia de infancias",
    color="Categoría",
    color_discrete_map={
        "Con infancias (Sí)": "#57C785",
        "Sin infancias (No)": "#B0B0B0"
    },
    labels={"Categoría": "Tipo de participación", "Frecuencia": "Número de personas"}
)
fig_inf.update_traces(textposition="outside")
fig_inf.update_layout(yaxis=dict(range=[0, max(con_infancias, sin_infancias) * 1.3]))
st.plotly_chart(fig_inf, use_container_width=True)

# --- Detalle de infancias registradas ---
st.markdown("#### Detalle de infancias registradas")
if con_infancias > 0:
    df_inf = df_filtered[df_filtered["Viene con infancias"]][["Nombre completo", COL_INFANCIAS]]
    st.dataframe(df_inf.rename(columns={
        "Nombre completo": "Participante",
        COL_INFANCIAS: "Infancias registradas"
    }), use_container_width=True)
else:
    st.info("Ninguna persona registrada viene acompañada de infancias.")


# ===========================================
# CONOCIMIENTO (solo taller seleccionado)
# ===========================================
st.subheader("Nivel de conocimiento del grupo seleccionado (escala 1–5)")

taller_vars = {
    "Taller 4: Carpintería (Punto Limpio con enfoque de género)": "¿Qué tan familiarizado/a estás con la carpintería y las herramientas que se usan para construir con madera?",
    "Taller 2: Reproducción de especies vegetales": "¿Tienes experiencia o conocimientos en la multiplicación de plantas y la propagación de especies vegetales?",
    "Taller 3: Guardado de semillas": "¿Qué tan familiarizado/a estás con las prácticas de cosecha, selección y conservación de semillas?",
    "Taller 1: Compostaje y Lombricultura": "¿Qué tanta experiencia tienes en el compostaje y la crianza de lombrices para gestionar tus residuos orgánicos?",
    "Taller 5: Construcción de invernadero": "¿Qué tanto sabes sobre los invernaderos y su uso para favorecer el cultivo?",
    "Taller 6: Cosecha de aguas lluvias": "¿Qué tan familiarizado/a estás con las formas de recolectar y guardar agua de lluvia?",
    "Reciclaje y gestión de residuos": "¿Cuál es tu nivel de conocimiento y práctica sobre cómo reciclar y gestionar residuos en tu hogar y comunidad?"
}

# Verificar que el taller seleccionado tenga variable asociada
if selected_taller in taller_vars:
    colname = taller_vars[selected_taller]
    
    # Convertir a numérico y eliminar nulos
    if colname in df.columns:
        df_filtered[colname] = pd.to_numeric(df_filtered[colname], errors="coerce")
        data_valid = df_filtered.dropna(subset=[colname])

        if len(data_valid) > 0:
            promedio = data_valid[colname].mean().round(2)
            participantes = len(data_valid)

            # ---- Métricas principales ----
            st.markdown(f"### {selected_taller}")
            c1, c2 = st.columns(2)
            c1.metric("Promedio de conocimiento", f"{promedio}/5")
            c2.metric("N° de participantes con respuesta", participantes)

            # ---- Distribución ----
            dist = data_valid[colname].value_counts().sort_index().reset_index()
            dist.columns = ["Nivel", "Personas"]

            fig = px.bar(
                dist, x="Nivel", y="Personas",
                text="Personas",
                color="Nivel",
                color_continuous_scale="YlGn",
                title=f"Distribución de niveles de conocimiento – {selected_taller}",
                labels={"Nivel": "Nivel (1–5)", "Personas": "Cantidad"}
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

            # ---- Participantes destacados ----
            st.markdown("#### 👥 Participantes destacados")
            df_max = data_valid[data_valid[colname] >= 4][["Nombre completo", "Género", "Territorio donde vives:", colname]]
            df_min = data_valid[data_valid[colname] <= 2][["Nombre completo", "Género", "Territorio donde vives:", colname]]

            colA, colB = st.columns(2)
            with colA:
                st.markdown("**🌱 Mayor conocimiento (niveles 4–5)**")
                if not df_max.empty:
                    st.dataframe(df_max.rename(columns={"Nombre completo": "Participante", colname: "Nivel"}), use_container_width=True)
                else:
                    st.caption("Sin registros de niveles altos.")
            with colB:
                st.markdown("**🌾 Menor conocimiento (niveles 1–2)**")
                if not df_min.empty:
                    st.dataframe(df_min.rename(columns={"Nombre completo": "Participante", colname: "Nivel"}), use_container_width=True)
                else:
                    st.caption("Sin registros de niveles bajos.")
        else:
            st.info("No hay respuestas válidas para este taller.")
    else:
        st.warning("No se encontró la columna asociada a este taller en la base de datos.")
else:
    st.info("Este taller no tiene preguntas asociadas de conocimiento.")

# ===========================================
# MOTIVACIONES
# ===========================================
st.subheader("Motivaciones y comentarios")

for _, row in df_filtered.iterrows():
    nombre = row["Nombre completo"]
    comentario = row[COL_MOTIVOS]
    if pd.notna(comentario) and len(str(comentario).strip()) > 1:
        st.markdown(f"**{nombre}:** {comentario}")

