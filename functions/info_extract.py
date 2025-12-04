import pandas as pd
import numpy as np
from .data_processing import int_non_error_nan, count_mean_mark, filter_df_column, add_column

# Функция для вывода всей информации о студенте по одному предмету или всем
def info_student(subjects, id_student, name_subject = "all"):
    columns_before_mean = list()
    columns_after_mean = list()
    for df_subject in subjects.values():
        id_mean = df_subject.columns.get_loc("Средняя оценка")
        for col in df_subject.columns[:id_mean]:
            if col not in columns_before_mean:
                columns_before_mean.append(col)
        for col in df_subject.columns[id_mean + 1:]:
            if col not in columns_after_mean:
                columns_after_mean.append(col)
    columns_order = columns_before_mean + ["Средняя оценка"] + columns_after_mean
    data_marks = list()
    for subject, df_subject in subjects.items():
        row = df_subject.loc[id_student]
        data_row = dict()
        data_row["Предмет"] = subject
        for col in columns_order:
            data_row[col] = row[col] if col in df_subject.columns else np.nan
        data_marks.append(data_row)
    df_marks = pd.DataFrame(data_marks).set_index("Предмет")
    df_student = pd.DataFrame({
        "ID": id_student,
        "Студент": df_marks["Студент"].iloc[0],
        "Группа": df_marks["Группа"].iloc[0],
        "Средний балл": int_non_error_nan(df_marks["Средняя оценка"].mean(axis = 0)),
        "Посещаемость": int_non_error_nan(df_marks["Посещаемость"].mean(axis = 0))
        }, index=[id_student]).set_index("ID")
    df_marks.drop(["Студент", "Группа"], inplace=True, axis=1)
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
    data_attendance = list(map(int_non_error_nan, sum(data_attendance) / cnt))
    data_subjects["Посещаемость"] = data_attendance
    df_subjects = pd.DataFrame(data_subjects).set_index("ID")
    df_subjects = add_column(df_subjects, "Средний балл", place = "before", name_column_before = "Посещаемость")
    df_subjects = count_mean_mark(df_subjects, name_column="Средний балл")
    return df_subjects

# Функция для вывода средних оценок по всем предметам по группам
def info_groups(subjects, list_groups):
    data_groups = dict()
    data_groups["Группа"] = list_groups
    data_attendance = list()
    cnt = 0
    for subject, df_subject in subjects.items():
        cnt += 1
        data_subject = list()
        data_subject_attendance = list()
        for group in data_groups["Группа"]:
            df_group = filter_df_column(df_subject, "Группа", group, type_f = "value")[0]
            data_subject.append(int_non_error_nan(df_group["Средняя оценка"].mean()))
            data_subject_attendance.append(int_non_error_nan(df_group["Посещаемость"].mean()))
        data_groups[subject] = data_subject
        data_attendance.append(pd.Series(data_subject_attendance))
    data_attendance = list(map(int_non_error_nan, sum(data_attendance) / cnt))
    data_groups["Посещаемость"] = data_attendance
    df_groups = pd.DataFrame(data_groups).set_index("Группа")
    df_groups = add_column(df_groups, "Средний балл", place = "before", name_column_before = "Посещаемость")
    df_groups = count_mean_mark(df_groups, name_column="Средний балл")
    return df_groups