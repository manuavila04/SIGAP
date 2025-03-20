# cost_predict.py
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

# Cargar dataset
df = pd.read_csv('bbdd3.csv', encoding='ISO-8859-1', delimiter=';')

# Inputs: columnas 3,4,8,9 (índices 3,4,8,9), Output: columna 7 (índice 7)
X = df.iloc[:, [3, 4, 8, 9]].values
y = df.iloc[:, 7].values

# Preprocesamiento: columna 2 de X (índice 2 global = columna 8) es categórica
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), [0, 1, 3]),  # columnas 3,4,9
        ('cat', OneHotEncoder(handle_unknown='ignore'), [2])  # columna 8 (subcontratación)
    ])

X_trans = preprocessor.fit_transform(X)

# Modelo XGBoost afinado
ygb_model_coste = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42, verbosity=0)
ygb_model_coste.fit(X_trans, y)

# Funcón de predicción
def predecir_coste(certificacion, plazo, subcontratacion, dias):
    input_data = np.array([[dias, certificacion, subcontratacion, plazo]])
    input_df = pd.DataFrame(input_data, columns=[0, 1, 2, 3])
    input_trans = preprocessor.transform(input_df)
    coste_estimado = ygb_model_coste.predict(input_trans)[0]
    return round(coste_estimado, 2)
