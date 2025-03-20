# app.py (Interfaz web con Streamlit)
import streamlit as st
from model_predict import predecir_dias
from cost_predict import predecir_coste

st.set_page_config(page_title="Estimador de Proyectos", layout="centered")
st.title("📊 Estimador de Días Imputados y Coste Total")

# Inicializar estado de sesión
if 'dias_estimados' not in st.session_state:
    st.session_state.dias_estimados = None
if 'dias_final' not in st.session_state:
    st.session_state.dias_final = None

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

    if st.button("Estimar Coste Total"):
        coste_estimado = predecir_coste(certificacion, plazo, subcontrata, st.session_state.dias_final)
        st.success(f"Coste total estimado: {coste_estimado:.2f} EUR")

        # Mostrar resumen
        st.subheader("Resumen")
        st.write(f"- Certificación: {certificacion} EUR")
        st.write(f"- Plazo: {plazo} meses")
        st.write(f"- Subcontratación: {subcontrata}")
        st.write(f"- Días Imputados: {st.session_state.dias_final}")
        st.write(f"- Coste Total: {coste_estimado:.2f} EUR")