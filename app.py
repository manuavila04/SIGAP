# app.py (Interfaz web con Streamlit)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from model_predict import predecir_dias
from cost_predict import predecir_coste

st.set_page_config(page_title="Estimador de Proyectos", layout="centered")
st.image("logo.png", width=200)
st.title("📊 Estimador de Días Imputados y Coste Total")

# Inicializar estado de sesión
if 'dias_estimados' not in st.session_state:
    st.session_state.dias_estimados = None
if 'dias_final' not in st.session_state:
    st.session_state.dias_final = None
if 'historial' not in st.session_state:
    st.session_state.historial = []

# Entrada de datos
st.subheader("Introduce los datos del proyecto")
certificacion = st.number_input("Certificación total del proyecto (EUR):", min_value=0.0, step=1000.0)
plazo = st.number_input("Plazo en meses:", min_value=0.0, step=1.0)
subcontrata = st.selectbox("Requiere subcontratación:", ["Si", "No"])

# Paso 1: Estimar días
if st.button("Estimar Días"):
    st.session_state.dias_estimados = predecir_dias(certificacion, plazo, subcontrata)
    st.session_state.dias_final = st.session_state.dias_estimados

# Mostrar y editar días estimados
if st.session_state.dias_estimados is not None:
    st.success(f"Días imputados estimados: {st.session_state.dias_estimados}")
    st.session_state.dias_final = st.number_input("Editar días imputados (opcional):",
                                                 value=st.session_state.dias_final,
                                                 step=1.0, key="dias_edit")

    # Validación automática
    dias_maximos = plazo * 30
    if st.session_state.dias_final > dias_maximos:
        st.warning(f"⚠️ Los días imputados superan el máximo recomendado ({dias_maximos} días para {plazo} meses). Revisa los datos.")

    if st.button("Estimar Coste Total"):
        coste_estimado = predecir_coste(certificacion, plazo, subcontrata, st.session_state.dias_final)
        st.success(f"Coste total estimado: {coste_estimado:.2f} EUR")

        # Mostrar resumen como tabla mejorada
        st.subheader("Resumen del Proyecto")
        resumen_dict = {
            "Certificación (EUR)": certificacion,
            "Plazo (meses)": plazo,
            "Subcontratación": subcontrata,
            "Días Imputados": st.session_state.dias_final,
            "Coste Total (EUR)": f"{coste_estimado:.2f}"
        }
        resumen_df = pd.DataFrame(resumen_dict.items(), columns=["Parámetro", "Valor"])
        st.dataframe(resumen_df, use_container_width=True, hide_index=True)

        # Guardar en historial
        st.session_state.historial.append({
            'Certificación (EUR)': certificacion,
            'Plazo (meses)': plazo,
            'Subcontratación': subcontrata,
            'Días Imputados': st.session_state.dias_final,
            'Coste Total (EUR)': coste_estimado
        })

# Mostrar historial de predicciones
if st.session_state.historial:
    st.subheader("Historial de Proyectos")
    historial_df = pd.DataFrame(st.session_state.historial)
    seleccion = st.multiselect("Selecciona proyectos para comparar:", historial_df.index, format_func=lambda i: f"Proyecto {i+1}")
    st.dataframe(historial_df, use_container_width=True)

    if seleccion:
        # Graficas comparativas
        st.subheader("Comparativa de Costes y Días Imputados")
        sub_df = historial_df.loc[seleccion]

        fig, ax = plt.subplots(2, 1, figsize=(8, 8))
        sub_df.plot(kind='bar', x='Certificación (EUR)', y='Coste Total (EUR)', ax=ax[0], legend=False, color='skyblue')
        ax[0].set_ylabel("Coste Total (EUR)")
        ax[0].set_title("Coste Total vs Certificación")

        sub_df.plot(kind='bar', x='Certificación (EUR)', y='Días Imputados', ax=ax[1], legend=False, color='lightgreen')
        ax[1].set_ylabel("Días Imputados")
        ax[1].set_title("Días Imputados vs Certificación")

        st.pyplot(fig)
