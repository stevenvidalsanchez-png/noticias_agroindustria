import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta

# --- 0. FUNCIONES DE SIMULACIÓN DE DATOS (REEMPLAZAR CON CARGA REAL) ---

def generar_datos_simulados(num_noticias=400):
    """Genera un DataFrame simulado para el dashboard si no hay datos cargados."""
    
    # Simulación de fechas a lo largo del último año
    start_date = datetime.now() - timedelta(days=365)
    
    data = []
    sentimientos = ['Positivo', 'Negativo', 'Neutro']
    
    for i in range(1, num_noticias + 1):
        sentimiento = random.choice(sentimientos)
        fecha = start_date + timedelta(days=random.randint(1, 365))
        
        # Simular variaciones en el conteo para la tendencia
        if sentimiento == 'Positivo':
            valor = random.randint(10, 50) + (10 if fecha.month % 3 == 0 else 0)
        elif sentimiento == 'Negativo':
            valor = random.randint(10, 50) + (15 if fecha.month % 4 == 0 else 0)
        else:
            valor = random.randint(5, 30)

        data.append({
            'ID': i,
            'Sentimiento': sentimiento,
            'Fecha': fecha.strftime('%Y-%m-%d'),
            'Conteo_Diario': valor # Variable proxy para tendencia
        })
        
    df = pd.DataFrame(data)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    return df

# Cargar los datos simulados (REEMPLAZAR por la carga de su CSV real)
# df = pd.read_csv('Agroindustria_400_Noticias_Sinteticas.csv', sep=';')
# df['Fecha Publicación'] = pd.to_datetime(df['Fecha Publicación'], format='%d/%m/%y')
# df.rename(columns={'Fecha Publicación': 'Fecha'}, inplace=True)

df = generar_datos_simulados(num_noticias=400) # Usar datos simulados por defecto

# Preparar datos agregados para los gráficos de tendencia
df_agrupado = df.groupby(['Fecha', 'Sentimiento']).size().reset_index(name='Total')

# --- 1. CONFIGURACIÓN INICIAL DE STREAMLIT ---

st.set_page_config(
    page_title="Tablero de Sentimiento Agroindustrial",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌱 Tablero de Sentimiento Noticioso Agroindustrial")
st.markdown("---")

# --- 2. SECCIÓN 1: GRÁFICO DE TORTA (Distribución General) ---

st.header("1. Distribución General de Sentimientos")

# Contar la distribución
df_conteo = df['Sentimiento'].value_counts().reset_index()
df_conteo.columns = ['Sentimiento', 'Conteo']

# Mapeo de colores personalizado
color_map = {'Positivo': '#28a745', 'Negativo': '#dc3545', 'Neutro': '#6c757d'}

fig_torta = px.pie(
    df_conteo, 
    values='Conteo', 
    names='Sentimiento', 
    title='Proporción de Noticias Clasificadas',
    color='Sentimiento',
    color_discrete_map=color_map,
    hole=.3 # Para convertirlo en un gráfico de dona
)
fig_torta.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))

st.plotly_chart(fig_torta, use_container_width=True)

st.markdown("---")

# --- 3. SECCIÓN 2: GRÁFICO DE BARRAS (Conteo Mensual Total) ---

st.header("2. Conteo de Noticias por Sentimiento y Mes")

# Agregar por mes
df_mensual = df.copy()
df_mensual['Mes'] = df_mensual['Fecha'].dt.to_period('M').astype(str)

df_barras = df_mensual.groupby(['Mes', 'Sentimiento']).size().reset_index(name='Total')

fig_barras = px.bar(
    df_barras, 
    x='Mes', 
    y='Total', 
    color='Sentimiento',
    title='Volumen Mensual de Noticias por Categoría',
    color_discrete_map=color_map,
    labels={'Total': 'Número de Noticias', 'Mes': 'Mes de Publicación'}
)
fig_barras.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_barras, use_container_width=True)

st.markdown("---")

# --- 4. SECCIONES 3, 4 y 5: LÍNEAS DE TENDENCIA (Por Sentimiento) ---

st.header("3. Tendencia Histórica de Sentimientos (Últimos 12 Meses)")

# Filtrar para cada sentimiento
df_positivo = df_agrupado[df_agrupado['Sentimiento'] == 'Positivo']
df_negativo = df_agrupado[df_agrupado['Sentimiento'] == 'Negativo']
df_neutro = df_agrupado[df_agrupado['Sentimiento'] == 'Neutro']

# Crear columnas para los 3 gráficos de línea
col_pos, col_neg, col_neu = st.columns(3)

# 4.1. Sección 3: Línea Verde Positivo
with col_pos:
    st.subheader("🟢 Noticias Positivas")
    fig_pos = px.line(
        df_positivo,
        x='Fecha',
        y='Total',
        title='Tendencia Positiva',
        color_discrete_sequence=['#28a745'], # Verde
        labels={'Total': 'Conteo Diario', 'Fecha': 'Fecha'}
    )
    fig_pos.update_traces(mode='lines+markers')
    st.plotly_chart(fig_pos, use_container_width=True)

# 4.2. Sección 4: Línea Roja Negativo
with col_neg:
    st.subheader("🔴 Noticias Negativas")
    fig_neg = px.line(
        df_negativo,
        x='Fecha',
        y='Total',
        title='Tendencia Negativa',
        color_discrete_sequence=['#dc3545'], # Rojo
        labels={'Total': 'Conteo Diario', 'Fecha': 'Fecha'}
    )
    fig_neg.update_traces(mode='lines+markers')
    st.plotly_chart(fig_neg, use_container_width=True)

# 4.3. Sección 5: Línea Gris Neutro
with col_neu:
    st.subheader("⚪ Noticias Neutras")
    fig_neu = px.line(
        df_neutro,
        x='Fecha',
        y='Total',
        title='Tendencia Neutra',
        color_discrete_sequence=['#6c757d'], # Gris
        labels={'Total': 'Conteo Diario', 'Fecha': 'Fecha'}
    )
    fig_neu.update_traces(mode='lines+markers')
    st.plotly_chart(fig_neu, use_container_width=True)

# --- FIN DEL CÓDIGO ---

