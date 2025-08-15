import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
import traceback
import folium
from streamlit_folium import folium_static
from statsmodels import api as sm
from scipy import stats
import calendar

# Configuración de la página
def setup_page():
    st.set_page_config(
        page_title="ANÁLISIS DE PRECIPITACIONES MENSUALES - ANA",
        page_icon="🌧️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# --- ESTILOS CSS PERSONALIZADOS ---
def apply_custom_styles():
    st.markdown("""
        <style>
        :root {
            --primary-color: #1a5bb7;
            --secondary-color: #3d8ee0;
            --accent-color: #ff8c00;
            --bg-color: #f0f5ff;
            --card-color: #ffffff;
        }

        /* Animación de degradado en el fondo */
        .stApp {
            background: linear-gradient(135deg, #1a5bb7, #3d8ee0, #42c0ff);
            background-size: 400% 400%;
            animation: gradientMove 15s ease infinite;
            color: #ffffff;
        }
        @keyframes gradientMove {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        /* Encabezado elegante */
        .header-container {
            background: rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(8px);
            padding: 1.8rem;
            border-radius: 0 0 15px 15px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(0,0,0,0.25);
            color: white;
            text-align: center;
            animation: fadeIn 1s ease-in-out;
        }
        .header-title {
            font-size: 2.6rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            letter-spacing: 1px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.4);
        }
        .header-subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 1.2rem;
            font-weight: 300;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(-15px);}
            to {opacity: 1; transform: translateY(0);}
        }

        /* Tarjetas con hover */
        .station-info, .metric-card, .plot-container {
            background-color: var(--card-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .station-info:hover, .metric-card:hover, .plot-container:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        .station-info {
            border-left: 5px solid var(--accent-color);
        }

        /* Títulos */
        .station-info h3 {
            color: var(--primary-color);
            margin-top: 0;
            border-bottom: 1px solid #eee;
            padding-bottom: 0.5rem;
        }
        .metric-title {
            font-size: 0.95rem;
            color: var(--secondary-color);
        }
        .metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        /* Grid adaptable */
        .station-info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
        }
        .info-label {
            font-weight: 600;
            color: var(--secondary-color);
        }
        .info-value {
            color: #444;
        }

        /* Botones modernos */
        .stButton>button {
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 6px;
            font-weight: 600;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, var(--secondary-color), var(--primary-color));
            transform: scale(1.05);
            box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        }

        /* Inputs con estilo */
        .stSelectbox, .stTextInput, .stNumberInput, .stDateInput, textarea {
            background-color: rgba(255,255,255,0.15) !important;
            color: white !important;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.3);
        }

        /* Mapas */
        .map-container {
            margin-top: 1.5rem;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            height: 500px;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header-title { font-size: 1.8rem; }
            .station-info-grid { grid-template-columns: 1fr; }
            .map-container { height: 350px; }
        }
        /* Estilos para los cuadros de interpretación */
        .interpretation-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 4px solid var(--primary-color);
            transition: all 0.3s ease;
        }
        .interpretation-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        .interpretation-title {
            color: var(--primary-color);
            font-size: 1.1rem;
            font-weight: 700;
            margin-top: 0;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
        }
        .interpretation-title svg {
            margin-right: 8px;
        }
        .interpretation-content {
            color: #444;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        .interpretation-list {
            padding-left: 1.2rem;
            margin: 0.5rem 0;
        }
        .interpretation-list li {
            margin-bottom: 0.4rem;
        }
        .key-point {
            font-weight: 600;
            color: var(--primary-color);
        }
        .divider-line {
            height: 1px;
            background: linear-gradient(90deg, var(--primary-color), transparent);
            margin: 1rem 0;
        }
        .highlight-box {
            background: rgba(26, 91, 183, 0.1);
            border-radius: 6px;
            padding: 0.8rem;
            margin: 0.8rem 0;
            border-left: 3px solid var(--primary-color);
        }
        </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE PROCESAMIENTO ---

def Extraer_Metadata(df):
    """Extrae metadatos del formato exacto del Excel"""
    metadata = {}
    field_mappings = {
        "Estación": "Estación",
        "Variable": "Variable",
        "Operador": "Operador",
        "WGS 84 Geográficas": "Coordenadas",
        "Tipo": "Tipo",
        "Ámbito Político": "Ámbito Político",
        "Ámbito Administrativo": "Ámbito Administrativo",
        "Unidad Hidrográfica": "Cuenca"
    }
    
    for i in range(15):
        col_a = str(df.iloc[i, 0]).strip() if pd.notna(df.iloc[i, 0]) else ""
        
        if col_a in field_mappings:
            metadata_key = field_mappings[col_a]
            metadata_value = str(df.iloc[i, 2]).strip() if len(df.columns) > 2 and pd.notna(df.iloc[i, 2]) else ""
            
            if col_a == "WGS 84 Geográficas":
                try:
                    parts = [p.strip() for p in metadata_value.split("/")]
                    lat = float(parts[0].split(":")[1].strip())
                    lon = float(parts[1].split(":")[1].strip())
                    alt = parts[2].split(":")[1].strip()
                    
                    metadata["Coordenadas"] = {
                        "Latitud": lat,
                        "Longitud": lon,
                        "Altitud": alt
                    }
                    continue
                except Exception as e:
                    st.warning(f"Error procesando coordenadas: {e}")
            
            elif col_a == "Ámbito Político":
                try:
                    parts = [p.strip() for p in metadata_value.split("/")]
                    ambito_data = {
                        "Departamento": parts[0].split(":")[1].strip(),
                        "Provincia": parts[1].split(":")[1].strip(),
                        "Distrito": parts[2].split(":")[1].strip()
                    }
                    metadata[metadata_key] = ambito_data
                    continue
                except:
                    metadata[metadata_key] = metadata_value
            
            else:
                metadata[metadata_key] = metadata_value
    
    return metadata

def Extracion_datos_mensuales(df):
    """Extrae y transforma los datos mensuales de precipitación"""
    inicio_id = None
    for i in range(len(df)):
        if str(df.iloc[i, 0]).strip() == 'Año':
            inicio_id = i
            break
    
    if inicio_id is None:
        return pd.DataFrame()

    meses = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Set', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    
    data = []
    for i in range(inicio_id + 1, len(df)):
        year = df.iloc[i, 0]
        
        try:
            year = int(year)
        except:
            continue
        
        for month_num in range(1, 13):
            col_idx = month_num
            if col_idx >= len(df.columns):
                break
                
            value = df.iloc[i, col_idx]
            
            if pd.isna(value) or value == '':
                continue
                
            try:
                value = float(value)
                data.append({
                    'Año': year,
                    'Mes': meses[month_num],
                    'Mes_num': month_num,
                    'Precipitación (mm)': value,
                    'Fecha': pd.to_datetime(f"{year}-{month_num}-01")
                })
            except:
                continue
    
    return pd.DataFrame(data)

def Calcular_estadisticas_Mensuales(data_df):
    """Calcula estadísticas mensuales agregadas"""
    if data_df.empty:
        return pd.DataFrame()
    
    monthly_stats = data_df.groupby('Mes_num').agg({
        'Precipitación (mm)': ['mean', 'median', 'std', 'min', 'max', 'count']
    }).reset_index()
    
    monthly_stats.columns = [
        'Mes_num', 'Promedio', 'Mediana', 'Desviación', 
        'Mínimo', 'Máximo', 'Datos Disponibles'
    ]
    
    month_map = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Set', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    monthly_stats['Mes'] = monthly_stats['Mes_num'].map(month_map)
    
    return monthly_stats

def Calcular_estadisticas_anuales(data_df):
    """Calcula estadísticas anuales agregadas"""
    if data_df.empty:
        return pd.DataFrame()
    
    annual_stats = data_df.groupby('Año').agg({
        'Precipitación (mm)': ['sum', 'mean', 'median', 'std', 'min', 'max', 'count']
    }).reset_index()
    
    annual_stats.columns = [
        'Año', 'Total Anual', 'Promedio Mensual', 'Mediana Mensual', 
        'Variabilidad', 'Mínimo Mensual', 'Máximo Mensual', 'Meses con Datos'
    ]
    
    return annual_stats

def Detectar_patrones_estacionales(data_df):
    """Detecta patrones estacionales en los datos"""
    if len(data_df) < 24:
        return None
    
    try:
        df_season = data_df.pivot_table(
            index='Año', 
            columns='Mes_num', 
            values='Precipitación (mm)', 
            aggfunc='mean'
        )
        
        df_normalized = df_season.apply(
            lambda x: (x - x.mean()) / x.std(), 
            axis=1
        )
        
        seasonality = {
            'meses_lluviosos': [],
            'meses_secos': [],
            'consistencia': None
        }
        
        avg_by_month = df_normalized.mean()
        threshold = 0.5
        
        for month in avg_by_month.index:
            if avg_by_month[month] > threshold:
                seasonality['meses_lluviosos'].append(month)
            elif avg_by_month[month] < -threshold:
                seasonality['meses_secos'].append(month)
        
        consistency = (df_normalized > 0).mean().mean()
        seasonality['consistencia'] = max(0, min(1, 2 * abs(consistency - 0.5)))
        
        return seasonality
    except:
        return None

# --- FUNCIONES DE GRÁFICOS ---
def Crear_figura(message):
    """Crea una figura vacía con un mensaje"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False
    )
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='grey'
    )
    return fig

def Grafica_distribucion_mensual(data_df, metadata):
    """Gráfico de distribución mensual"""
    if data_df.empty:
        return Crear_figura("No hay datos disponibles")
    
    try:
        df_agg = data_df.groupby(['Mes_num', 'Mes'])['Precipitación (mm)'].agg(
            ['mean', 'median', 'std', 'min', 'max']
        ).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            x=data_df['Mes'],
            y=data_df['Precipitación (mm)'],
            name='Distribución',
            boxpoints=False,
            marker_color='#4a7cb1',
            line_color='#1e3d6b',
            fillcolor='rgba(74, 124, 177, 0.3)'
        ))
        
        fig.add_trace(go.Scatter(
            x=df_agg['Mes'],
            y=df_agg['mean'],
            mode='lines+markers',
            name='Promedio',
            line=dict(color='#ff8c00', width=3),
            marker=dict(size=8),
            hovertemplate="<b>%{x}</b><br>Promedio: %{y:.1f} mm<extra></extra>"
        ))
        
        fig.add_trace(go.Scatter(
            x=df_agg['Mes'],
            y=df_agg['median'],
            mode='lines',
            name='Mediana',
            line=dict(color='#2ca02c', width=2, dash='dash'),
            hovertemplate="<b>%{x}</b><br>Mediana: %{y:.1f} mm<extra></extra>"
        ))
        
        fig.update_layout(
            title=dict(
                text=f'Distribución Mensual de Precipitación<br><sup>{metadata.get("Estación", "")}</sup>',
                x=0.5,
                xanchor='center',
                font=dict(size=18, color='#1e3d6b')
            ),
            xaxis_title='Mes',
            yaxis_title='Precipitación (mm)',
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='grey',
            font=dict(
                family="Arial",
                size=12,
                color="#333333"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(
                    color="#333333",
                    size=12
                )
            ),
            margin=dict(l=50, r=50, t=100, b=50)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error al generar gráfico de distribución: {str(e)}")
        return Crear_figura("Error al generar gráfico")

def Grafico_tendencia_anual(data_df, metadata):
    """Gráfico de tendencia anual"""
    if data_df.empty:
        return Crear_figura("No hay datos disponibles")
    
    try:
        annual_data = data_df.groupby('Año')['Precipitación (mm)'].sum().reset_index()
        
        x = annual_data['Año']
        y = annual_data['Precipitación (mm)']
        
        mask = ~y.isna()
        x = x[mask]
        y = y[mask]
        
        if len(x) < 2:
            return Crear_figura("Datos insuficientes para análisis de tendencia")
        
        coeffs = np.polyfit(x, y, 1)
        trend_line = np.poly1d(coeffs)(x)
        
        lowess = sm.nonparametric.lowess(y, x, frac=0.3) if len(x) > 5 else None
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        y_err = std_err * np.sqrt(1/len(x) + (x - np.mean(x))**2 / np.sum((x - np.mean(x))**2))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=np.concatenate([x, x[::-1]]),
            y=np.concatenate([trend_line + 1.96*y_err, (trend_line - 1.96*y_err)[::-1]]),
            fill='toself',
            fillcolor='rgba(30, 61, 107, 0.2)',
            line_color='rgba(255,255,255,0)',
            name='Intervalo 95% confianza'
        ))
        
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='markers',
            marker=dict(size=10, color='#4a7cb1', line=dict(width=1, color='#1e3d6b')),
            name='Precipitación anual',
            hovertemplate="<b>Año %{x}</b><br>Precipitación: %{y:.1f} mm<extra></extra>"
        ))
        
        fig.add_trace(go.Scatter(
            x=x,
            y=trend_line,
            mode='lines',
            line=dict(color='#ff8c00', width=3, dash='dash'),
            name=f'Tendencia (R²={r_value**2:.2f})',
            hovertemplate="<b>Año %{x}</b><br>Tendencia: %{y:.1f} mm<extra></extra>"
        ))
        
        if lowess is not None:
            fig.add_trace(go.Scatter(
                x=lowess[:, 0],
                y=lowess[:, 1],
                mode='lines',
                line=dict(color='#1e3d6b', width=3),
                name='Tendencia suavizada',
                hovertemplate="<b>Año %{x:.0f}</b><br>Tendencia suavizada: %{y:.1f} mm<extra></extra>"
            ))
        
        fig.update_layout(
            title=dict(
                text=f'Tendencia Anual de Precipitación<br><sup>{metadata.get("Estación", "")}</sup>',
                x=0.5,
                xanchor='center',
                font=dict(size=18, color='#1e3d6b')
            ),
            xaxis_title='Año',
            yaxis_title='Precipitación total anual (mm)',
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='grey',
            font=dict(
                family="Arial",
                size=12,
                color="#333333"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(
                    color="#333333",
                    size=12
                )
            ),
            margin=dict(l=50, r=50, t=100, b=50)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error al generar gráfico de tendencia: {str(e)}")
        return Crear_figura("Error al generar gráfico")

def Mapa_calor_mensual(data_df, metadata):
    """Heatmap de precipitación mensual por año"""
    if data_df.empty:
        return None
    
    try:
        # Crear pivot table solo con los meses disponibles
        pivot_df = data_df.pivot_table(
            index='Año',
            columns='Mes_num',
            values='Precipitación (mm)',
            aggfunc='mean'
        )
        
        # Verificar si hay datos
        if pivot_df.empty:
            return None
        
        # Mapeo de números de mes a nombres abreviados
        month_map = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
            9: 'Set', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }
        
        # Renombrar solo las columnas existentes
        available_months = pivot_df.columns.tolist()
        new_columns = [month_map.get(month, month) for month in available_months]
        pivot_df.columns = new_columns
        
        # Ordenar por mes numérico (ya no es necesario ordenar alfabéticamente)
        pivot_df = pivot_df[sorted(pivot_df.columns, key=lambda x: list(month_map.values()).index(x))]
        
        fig = px.imshow(
            pivot_df,
            labels=dict(x="Mes", y="Año", color="Precipitación (mm)"),
            color_continuous_scale='RdYlGn_r',
            aspect='auto'
        )
        
        fig.update_layout(
            title=f'Patrón Mensual por Año - {metadata.get("Estación", "")}',
            xaxis_title='Mes',
            yaxis_title='Año',
            plot_bgcolor='white',
            paper_bgcolor='grey'
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error al generar el heatmap: {str(e)}")
        return None



def Grafica_dispercion_anual(data_df, metadata):
    """Gráfico de dispersión de precipitación por año"""
    if data_df.empty:
        return Crear_figura("No hay datos disponibles")
    
    try:
        annual_data = data_df.groupby('Año')['Precipitación (mm)'].sum().reset_index()
        
        fig = px.scatter(
            annual_data,
            x='Año',
            y='Precipitación (mm)',
            trendline="lowess",
            trendline_color_override="#FF7F0E",
            labels={'Precipitación (mm)': 'Precipitación Total Anual (mm)'},
            color_discrete_sequence=["#2ff310"]
        )
        
        fig.update_traces(
            hovertemplate="<b>Año:</b> %{x}<br><b>Precipitación:</b> %{y:.1f} mm<extra></extra>",
            marker=dict(size=10, opacity=0.8, line=dict(width=1, color='#1e3d6b'))
        )
        
        fig.update_layout(
            title=dict(
                text=f'Dispersión de Precipitación Anual<br><sup>{metadata.get("Estación", "")}</sup>',
                x=0.5,
                xanchor='center',
                font=dict(size=18, color='#1e3d6b')
            ),
            xaxis_title='Año',
            yaxis_title='Precipitación Total Anual (mm)',
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='grey',
            font=dict(
                family="Arial",
                size=12,
                color="#333333"
            ),
            showlegend=False,
            margin=dict(l=50, r=50, t=100, b=50)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error al generar gráfico de dispersión anual: {str(e)}")
        return Crear_figura("Error al generar gráfico")

def Grafica_dispercion_mensual(data_df, metadata):
    """Gráfico de dispersión de precipitación por mes"""
    if data_df.empty:
        return Crear_figura("No hay datos disponibles")
    
    try:
        month_order = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                      'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic']
        
        fig = px.scatter(
            data_df,
            x='Mes',
            y='Precipitación (mm)',
            color='Mes',
            category_orders={"Mes": month_order},
            labels={'Precipitación (mm)': 'Precipitación Mensual (mm)'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_traces(
            hovertemplate="<b>Año:</b> %{customdata}<br><b>Mes:</b> %{x}<br><b>Precipitación:</b> %{y:.1f} mm<extra></extra>",
            customdata=data_df['Año'],
            marker=dict(size=8, opacity=0.9, line=dict(width=1, color='#1e3d6b'))
        )
        
        fig.update_layout(
            title=dict(
                text=f'Dispersión de Precipitación por Mes',
                x=0.5,
                xanchor='center',
                font=dict(size=18, color='#1e3d6b')
            ),
            xaxis_title='Mes',
            yaxis_title='Precipitación Mensual (mm)',
            hovermode='closest',
            plot_bgcolor='white',
            paper_bgcolor='grey',
            font=dict(
                family="Arial",
                size=12,
                color="#333333"
            ),
            xaxis={'categoryorder': 'array', 'categoryarray': month_order},
            legend=dict(
                title_text='Mes',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(
                    color="#333333",
                    size=10
                )
            ),
            margin=dict(l=50, r=50, t=100, b=50)
        )
        
        
        return fig
    
    except Exception as e:
        st.error(f"Error al generar gráfico de dispersión mensual: {str(e)}")
        return Crear_figura("Error al generar gráfico")

def Grafico_precipitacion_anual(data_df, metadata):
    """Gráfico de precipitación acumulada anual"""
    if data_df.empty:
        return Crear_figura("No hay datos disponibles")
    
    try:
        annual_cum = data_df.groupby('Año')['Precipitación (mm)'].sum().reset_index()
        
        annual_cum = annual_cum.sort_values('Año')
        annual_cum['Acumulado'] = annual_cum['Precipitación (mm)'].cumsum()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=annual_cum['Año'],
            y=annual_cum['Precipitación (mm)'],
            name='Precipitación anual',
            marker_color='#4a7cb1',
            opacity=0.7,
            hovertemplate="<b>Año %{x}</b><br>Precipitación: %{y:.1f} mm<extra></extra>"
        ))
        
        fig.add_trace(go.Scatter(
            x=annual_cum['Año'],
            y=annual_cum['Acumulado'],
            mode='lines+markers',
            name='Acumulado',
            line=dict(color="#4dff00", width=3),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate="<b>Año %{x}</b><br>Acumulado: %{y:.1f} mm<extra></extra>"
        ))
        
        fig.update_layout(
            title=dict(
                text=f'Precipitación Anual y Acumulada<br><sup>{metadata.get("Estación", "")}</sup>',
                x=0.5,
                xanchor='center',
                font=dict(size=18, color="#141466")
            ),
            xaxis_title='Año',
            yaxis_title='Precipitación Anual (mm)',
            yaxis2=dict(
                title='Precipitación Acumulada (mm)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='grey',
            font=dict(
                family="Arial",
                size=12,
                color="#333333"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(
                    color="#333333",
                    size=12
                )
            ),
            margin=dict(l=50, r=50, t=100, b=50)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error al generar gráfico de precipitación acumulada: {str(e)}")
        return Crear_figura("Error al generar gráfico")

def Grafico_violin_mensual(data_df, metadata):
    """Gráfico de violín para distribución mensual"""
    if data_df.empty:
        return Crear_figura("No hay datos disponibles")
    
    try:
        month_order = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                      'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic']
        
        fig = px.violin(
            data_df,
            x='Mes',
            y='Precipitación (mm)',
            color='Mes',
            category_orders={"Mes": month_order},
            box=True,
            points="all",
            hover_data=['Año'],
            labels={'Precipitación (mm)': 'Precipitación Mensual (mm)'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_layout(
            title=dict(
                text=f'Distribución de Precipitación por Mes<br><sup>{metadata.get("Estación", "")}</sup>',
                x=0.5,
                xanchor='center',
                font=dict(size=18, color='#1e3d6b')
            ),
            xaxis_title='Mes',
            yaxis_title='Precipitación Mensual (mm)',
            plot_bgcolor='white',
            paper_bgcolor='grey',
            font=dict(
                family="Arial",
                size=12,
                color="#333333"
            ),
            showlegend=False,
            margin=dict(l=50, r=50, t=100, b=50)
        )
        
        fig.update_traces(
            hovertemplate="<b>Mes:</b> %{x}<br><b>Precipitación:</b> %{y:.1f} mm<extra></extra>",
            hoveron="points+violins"
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error al generar gráfico de violín: {str(e)}")
        return Crear_figura("Error al generar gráfico")

def Grafica_anomalia_anual(data_df, metadata):
    """Gráfico de anomalías anuales"""
    if data_df.empty:
        return Crear_figura("No hay datos disponibles")
    
    try:
        annual_data = data_df.groupby('Año')['Precipitación (mm)'].sum().reset_index()
        avg_precip = annual_data['Precipitación (mm)'].mean()
        
        annual_data['Anomalía'] = annual_data['Precipitación (mm)'] - avg_precip
        annual_data['Color'] = np.where(annual_data['Anomalía'] >= 0, '#4a7cb1', '#ff8c00')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=annual_data['Año'],
            y=annual_data['Anomalía'],
            marker_color=annual_data['Color'],
            name='Anomalía',
            hovertemplate="<b>Año %{x}</b><br>Anomalía: %{y:.1f} mm<extra></extra>"
        ))
        
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="#1e3d6b",
            annotation_text=f"Promedio: {avg_precip:.1f} mm",
            annotation_position="bottom right"
        )
        
        fig.update_layout(
            title=dict(
                text=f'Anomalías de Precipitación Anual<br><sup>{metadata.get("Estación", "")}</sup>',
                x=0.5,
                xanchor='center',
                font=dict(size=18, color='#1e3d6b')
            ),
            xaxis_title='Año',
            yaxis_title='Anomalía (mm)',
            plot_bgcolor='white',
            paper_bgcolor='grey',
            font=dict(
                family="Arial",
                size=12,
                color="#333333"
            ),
            showlegend=False,
            margin=dict(l=50, r=50, t=100, b=50)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error al generar gráfico de anomalías: {str(e)}")
        return Crear_figura("Error al generar gráfico")

def Ubicacion(metadata):
    """Muestra el mapa con la ubicación exacta de la estación"""
    try:
        if "Coordenadas" not in metadata:
            st.warning("No se encontraron coordenadas en los metadatos")
            return
        
        coords = metadata["Coordenadas"]
        lat = coords["Latitud"]
        lon = coords["Longitud"]
        alt = coords["Altitud"]
        station_name = metadata.get("Estación", "Estación Desconocida")
        
        st.subheader(f"Ubicación de la Estación {station_name}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Latitud", f"{lat:.6f}°")
        with col2:
            st.metric("Longitud", f"{lon:.6f}°")
        with col3:
            st.metric("Altitud", f"{alt} msnm")
        
        m = folium.Map(
            location=[lat, lon],
            zoom_start=12,
            tiles="OpenStreetMap",
            width="100%"
        )
        
        folium.Marker(
            [lat, lon],
            popup=f"""
            <div style="font-family: Arial; font-size: 14px;">
                <h4 style="margin-bottom: 5px;">{station_name}</h4>
                <b>Tipo:</b> {metadata.get('Tipo', '')}<br>
                <b>Altitud:</b> {alt} msnm<br>
                <b>Operador:</b> {metadata.get('Operador', '')}
            </div>
            """,
            tooltip="Ver detalles",
            icon=folium.Icon(color='blue', icon='tint', prefix='fa')
        ).add_to(m)
        
        folium_static(m, width=800, height=500)
        
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 15px;">
                <a href="https://www.google.com/maps?q={lat},{lon}&z=15" target="_blank" 
                   style="color: white; background-color: #1e3d6b; padding: 8px 15px; 
                          border-radius: 4px; text-decoration: none; font-weight: bold;">
                    📍 Abrir en Google Maps
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    except Exception as e:
        st.error(f"Error al generar el mapa: {str(e)}")

def MostrarMetada(metadata):
    """Muestra los metadatos de la estación en la barra lateral"""
    st.markdown(f"""
        <div class="station-info">
            <h3>{metadata.get('Estación', 'Estación Desconocida')}</h3>
            <div class="station-info-grid">
                <div class="info-item">
                    <div class="info-label">Ubicación</div>
                    <div class="info-value">
                        {metadata.get('Ámbito Político', {}).get('Departamento', '')} / 
                        {metadata.get('Ámbito Político', {}).get('Provincia', '')} / 
                        {metadata.get('Ámbito Político', {}).get('Distrito', '')}
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-label">Coordenadas</div>
                    <div class="info-value">
                        Lat: {metadata.get('Coordenadas', {}).get('Latitud', '--')}<br>
                        Lon: {metadata.get('Coordenadas', {}).get('Longitud', '--')}<br>
                        Alt: {metadata.get('Coordenadas', {}).get('Altitud', '--')}
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-label">Variable</div>
                    <div class="info-value">{metadata.get('Variable', '')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Cuenca</div>
                    <div class="info-value">{metadata.get('Cuenca', '')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Operador</div>
                    <div class="info-value">{metadata.get('Operador', '')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Período de Datos</div>
                    <div class="info-value">{metadata.get('Periodo', 'Desconocido')}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def Mostrar_resumen_barra_lateral(filtered_df):
    """Muestra estadísticas resumen en la barra lateral"""
    st.markdown("### Resumen Estadístico")
    
    if not filtered_df.empty:
        total_years = filtered_df['Año'].nunique()
        avg_precip = filtered_df['Precipitación (mm)'].mean()
        max_precip = filtered_df['Precipitación (mm)'].max()
        min_precip = filtered_df['Precipitación (mm)'].min()
        total_precip = filtered_df['Precipitación (mm)'].sum()
        data_coverage = len(filtered_df) / (total_years * 12)
        
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Años de Datos</div>
                <div class="metric-value">{total_years}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Cobertura de Datos</div>
                <div class="metric-value">{data_coverage:.0%}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Precipitación Promedio</div>
                <div class="metric-value">{avg_precip:.1f} mm</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Máxima Registrada</div>
                <div class="metric-value">{max_precip:.1f} mm</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Mínima Registrada</div>
                <div class="metric-value">{min_precip:.1f} mm</div>
            </div>
        """, unsafe_allow_html=True)

def mostrar_mensaje_bienvenida():
    # CSS para dar estilo
    st.markdown("""
    <style>
        .instructions {
            background: linear-gradient(135deg, #1b5e20, #4caf50);
            color: white;
            padding: 20px;
            border-radius: 12px;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
            animation: fadeIn 1s ease-in-out;
        }
        .instructions strong {
            font-size: 1.2em;
            display: block;
            margin-bottom: 10px;
        }
        .instructions ol {
            padding-left: 20px;
        }
        .instructions li {
            margin-bottom: 8px;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
    </style>
    """, unsafe_allow_html=True)

    # HTML para mostrar el contenido
    st.markdown("""
    <div class="instructions">
        <strong>📋 Instrucciones:</strong>
        <ol>
            <li>📂 Sube un archivo <strong>Excel</strong> con datos de precipitación mensual</li>
            <li>🔍 La aplicación extraerá automáticamente los <em>metadatos</em> y la información</li>
            <li>📈 Explora los datos con visualizaciones interactivas</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Función para mostrar cuadros de interpretación
def show_interpretation(title, content, icon="ℹ️"):
    st.markdown(f"""
        <div class="interpretation-card">
            <div class="interpretation-title">
                {icon} {title}
            </div>
            <div class="interpretation-content">
                {content}
            </div>
        </div>
    """, unsafe_allow_html=True)
def setup_interpretation_styles():
    st.markdown("""
    <style>
        /* Contenedor principal - ¡Ahora con !important para prioridad! */
        div.interpret-card {
            background: white !important;
            border-radius: 10px !important;
            padding: 15px !important;
            margin: 15px 0 !important;
            border-left: 4px solid #1a5bb7 !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
            font-family: Arial, sans-serif !important;
        }
        
        /* Selectores más específicos */
        div.interpret-card div.interpret-title {
            color: #1a5bb7 !important;
            font-weight: bold !important;
            margin-bottom: 10px !important;
            font-size: 18px !important;
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
        }
        
        div.interpret-card div.interpret-content {
            color: #333333 !important;
            font-size: 15px !important;
            line-height: 1.5 !important;
        }
        
        div.interpret-card div.interpret-content ul {
            padding-left: 20px !important;
            margin: 10px 0 !important;
        }
        
        div.interpret-card div.interpret-content li {
            margin-bottom: 8px !important;
            position: relative !important;
        }
        
        div.interpret-card div.interpret-content li::before {
            content: "•" !important;
            color: #1a5bb7 !important;
            position: absolute !important;
            left: -15px !important;
        }
        
        div.interpret-card .key-term {
            font-weight: bold !important;
            color: #1a5bb7 !important;
            background-color: rgba(26, 91, 183, 0.1) !important;
            padding: 2px 5px !important;
            border-radius: 3px !important;
        }
        
        div.interpret-card .divider {
            height: 1px !important;
            background: #e0e0e0 !important;
            margin: 12px 0 !important;
            border: none !important;
        }
        
        div.interpret-card .highlight-tip {
            background: #f0f7ff !important;
            padding: 10px !important;
            border-radius: 5px !important;
            margin: 10px 0 !important;
            border-left: 3px solid #1a5bb7 !important;
        }
    </style>
    """, unsafe_allow_html=True)
def show_interpretation(title, content, icon="📊"):
    # Primero inyectamos los estilos (por si acaso)
    setup_interpretation_styles()
    
    # Usamos markdown con HTML directamente
    st.markdown(f"""
    <div class="interpret-card">
        <div class="interpret-title">{icon} {title}</div>
        <div class="interpret-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)
# --- FUNCIÓN PRINCIPAL ---
def main():
    # Configurar página y estilos
    setup_page()
    apply_custom_styles()
    setup_interpretation_styles()
    # Mostrar encabezado
    st.markdown("""
    <style>
        /* Fondo fijo con degradado azul-verde */
        .stApp {
            background: linear-gradient(135deg, #004e92, #00bfa5);
            font-family: 'Segoe UI', Tahoma, sans-serif;
            color: #002b36; /* Texto oscuro para contraste */
        }

        /* Sidebar con fondo semitransparente */
        section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(6px);
            color: #002b36;
        }

        /* Inputs */
        .stSelectbox, .stTextInput, .stNumberInput, .stDateInput, textarea {
            background-color: rgba(255, 255, 255, 0.85) !important;
            color: #002b36 !important;
            border-radius: 10px;
            border: 1px solid rgba(0, 0, 0, 0.15);
        }

        /* Botones */
        .stButton>button {
            background: linear-gradient(90deg, #00bfa5, #1de9b6);
            color: #002b36;
            font-weight: bold;
            border: none;
            border-radius: 12px;
            padding: 10px 18px;
            transition: all 0.2s ease;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.25);
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #1de9b6, #00bfa5);
            color: white;
        }

        /* Encabezado */
        .header-container {
            text-align: center;
            padding: 35px 15px;
            background: rgba(255, 255, 255, 0.85);
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        }

        /* Título */
        .header-title {
            font-size: 2.6em;
            font-weight: bold;
            letter-spacing: 1px;
            margin-bottom: 8px;
            color: #002b36;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.6);
        }

        /* Subtítulo */
        .header-subtitle {
            font-size: 1.2em;
            font-weight: 300;
            margin-top: 5px;
            color: #084c61;
        }

        /* Línea decorativa */
        .divider {
            height: 4px;
            width: 80px;
            background: #00bfa5;
            margin: 15px auto;
            border-radius: 2px;
        }

        /* Iconos */
        .icons-row {
            font-size: 1.8em;
            margin-top: 10px;
        }
         /* Hover de pestañas */
    [data-testid="stTabs"] button:hover {
        background-color: #26a69a;
        color: white;
        transform: scale(1.05);
    }

    /* Pestaña activa */
    [data-testid="stTabs"] button[aria-selected="true"] {
        background-color: #004d40;
        color: white;
        font-weight: 700;
    }
    </style>

    <div class="header-container">
        <div class="header-title">🌧️📊 ANÁLISIS DE PRECIPITACIONES</div>
        <div class="divider"></div>
        <div class="header-subtitle">🚰 Autoridad Nacional del Agua - ANA | 🌍 Sistema de Análisis de Datos Hidrológicos</div>
        <div class="icons-row">💧 ☔ 🌦️ 🌊 📈</div>
    </div>
""", unsafe_allow_html=True)

    
    # Carga de archivo
    uploaded_file = st.file_uploader(
        "📤 CARGAR ARCHIVO EXCEL CON DATOS MENSUALES", 
        type=['xlsx'],
        help="Suba un archivo Excel con datos mensuales de precipitación en formato estándar ANA"
    )
    
    if uploaded_file is not None:
        try:
            # Procesamiento de datos
            df = pd.read_excel(uploaded_file, header=None)
            metadata = Extraer_Metadata(df)
            data_df = Extracion_datos_mensuales(df)
            
            if not data_df.empty:
                # --- BARRA LATERAL ---
                with st.sidebar:
                    # Mostrar metadatos de la estación
                    MostrarMetada(metadata)
                    
                    # Filtros
                    st.markdown("### Filtros de Datos")
                    min_year = int(data_df['Año'].min())
                    max_year = int(data_df['Año'].max())
                    year_range = st.slider(
                        "RANGO DE AÑOS",
                        min_value=min_year,
                        max_value=max_year,
                        value=(min_year, max_year))
                    
                    selected_months = st.multiselect(
                        "MESES A INCLUIR",
                        options=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                                'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic'],
                        default=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                                'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic']
                    )
                    
                    # Aplicar filtros
                    filtered_df = data_df[
                        (data_df['Año'] >= year_range[0]) & 
                        (data_df['Año'] <= year_range[1]) &
                        (data_df['Mes'].isin(selected_months))
                    ]
                    
                    # Mostrar estadísticas resumen
                    Mostrar_resumen_barra_lateral(filtered_df)
                
                # --- CONTENIDO PRINCIPAL ---
                if len(filtered_df) > 0:
                    # Pestañas para diferentes visualizaciones
                    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
                        "📊 Visión General", 
                        "📈 Tendencia Anual", 
                        "🌧️ Patrón Mensual",
                        "📉 Anomalías",
                        "📊 Dispersión",  
                        "📋 Estadísticas",
                        "🗺️ Ubicación",
                        "📥 Datos"
                    ])
                    
                    with tab1:
                        st.markdown("### Visión General de los Datos")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("<div class='plot-title'>Distribución Mensual</div>", unsafe_allow_html=True)
                            fig_dist = Grafica_distribucion_mensual(filtered_df, metadata)
                            st.plotly_chart(fig_dist, use_container_width=True)
                            show_interpretation(
    "Distribución Mensual de Precipitación",
    """
    <div class="highlight-tip">
        Este gráfico combina múltiples medidas estadísticas para mostrar la variabilidad mensual.
    </div>
    
    <ul>
        <li><span class="key-term">Cajas:</span> Representan el rango entre el 25° y 75° percentil (Q1-Q3)</li>
        <li><span class="key-term">Línea central:</span> Mediana (50° percentil) de los datos históricos</li>
        <li><span class="key-term">Bigotes:</span> Extienden hasta 1.5×IQR (rango intercuartílico)</li>
        <li><span class="key-term">Puntos:</span> Valores atípicos extremos fuera del rango de bigotes</li>
        <li><span class="key-term">Línea naranja:</span> Promedio histórico mensual</li>
    </ul>
    
    <div class="divider"></div>
    
    <strong>Análisis recomendado:</strong>
    <ul>
        <li>Busque meses con cajas altas (alta variabilidad interanual)</li>
        <li>Compare mediana vs promedio para identificar sesgos</li>
        <li>Meses con muchos puntos atípicos pueden indicar eventos extremos</li>
        <li>La diferencia entre bigotes superiores/inferiores muestra asimetría</li>
    </ul>
    """,
    icon="📅"
)
                        
                        with col2:
                            st.markdown("<div class='plot-title'>Heatmap Mensual</div>", unsafe_allow_html=True)
                            fig_heat = Mapa_calor_mensual(filtered_df, metadata)
                            st.plotly_chart(fig_heat, use_container_width=True)
                            show_interpretation(
    "Patrón Temporal - Mapa de Calor",
    """
    <div class="highlight-tip">
        Visualización matricial que codifica valores de precipitación en colores para identificar patrones.
    </div>
    
    <ul>
        <li><span class="key-term">Eje Y:</span> Años (orden cronológico descendente)</li>
        <li><span class="key-term">Eje X:</span> Meses (orden estacional)</li>
        <li><span class="key-term">Escala de color:</span> Azul (bajo) → Rojo (alto)</li>
        <li><span class="key-term">Celdas vacías:</span> Datos faltantes en ese período</li>
    </ul>
    
    <div class="divider"></div>
    
    <strong>Patrones clave:</strong>
    <ul>
        <li>Columnas uniformes: Estacionalidad consistente</li>
        <li>Filas atípicas: Años con comportamiento anómalo</li>
        <li>Transiciones bruscas: Cambios rápidos entre estaciones</li>
        <li>Bloques de color: Períodos húmedos/secos prolongados</li>
    </ul>
    """,
    icon="🌡️"
)
                        
                        st.markdown("<div class='plot-title'>Distribución Detallada por Mes</div>", unsafe_allow_html=True)
                        fig_violin = Grafico_violin_mensual(filtered_df, metadata)
                        st.plotly_chart(fig_violin, use_container_width=True)
                        show_interpretation(
    "Distribución de Probabilidad por Mes",
    """
    <div class="highlight-tip">
        Muestra la densidad de probabilidad estimada junto con los datos reales.
    </div>
    
    <ul>
        <li><span class="key-term">Ancho del violín:</span> Frecuencia relativa de valores</li>
        <li><span class="key-term">Puntos internos:</span> Observaciones individuales</li>
        <li><span class="key-term">Caja blanca:</span> Rango intercuartílico (25°-75° percentil)</li>
        <li><span class="key-term">Punto central:</span> Mediana de los datos</li>
    </ul>
    
    <div class="divider"></div>
    
    <strong>Interpretación avanzada:</strong>
    <ul>
        <li>Violines bimodales: Dos regímenes climáticos distintos</li>
        <li>Colas largas: Presencia de valores extremos</li>
        <li>Asimetría: Mayor concentración de valores en un rango</li>
        <li>Violines estrechos: Baja variabilidad interanual</li>
    </ul>
    """,
    icon="🎻"
)
                    
                    with tab2:
                        st.markdown("<div class='plot-title'>Tendencia Anual</div>", unsafe_allow_html=True)
                        fig_trend = Grafico_tendencia_anual(filtered_df, metadata)
                        st.plotly_chart(fig_trend, use_container_width=True)
                        show_interpretation(
    "Tendencia de Precipitación Anual",
    """
    <div class="highlight-tip">
        Análisis de cambios a largo plazo con modelo lineal y suavizado.
    </div>
    
    <ul>
        <li><span class="key-term">Puntos azules:</span> Precipitación anual observada</li>
        <li><span class="key-term">Línea naranja:</span> Tendencia lineal (R² muestra bondad de ajuste)</li>
        <li><span class="key-term">Área sombreada:</span> Intervalo de confianza del 95%</li>
        <li><span class="key-term">Línea azul:</span> Suavizado LOWESS (tendencia no paramétrica)</li>
    </ul>
    
    <div class="divider"></div>
    
    <strong>Indicadores clave:</strong>
    <ul>
        <li><span class="key-term">Pendiente positiva:</span> Aumento promedio de {X} mm/año</li>
        <li><span class="key-term">R² > 0.5:</span> Tendencia estadísticamente significativa</li>
        <li><span class="key-term">Divergencia líneas:</span> Comportamiento no lineal</li>
        <li><span class="key-term">Años fuera del IC:</span> Eventos extremos</li>
    </ul>
    """,
    icon="📈"
)
                        
                        st.markdown("<div class='plot-title'>Precipitación Acumulada</div>", unsafe_allow_html=True)
                        fig_cum = Grafico_precipitacion_anual(filtered_df, metadata)
                        st.plotly_chart(fig_cum, use_container_width=True)
                        show_interpretation(
    "Acumulado Histórico de Precipitación",
    """
    <div class="highlight-tip">
        Muestra la contribución progresiva de cada año al total histórico.
    </div>
    
    <ul>
        <li><span class="key-term">Barras azules:</span> Precipitación anual (eje izquierdo)</li>
        <li><span class="key-term">Línea verde:</span> Acumulado progresivo (eje derecho)</li>
        <li><span class="key-term">Pendiente:</span> Tasa de acumulación anual</li>
    </ul>
    
    <div class="divider"></div>
    
    <strong>Análisis recomendado:</strong>
    <ul>
        <li>Periodos planos: Años secos consecutivos</li>
        <li>Cambios de pendiente: Alteraciones en el régimen pluviométrico</li>
        <li>Comparar altura de barras: Años húmedos vs secos</li>
        <li>El último punto muestra el total acumulado histórico</li>
    </ul>
    """,
    icon="📉"
)
                    
                    with tab3:
                        st.markdown("<div class='plot-title'>Comparación Mensual</div>", unsafe_allow_html=True)
                        
                        selected_year = st.selectbox(
                            "Seleccione un año para comparar",
                            options=sorted(filtered_df['Año'].unique(), reverse=True),
                            key='year_selector'
                        )
                        
                        year_data = filtered_df[filtered_df['Año'] == selected_year]
                        monthly_stats = Calcular_estadisticas_Mensuales(filtered_df)
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=monthly_stats['Mes'],
                            y=monthly_stats['Promedio'],
                            mode='lines',
                            name='Promedio histórico',
                            line=dict(color='#1e3d6b', width=3)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=year_data['Mes'],
                            y=year_data['Precipitación (mm)'],
                            mode='lines+markers',
                            name=f'Año {selected_year}',
                            line=dict(color='#ff8c00', width=3)
                        ))
                        
                        fig.update_layout(
                            title=dict(
                                text=f'Comparación Mensual<br><sup>{metadata.get("Estación", "")}</sup>',
                                x=0.5,
                                xanchor='center',
                                font=dict(size=18, color='#1e3d6b')
                            ),
                            xaxis_title='Mes',
                            yaxis_title='Precipitación (mm)',
                            plot_bgcolor='white',
                            paper_bgcolor='grey',
                            font=dict(
                                family="Arial",
                                size=12,
                                color="#333333"
                            ),
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1,
                                font=dict(
                                    color="#333333",
                                    size=12
                                )
                            ),
                            margin=dict(l=50, r=50, t=100, b=50)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        show_interpretation(
    "Comparación Mensual: Año vs Histórico",
    """
    <div class="highlight-tip">
        Contrasta el comportamiento de un año específico contra el promedio histórico.
    </div>
    
    <ul>
        <li><span class="key-term">Línea azul:</span> Promedio histórico mensual (todos los años)</li>
        <li><span class="key-term">Línea naranja:</span> Datos del año seleccionado ({selected_year})</li>
        <li><span class="key-term">Marcadores:</span> Valores mensuales reales</li>
    </ul>
    
    <div class="divider"></div>
    
    <strong>Análisis recomendado:</strong>
    <ul>
        <li>Busque meses donde la línea naranja se desvíe significativamente de la azul</li>
        <li>Patrones consistentes arriba/abajo del promedio indican años húmedos/secos</li>
        <li>Note si la forma estacional (picos/valles) coincide con el histórico</li>
    </ul>
    
    <div class="highlight-tip" style="background:#fff8e1;border-left:3px solid #ffc107">
        <strong>Nota:</strong> Un año puede ser normal en promedio pero tener meses extremos.
    </div>
    """,
    icon="🔀"
)
                    with tab4:
                        st.markdown("<div class='plot-title'>Anomalías Anuales</div>", unsafe_allow_html=True)
                        fig_anom = Grafica_anomalia_anual(filtered_df, metadata)
                        st.plotly_chart(fig_anom, use_container_width=True)
                        
                        # Calcular estadísticas para el texto dinámico
                        avg_precip = filtered_df.groupby('Año')['Precipitación (mm)'].sum().mean()
                        std_dev = filtered_df.groupby('Año')['Precipitación (mm)'].sum().std()

                        show_interpretation(
    "Anomalías de Precipitación Anual",
    f"""
    <div class="highlight-tip">
        Desviaciones respecto al promedio histórico ({avg_precip:.1f} mm) ± {std_dev:.1f} mm.
    </div>
    
    <ul>
        <li><span class="key-term">Barras azules:</span> Exceso de precipitación (> +1σ)</li>
        <li><span class="key-term">Barras naranjas:</span> Déficit de precipitación (< -1σ)</li>
        <li><span class="key-term">Línea cero:</span> Promedio histórico (referencia)</li>
        <li><span class="key-term">Escala:</span> Desviaciones estándar (σ = {std_dev:.1f} mm)</li>
    </ul>
    
    <div class="divider"></div>
    
    <strong>Clasificación de eventos:</strong>
    <ul>
        <li><span class="key-term">Moderado:</span> ±1σ a ±2σ (colores claros)</li>
        <li><span class="key-term">Severo:</span> ±2σ a ±3σ (colores medios)</li>
        <li><span class="key-term">Extremo:</span> > ±3σ (colores intensos)</li>
    </ul>
    """,
    icon="⚠️"
)
                    
                    with tab5:
                        st.markdown("<div class='plot-title'>Dispersión Anual</div>", unsafe_allow_html=True)
                        fig_scatter_year = Grafica_dispercion_anual(filtered_df, metadata)
                        st.plotly_chart(fig_scatter_year, use_container_width=True)
                        show_interpretation(
    "Dispersión de Precipitación Anual",
    """
    <div class="highlight-tip">
        Muestra la variabilidad interanual y tendencia no lineal.
    </div>
    
    <ul>
        <li><span class="key-term">Puntos verdes:</span> Valores anuales observados</li>
        <li><span class="key-term">Línea naranja:</span> Tendencia suavizada (LOWESS)</li>
        <li><span class="key-term">Eje Y:</span> Precipitación total anual (mm)</li>
    </ul>
    
    <div class="divider"></div>
    
    <strong>Qué observar:</strong>
    <ul>
        <li>Años agrupados en un rango estrecho = Baja variabilidad</li>
        <li>Puntos alejados de la tendencia = Eventos atípicos</li>
        <li>Cambios en la pendiente de la línea = Cambios de régimen</li>
    </ul>
    """,
    icon="🌐"
)
                        st.markdown("<div class='plot-title'>Dispersión Mensual</div>", unsafe_allow_html=True)
                        fig_scatter_month = Grafica_dispercion_mensual(filtered_df, metadata)
                        st.plotly_chart(fig_scatter_month, use_container_width=True)
                        show_interpretation(
    "Dispersión Mensual por Año",
    """
    <div class="highlight-tip">
        Visualiza todos los valores mensuales para detectar patrones y anomalías.
    </div>
    
    <ul>
        <li><span class="key-term">Eje X:</span> Meses (orden estacional)</li>
        <li><span class="key-term">Eje Y:</span> Precipitación mensual (mm)</li>
        <li><span class="key-term">Color:</span> Diferencia entre meses</li>
        <li><span class="key-term">Transparencia:</span> Frecuencia de valores similares</li>
    </ul>
    
    <div class="divider"></div>
    
    <strong>Patrones clave:</strong>
    <ul>
        <li>Nubes de puntos densas = Valores frecuentes</li>
        <li>Puntos aislados superiores = Eventos extremos lluviosos</li>
        <li>Huecos en la distribución = Valores meteorológicamente improbables</li>
    </ul>
    """,
    icon="🔍"
)
                    with tab6:
                        st.markdown("### Estadísticas Detalladas")
                        
                        st.markdown("#### Por Mes")
                        monthly_stats = Calcular_estadisticas_Mensuales(filtered_df)
                        st.dataframe(
                            monthly_stats.style
                                .background_gradient(subset=['Promedio', 'Máximo'], cmap='Blues')
                                .format({
                                    'Promedio': '{:.1f}',
                                    'Mediana': '{:.1f}',
                                    'Desviación': '{:.1f}',
                                    'Mínimo': '{:.1f}',
                                    'Máximo': '{:.1f}'
                                }),
                            use_container_width=True
                        )
                        
                        st.markdown("#### Por Año")
                        annual_stats = Calcular_estadisticas_anuales(filtered_df)
                        st.dataframe(
                            annual_stats.style
                                .background_gradient(subset=['Total Anual', 'Máximo Mensual'], cmap='Blues')
                                .format({
                                    'Total Anual': '{:.1f}',
                                    'Promedio Mensual': '{:.1f}',
                                    'Mediana Mensual': '{:.1f}',
                                    'Variabilidad': '{:.1f}',
                                    'Mínimo Mensual': '{:.1f}',
                                    'Máximo Mensual': '{:.1f}'
                                }),
                            use_container_width=True
                        )
                        show_interpretation(
    "Interpretación de Estadísticas",
    """
    <div class="highlight-tip">
        Resumen numérico para análisis cuantitativo detallado.
    </div>
    
    <strong>Métricas clave por mes:</strong>
    <ul>
        <li><span class="key-term">Promedio vs Mediana:</span> Diferencias indican distribución asimétrica</li>
        <li><span class="key-term">Desviación Estándar:</span> Valores >50% del promedio = Alta variabilidad</li>
        <li><span class="key-term">Máximo/Mínimo:</span> Rango absoluto observado</li>
    </ul>
    
    <div class="divider"></div>
    
    <strong>Métricas anuales:</strong>
    <ul>
        <li><span class="key-term">Total Anual:</span> Comparar con promedio histórico</li>
        <li><span class="key-term">Variabilidad:</span> Consistencia entre meses</li>
        <li><span class="key-term">Máximo Mensual:</span> Eventos extremos registrados</li>
    </ul>
    
    <div class="highlight-tip" style="background:#e8f5e9;border-left:3px solid #4caf50;">
        <strong>Tip:</strong> Use los gradientes de color para identificar rápidamente meses/años destacados.
    </div>
    """,
    icon="📋"
)
                    with tab7:
                        Ubicacion(metadata)
                        show_interpretation(
    "Ubicación Geográfica",
    """
    <div class="highlight-tip">
        La ubicación geográfica explica patrones climáticos y variaciones en los datos.
    </div>
    
    <strong>Factores clave:</strong>
    <ul>
        <li><span class="key-term">Altitud:</span> Afecta directamente la temperatura y precipitación</li>
        <li><span class="key-term">Coordenadas:</span> Determinan el régimen climático local</li>
        <li><span class="key-term">Orografía:</span> Montañas/ríos modifican los patrones de lluvia</li>
    </ul>
    
    <div class="divider"></div>
    
    <strong>Análisis recomendado:</strong>
    <ul>
        <li>Compare con estaciones cercanas para contexto regional</li>
        <li>Verifique exposición a vientos predominantes</li>
        <li>Considere efectos de urbanización en microclima</li>
    </ul>
    
    <div class="highlight-tip" style="background:#e8f5e9;border-left:3px solid #4caf50;">
        <strong>Tip:</strong> Use el mapa interactivo para verificar relieve en Google Maps.
    </div>
    """,
    icon="🌍"
)
                    with tab8:
                        st.markdown("### Datos Completos")
                        st.dataframe(filtered_df, use_container_width=True)
                        
                        try:
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                filtered_df.to_excel(writer, sheet_name='Datos', index=False)
                                
                                if not filtered_df.empty:
                                    monthly_stats = Calcular_estadisticas_Mensuales(filtered_df)
                                    annual_stats = Calcular_estadisticas_anuales(filtered_df)
                                    
                                    writer.book.create_sheet('Estadísticas')
                                    writer.sheets['Estadísticas'] = writer.book['Estadísticas']
                                    
                                    monthly_stats.to_excel(
                                        writer, 
                                        sheet_name='Estadísticas', 
                                        startrow=0, 
                                        index=False
                                    )
                                    
                                    annual_stats.to_excel(
                                        writer, 
                                        sheet_name='Estadísticas', 
                                        startrow=len(monthly_stats)+3, 
                                        index=False
                                    )
                                
                                metadata_list = []
                                for key, value in metadata.items():
                                    if isinstance(value, dict):
                                        metadata_list.append({"Clave": key, "Valor": ""})
                                        for k, v in value.items():
                                            metadata_list.append({"Clave": f"  {k}", "Valor": v})
                                    else:
                                        metadata_list.append({"Clave": key, "Valor": value})
                                
                                pd.DataFrame(metadata_list).to_excel(
                                    writer, 
                                    sheet_name='Metadatos', 
                                    index=False
                                )
                            
                            st.download_button(
                                label="📥 DESCARGAR REPORTE COMPLETO",
                                data=output.getvalue(),
                                file_name=f"reporte_precipitacion_{metadata.get('Estación', 'estacion')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        
                        except Exception as e:
                            st.error(f"Error al generar el reporte: {str(e)}")
                            st.warning("Por favor verifique que los datos no estén vacíos y tengan el formato correcto.")
            else:
                st.warning("El archivo no contiene datos válidos de precipitación")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")
            st.error(traceback.format_exc())
    else:
       mostrar_mensaje_bienvenida()

if __name__ == "__main__":
    main()