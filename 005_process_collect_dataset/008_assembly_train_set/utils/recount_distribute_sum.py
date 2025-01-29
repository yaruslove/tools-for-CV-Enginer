import numpy as np
import pandas as pd
from utils.distribute_sum import distribute_sum

def recount_distribute_sum(df_asis, amount_in_class):
    # Create a new empty DataFrame with the same structure
    df_redistribute = pd.DataFrame()
    
    # Copy the 'name' column
    df_redistribute['name'] = df_asis['name']
    
    # Process each numeric column
    for col in df_asis.columns:
        if col != 'name':  # Skip the name column
            # Convert column to numeric type and handle NaN values
            column_data = pd.to_numeric(df_asis[col], errors='coerce').fillna(0)
            list_init = column_data.tolist()
            
            # Apply distribute_sum function
            list_new = distribute_sum(list_init, amount_in_class)
            
            # Add the redistributed values to the new DataFrame
            df_redistribute[col] = list_new
    
    return df_redistribute




"""
Ниже функция УСРЕДНЯЕТ ПО СТРОКАМ
Функция recount_distribute_sum пересчитывает значения в каждой строке DataFrame так, 
чтобы их сумма равнялась заданному числу amount_in_class, сохраняя пропорции между значениями и возвращая новый DataFrame.
"""

# def recount_distribute_sum(df_asis: pd.DataFrame, amount_in_class: int) -> pd.DataFrame:
#     df_new = df_asis.copy()
#     numeric_columns = [col for col in df_asis.columns if col != 'name']
    
#     for idx in df_asis.index:
#         # Получаем строку с числовыми значениями
#         current_row = df_asis.loc[idx, numeric_columns]
        
#         # Сначала приводим к float64, затем заменяем пропущенные значения
#         row_float = current_row.astype(np.float64)
#         row_no_na = row_float.fillna(0)
        
#         # Применяем infer_objects для правильного определения типов
#         row_inferred = row_no_na.infer_objects(copy=False)
        
#         # Преобразуем в список
#         row_values = row_inferred.tolist()
        
#         # Применяем distribute_sum
#         new_values = distribute_sum(row_values, amount_in_class)
        
#         # Обновляем значения
#         for col, value in zip(numeric_columns, new_values):
#             df_new.loc[idx, col] = value
            
#     return df_new