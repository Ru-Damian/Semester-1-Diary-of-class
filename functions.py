import pandas as pd
import numpy as np

# Функция для создания таблицы предмета с синтетическими данными
def create_df_subject(list_students, list_groups):
    df_subject = pd.DataFrame({"Студент": list_students,
                            "Группа": list_groups,
                            "Оценка дз": np.random.randint(0, 101, len(list_students)),
                            "Оценка проект": np.random.randint(0, 101, len(list_students)),
                            "Оценка доклад": np.random.randint(0, 101, len(list_students)),
                            "Средняя оценка": np.random.randint(0, 101, len(list_students)),
                            "Посещаемость": np.random.randint(0, 101, len(list_students))})
    df_subject = df_subject.set_index("Студент")
    return df_subject

def filter_df_column(df_subject, id_column, x, low = True):
    if low:
        return df_subject[df_subject[id_column] < x]
    return df_subject[df_subject[id_column] > x]
