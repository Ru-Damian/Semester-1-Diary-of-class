import pandas as pd
import numpy as np

# Функция для подсчета среденей оценки
def count_mean_mark(df_subject, name_column = "Средняя оценка", output = "df"):
    id_mean = df_subject.columns.get_loc(name_column)
    id_mark1 = ("Студент" in df_subject.columns) + ("Группа" in df_subject.columns)
    df_subject[name_column] = list(map(int, df_subject.iloc[:, id_mark1:id_mean].mean(axis=1)))
    if output == "df":
        return df_subject
    return df_subject[name_column]

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
    data = 0
    if place == "before":
        id_column = df_subject.columns.get_loc(name_column_before)
        df_subject.insert(loc=id_column, column=title, value=data)
    elif place == "end":
        df_subject[title] = data
    return df_subject

# Функция для добавления студента
def add_student(subjects, name, group):
    id = np.nan
    for df_subject in subjects.values():
        if np.isnan(id):
            id = df_subject.index.tolist()[-1] + 1
        df_subject.loc[id] = [name, group] + [0 for p in range(df_subject.shape[1] - 2)]

# Функция для удаления студента
def remove_student(subjects, id_student):
    for subject, df_subject in subjects.items():
        subjects[subject] = df_subject.drop(id_student, axis=0)

# Функция для изменения значения ячейки в таблице
def replace_value(df_subject, name_column, id, value):
    df_subject.loc[id, name_column] = value
    df_subject = count_mean_mark(df_subject)

# Функция для вывода всей информации о студенте по одному предмету или всем
def info_student(subjects, id_student, name_subject = "all"):
    data_marks = list()
    for subject, df_subject in subjects.items():
        row = df_subject.loc[id_student]
        data_row = dict()
        data_row["Предмет"] = subject
        for col in df_subject.columns:
            data_row[col] = row[col]
        data_marks.append(data_row)
    df_marks = pd.DataFrame(data_marks).set_index("Предмет")
    df_student = pd.DataFrame({
        "ID": id_student,
        "Студент": df_marks["Студент"][0],
        "Группа": df_marks["Группа"][0],
        "Средний балл": int(df_marks["Средняя оценка"].mean(axis = 0)),
        "Посещаемость": int(df_marks["Посещаемость"].mean(axis = 0))
        }, index=[id_student]).set_index("ID")
    df_marks.drop(["Студент", "Группа"], inplace=True, axis=1)
    # print("Данные студента\n", df_student.to_string(index=False), "\n")
    # if name_subject == "all":
    #     print("Оценки по предметам\n", df_marks, "\n")
    # else:
    #     print("Оценки по предмету\n", pd.DataFrame(df_marks.loc[name_subject]).T, "\n")
    if name_subject == "all":
        return df_student, df_marks
    return df_student, pd.DataFrame(df_marks.loc[name_subject]).T

# Функция для вывода средних оценок по всем предметам
def info_subjects(subjects):
    data_subjects = dict()
    data_attendance = list()
    cnt = 0
    for subject, df_subject in subjects.items():
        cnt += 1
        if data_subjects == dict():
            data_subjects["ID"] = df_subject.index
            data_subjects["Студент"] = df_subject["Студент"]
            data_subjects["Группа"] = df_subject["Группа"]
        data_subjects[subject] = df_subject["Средняя оценка"]
        data_attendance.append(df_subject["Посещаемость"])
    data_attendance = list(map(int, sum(data_attendance) / cnt))
    data_subjects["Посещаемость"] = data_attendance
    df_subjects = pd.DataFrame(data_subjects).set_index("ID")
    df_subjects = add_column(df_subjects, "Средний балл", place = "before", name_column_before = "Посещаемость")
    df_subjects = count_mean_mark(df_subjects, name_column="Средний балл")
    # print("Все предметы\n", df_subjects, "\n")
    return df_subjects

# Функция для вывода средних оценок по всем предметам по группам
def info_groups(subjects, list_groups):
    data_groups = dict()
    data_groups["Группа"] = sorted(set(list_groups))
    data_attendance = list()
    cnt = 0
    for subject, df_subject in subjects.items():
        cnt += 1
        data_subject = list()
        data_subject_attendance = list()
        for group in data_groups["Группа"]:
            df_group = filter_df_column(df_subject, "Группа", group, type_f = "value")[0]
            data_subject.append(int(df_group["Средняя оценка"].mean()))
            data_subject_attendance.append(int(df_group["Посещаемость"].mean()))
        data_groups[subject] = data_subject
        data_attendance.append(pd.Series(data_subject_attendance))
    data_attendance = list(map(int, sum(data_attendance) / cnt))
    data_groups["Посещаемость"] = data_attendance
    df_groups = pd.DataFrame(data_groups).set_index("Группа")
    df_groups = add_column(df_groups, "Средний балл", place = "before", name_column_before = "Посещаемость")
    df_groups = count_mean_mark(df_groups, name_column="Средний балл")
    # print("Средние баллы по группам\n", df_groups, "\n")
    return df_groups