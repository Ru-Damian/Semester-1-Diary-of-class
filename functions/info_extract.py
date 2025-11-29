import pandas as pd
from .data_processing import *

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