import pandas as pd
import numpy as np

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