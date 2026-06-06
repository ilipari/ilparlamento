import pandas as pd


def str_to_datetime(df: pd.DataFrame, dt_format='ISO8601', in_place=True, newcol_suffix='_at'):
    string_cols = df.select_dtypes(include=['str']).columns
    for col in string_cols:
        try:
            # Provo a convertire la colonna in data
            date_col = pd.to_datetime(df[col], format=dt_format)
            if in_place:
                df[col] = date_col
            else:
                df[f'{col}{newcol_suffix}'] = date_col
        except (TypeError, ValueError):
            pass
