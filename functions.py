import pandas as pd
import numpy as np

# Функция для подсчета среденей оценки
def count_mean_mark(df_subject, output = "df"):
    id_mean = df_subject.columns.get_loc("Средняя оценка")
    df_subject["Средняя оценка"] = list(map(int, df_subject.iloc[:, 1:id_mean].mean(axis=1)))
    if output == "df":
        return df_subject
    return df_subject["Средняя оценка"]

# Функция для создания таблицы предмета с синтетическими данными
def create_df_subject(list_students, list_groups):
    df_subject = pd.DataFrame({"Студент": list_students,
                            "Группа": list_groups,
                            "Оценка дз": np.random.randint(0, 101, len(list_students)),
                            "Оценка проект": np.random.randint(0, 101, len(list_students)),
                            "Оценка доклад": np.random.randint(0, 101, len(list_students)),
                            "Средняя оценка": np.nan,
                            "Посещаемость": np.random.randint(0, 101, len(list_students))})
    df_subject = df_subject.set_index("Студент")
    df_subject["Средняя оценка"] = count_mean_mark(df_subject, output = "col")
    return df_subject

# Функция для фильтрации таблицы по столбцу
def filter_df_column(df_subject, id_column, x, low = True):
    if low:
        return df_subject[df_subject[id_column] < x]
    return df_subject[df_subject[id_column] > x]

# Функция для добавления столбца одного из двух типов(mark, bool)
def add_column(df_subject, title, type = "mark"):
    data = np.nan
    if type == "mark":
        id_mean = df_subject.columns.get_loc("Средняя оценка")
        df_subject.insert(loc=id_mean, column=title, value=data)
    if type == "bool":
        df_subject[title] = data
    return df_subject