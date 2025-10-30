import pandas as pd
import numpy as np

# Функция для подсчета среденей оценки
def count_mean_mark(df_subject, id_column = "Средняя оценка", output = "df"):
    id_mean = df_subject.columns.get_loc(id_column)
    df_subject[id_column] = list(map(int, df_subject.iloc[:, 2:id_mean].mean(axis=1)))
    if output == "df":
        return df_subject
    return df_subject[id_column]

# Функция для создания таблицы предмета с синтетическими данными
def create_df_subject(list_students, list_groups):
    df_subject = pd.DataFrame({
        "ID": [p + 1 for p in range(1000, 1000 + len(list_students))],
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
def filter_df_column(df_subject, id_column, x, type_f = "compare", low = True):
    if type_f == "compare":
        if low:
            return df_subject[df_subject[id_column] < x], len(df_subject[df_subject[id_column] < x])
        return df_subject[df_subject[id_column] > x], len(df_subject[df_subject[id_column] > x])
    elif type_f == "value":
        if type(x) != list():
            x = [x]
        return df_subject[df_subject[id_column].isin(x)], len(df_subject[df_subject[id_column].isin(x)])

# Функция для добавления столбца одного из двух типов(mark, bool)
def add_column(df_subject, title, type_f = "mark"):
    data = np.nan
    if type_f == "mark":
        id_mean = df_subject.columns.get_loc("Средняя оценка")
        df_subject.insert(loc=id_mean, column=title, value=data)
    elif type_f == "bool":
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

# Функция для вывода всей информации о студенте по одному предмету или всем
def info_student(subjects, id, id_subject = "all"):
    data_marks = list()
    for subject, df_subject in subjects.items():
        row = df_subject.loc[id]
        data_row = dict()
        data_row["Предмет"] = subject
        for col in df_subject.columns:
            data_row[col] = row[col]
        data_marks.append(data_row)
    df_marks = pd.DataFrame(data_marks).set_index("Предмет")
    df_student = pd.DataFrame({
        "Студент": df_marks["Студент"][0],
        "Группа": df_marks["Группа"][0],
        "Средний балл": int(df_marks["Средняя оценка"].mean(axis = 0)),
        "Посещаемость": int(df_marks["Посещаемость"].mean(axis = 0))
        }, index=[id])
    df_marks.drop(["Студент", "Группа"], inplace=True, axis=1)
    print("Данные студента\n", df_student.to_string(index=False), "\n")
    if id_subject == "all":
        print("Оценки по предметам\n", df_marks, "\n")
    else:
        print("Оценки по предмету\n", pd.DataFrame(df_marks.loc[id_subject]).T, "\n")

# Функция для вывода средних оценок по всем предметам
def info_subjects(subjects):
    data_subjects = dict()
    for subject, df_subject in subjects.items():
        if data_subjects == dict():
            data_subjects["ID"] = df_subject.index
            data_subjects["Студент"] = df_subject["Студент"]
            data_subjects["Группа"] = df_subject["Группа"]
        data_subjects[subject] = df_subject["Средняя оценка"]
    df_subjects = pd.DataFrame(data_subjects).set_index("ID")
    df_subjects = add_column(df_subjects, "Средний балл", type_f = "bool")
    df_subjects = count_mean_mark(df_subjects, id_column="Средний балл")
    print("Все предметы\n", df_subjects, "\n")