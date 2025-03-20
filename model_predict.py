# model_predict.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from preprocessing import load_preprocessor

# Cargar dataset original para entrenamiento
# Solo si se entrena nuevamente
# df = pd.read_csv('bbdd3.csv', encoding='ISO-8859-1', delimiter=';')

# Funciones para modelos ya entrenados (a usar en prediccion)

# Modelos afinados
rf_model = RandomForestRegressor(n_estimators=100, max_depth=30,
                                 min_samples_split=2, min_samples_leaf=4, random_state=42)

xgb_model = XGBRegressor(n_estimators=200, max_depth=5, learning_rate=0.01,
                         subsample=0.8, colsample_bytree=1, random_state=42, verbosity=0)

# Simulación: Cargar df para preprocesador y entrenamiento de modelos
# En tu implementación real, entrena una vez y guarda los modelos (pkl)
df_train = pd.read_csv('bbdd3.csv', encoding='ISO-8859-1', delimiter=';')
df_train = df_train.rename(columns={df_train.columns[4]: "Certificacion",
                                    df_train.columns[8]: "Subcontratacion",
                                    df_train.columns[9]: "Plazo",
                                    df_train.columns[3]: "Dias"})

preprocessor = load_preprocessor(df_train)
X_train = df_train[["Certificacion", "Subcontratacion", "Plazo"]]
y_train = df_train["Dias"]

# Entrenar modelos
rf_model.fit(preprocessor.transform(X_train), y_train)
xgb_model.fit(preprocessor.transform(X_train), y_train)


# Función principal de predicción
def predecir_dias(certificacion_total, plazo_meses, subcontratacion):
    """
    Devuelve la estimación de días imputados a partir de los 3 datos del usuario.
    """
    input_df = pd.DataFrame({
        "Certificacion": [certificacion_total],
        "Subcontratacion": [subcontratacion],  # "Si" o "No"
        "Plazo": [plazo_meses]
    })

    X_trans = preprocessor.transform(input_df)

    pred_rf = rf_model.predict(X_trans)[0]
    pred_xgb = xgb_model.predict(X_trans)[0]

    dias_estimados = 0.5 * pred_rf + 0.5 * pred_xgb

    return round(dias_estimados, 2)
