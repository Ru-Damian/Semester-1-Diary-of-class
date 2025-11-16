import pandas as pd
import numpy as np
import streamlit as st
import functions as func

with open("subjects.txt", "r", encoding="utf-8") as file:
    list_subjects = [s.strip() for s in file]

subjects = dict()
for subject in list_subjects:
    try:
        subjects[subject] = pd.read_csv(f"{subject}.csv", encoding="utf-8", sep=',').set_index("ID")
    except FileNotFoundError:
        try:
            subjects[subject] = func.create_df_subject(list_id, list_students, list_groups)
        except NameError:
            with open("students.txt", "r", encoding="utf-8") as file:
                list_id = list()
                list_students = list()
                list_groups = list()
                for line in file:
                    id, fio, group = line.strip().split(";")
                    list_id.append(id)
                    list_students.append(fio)
                    list_groups.append(group)
            subjects[subject] = func.create_df_subject(list_id, list_students, list_groups)

print(subjects["Химия"])

for subject, df_subject in subjects.items():
    df_subject.to_csv(f"{subject}.csv")