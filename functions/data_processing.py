import pandas as pd
import numpy as np

def int_non_error_nan(mean):
    if pd.isna(mean):
        return mean
    else:
        return int(mean)

# Функция для подсчета среденей оценки
def count_mean_mark(df, name_column = "Средняя оценка", output = "df"):
    id_mean = df.columns.get_loc(name_column)
    id_mark1 = ("Студент" in df.columns) + ("Группа" in df.columns) + ("Предмет" in df.columns)
    df[name_column] = list(map(int_non_error_nan, df.iloc[:, id_mark1:id_mean].mean(axis=1)))
    if output == "df":
        return df
    return df[name_column]

# Функция для создания таблицы предмета с синтетическими данными
def create_df_subject(list_id, list_students, list_groups):
    df_subject = pd.DataFrame({
        "ID": list_id,
        "Студент": list_students,
        "Группа": list_groups,
        "Оценка дз": np.random.randint(0, 101, len(list_students)),
        "Оценка проект": np.random.randint(0, 101, len(list_students)),
        "Оценка доклад": np.random.randint(0, 101, len(list_students)),
        "Средняя оценка": np.nan,
        "Посещаемость": np.random.randint(0, 101, len(list_students))
        })
    df_subject = df_subject.set_index("ID")
    df_subject["Средняя оценка"] = count_mean_mark(df_subject, output = "col")
    return df_subject

# Функция для фильтрации таблицы по столбцу двумя способами(compare, value)
# compare -- оставить строки, где в столбце name_column значения больше(low = False) или меньше(low = True) значения x(int)
# value   -- оставить строки, где в столбце name_column значения совпадают со значениями из списка x(int, list)
def filter_df_column(df_subject, name_column, x, type_f = "compare", low = True):
    if type_f == "compare":
        if low:
            return df_subject[df_subject[name_column] < x], len(df_subject[df_subject[name_column] < x])
        return df_subject[df_subject[name_column] > x], len(df_subject[df_subject[name_column] > x])
    elif type_f == "value":
        if type(x) != list():
            x = [x]
        return df_subject[df_subject[name_column].isin(x)], len(df_subject[df_subject[name_column].isin(x)])

# Функция для добавления столбца одного из двух типов(before, end)
# before -- создать столбец перед столбцом name_column_before
# end    -- создать столбец в конце таблицы
def add_column(df_subject, title, place = "before", name_column_before = "Средняя оценка"):
    data = np.nan
    if place == "before":
        id_column = df_subject.columns.get_loc(name_column_before)
        df_subject.insert(loc=id_column, column=title, value=data)
    elif place == "end":
        df_subject[title] = data
    return df_subject

# Функция для изменения значения ячейки в таблице
def replace_value(df_subject, name_column, id, value):
    df_subject.loc[id, name_column] = value
    df_subject = count_mean_mark(df_subject)