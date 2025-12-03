import pandas as pd
import numpy as np

# Функция для добавления студента
def add_student(subjects, name, group):
    id = np.nan
    for df_subject in subjects.values():
        if np.isnan(id):
            id = df_subject.index.tolist()[-1] + 1
        df_subject.loc[id] = [name, group] + [np.nan for p in range(df_subject.shape[1] - 2)]
    return id

# Функция для удаления студента
def remove_student(subjects, id):
    name = ""
    group = 0
    for subject, df_subject in subjects.items():
        if name == "" or group == 0:
            name = df_subject.loc[id, "Студент"]
            group = df_subject.loc[id, "Группа"]
        subjects[subject] = df_subject.drop(id, axis=0)
    return name, group