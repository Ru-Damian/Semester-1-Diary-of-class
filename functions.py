import pandas as pd
import numpy as np

# Функция для подсчета среденей оценки
def count_mean_mark(df_subject, output = "df"):
    id_mean = df_subject.columns.get_loc("Средняя оценка")
    df_subject["Средняя оценка"] = list(map(int, df_subject.iloc[:, 2:id_mean].mean(axis=1)))
    if output == "df":
        return df_subject
    return df_subject["Средняя оценка"]

# Функция для создания таблицы предмета с синтетическими данными
def create_df_subject(list_students, list_groups):
    df_subject = pd.DataFrame({"ID": [p + 1 for p in range(1000, 1000 + len(list_students))],
                            "Студент": list_students,
                            "Группа": list_groups,
                            "Оценка дз": np.random.randint(0, 101, len(list_students)),
                            "Оценка проект": np.random.randint(0, 101, len(list_students)),
                            "Оценка доклад": np.random.randint(0, 101, len(list_students)),
                            "Средняя оценка": np.nan,
                            "Посещаемость": np.random.randint(0, 101, len(list_students))})
    df_subject = df_subject.set_index("ID")
    df_subject["Средняя оценка"] = count_mean_mark(df_subject, output = "col")
    return df_subject

# Функция для фильтрации таблицы по столбцу двумя способами(compare, value)
def filter_df_column(df_subject, id_column, x, type = "compare", low = True):
    if type == "compare":
        if low:
            return df_subject[df_subject[id_column] < x], len(df_subject[df_subject[id_column] < x])
        return df_subject[df_subject[id_column] > x], len(df_subject[df_subject[id_column] > x])
    elif type == "value":
        return df_subject[df_subject[id_column].isin(x)], len(df_subject[df_subject[id_column].isin(x)])

# Функция для добавления столбца одного из двух типов(mark, bool)
def add_column(df_subject, title, type = "mark"):
    data = np.nan
    if type == "mark":
        id_mean = df_subject.columns.get_loc("Средняя оценка")
        df_subject.insert(loc=id_mean, column=title, value=data)
    elif type == "bool":
        df_subject[title] = data
    return df_subject

# Функция для добавления студента
def add_student(subjects, name, group):
    id = np.nan
    for df_subject in subjects.values():
        if np.isnan(id):
            id = df_subject.index.tolist()[-1] + 1
        df_subject.loc[id] = [name, group] + [np.nan for p in range(df_subject.shape[1] - 2)]

# Функция для удаления студента
def remove_student(subjects, id):
    for subject, df_subject in subjects.items():
        subjects[subject] = df_subject.drop(id, axis=0)

# Функция для изменения значения ячейки в таблице
def replace_value(df_subject, id_column, id_student, value):
    df_subject.loc[id_student, id_column] = value
    count_mean_mark(df_subject)