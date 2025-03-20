# preprocessing.py
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def load_preprocessor(df):
    """
    Crea y ajusta el preprocesador con los datos originales.
    """
    X = df[["Certificacion", "Subcontratacion", "Plazo"]]
    categorical_col = "Subcontratacion"
    numerical_cols = ["Certificacion", "Plazo"]

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), [categorical_col])
        ])

    preprocessor.fit(X)
    return preprocessor
