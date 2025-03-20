# app.py (Interfaz web con Streamlit)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from model_predict import predecir_dias
from cost_predict import predecir_coste
from fpdf import FPDF
import io

st.set_page_config(page_title="Estimador de Proyectos", layout="centered")
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

        # Mostrar resumen como tabla
        st.subheader("Resumen del Proyecto")
        resumen_data = {
            'Parámetro': ['Certificación (EUR)', 'Plazo (meses)', 'Subcontratación', 'Días Imputados', 'Coste Total (EUR)'],
            'Valor': [certificacion, plazo, subcontrata, st.session_state.dias_final, f"{coste_estimado:.2f}"]
        }
        resumen_df = pd.DataFrame(resumen_data)
        st.table(resumen_df)

        # Guardar en historial
        st.session_state.historial.append({
            'Certificación (EUR)': certificacion,
            'Plazo (meses)': plazo,
            'Subcontratación': subcontrata,
            'Días Imputados': st.session_state.dias_final,
            'Coste Total (EUR)': coste_estimado
        })

        # Generar PDF resumen individual
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Resumen del Proyecto", ln=True, align='C')
        pdf.ln(10)
        for param, val in zip(resumen_data['Parámetro'], resumen_data['Valor']):
            pdf.cell(200, 10, txt=f"{param}: {val}", ln=True)

        pdf_output = "resumen_proyecto.pdf"
        pdf.output(pdf_output)

        with open(pdf_output, "rb") as file:
            st.download_button("🔗 Descargar resumen en PDF", data=file, file_name="resumen_proyecto.pdf", mime="application/pdf")

# Mostrar historial de predicciones
if st.session_state.historial:
    st.subheader("Historial de Proyectos")
    historial_df = pd.DataFrame(st.session_state.historial)
    seleccion = st.multiselect("Selecciona proyectos para exportar:", historial_df.index, format_func=lambda i: f"Proyecto {i+1}")
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

        # Generar PDF resumen multiple
        pdf_multi = FPDF()
        pdf_multi.add_page()
        pdf_multi.set_font("Arial", size=12)
        pdf_multi.cell(200, 10, txt="Resumen Comparativo de Proyectos", ln=True, align='C')
        pdf_multi.ln(10)
        for idx in seleccion:
            row = historial_df.loc[idx]
            for col in historial_df.columns:
                pdf_multi.cell(200, 10, txt=f"{col}: {row[col]}", ln=True)
            pdf_multi.ln(5)

        pdf_multi_output = "historial_proyectos.pdf"
        pdf_multi.output(pdf_multi_output)

        with open(pdf_multi_output, "rb") as file:
            st.download_button("🔗 Descargar historial seleccionado en PDF", data=file, file_name="historial_proyectos.pdf", mime="application/pdf")
