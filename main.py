import pandas as pd
import numpy as np
import streamlit as st
import functions as func
import time
def load_subjects():
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
    list_groups = subjects[list_subjects[0]]["Группа"].to_list()
    return subjects, list_subjects, list_groups

def save_subjects(subjects):
    for subject, df_subject in subjects.items():
        df_subject.to_csv(f"{subject}.csv")

subjects, list_subjects, list_groups = load_subjects()
actions = ["Добавить студента", "Удалить студента", "Добавить столбец"]

if "subjects" not in st.session_state:
    st.session_state.subjects = subjects
subjects = st.session_state.subjects
st.set_page_config(layout="wide")

st.sidebar.title("Таблицы")
name_table = st.sidebar.selectbox("", (["Все предметы", "Данные студента", "Данные по группам"] + list_subjects))

if name_table in list_subjects:
    st.write(name_table)
    if "editing" not in st.session_state:
        st.session_state.editing = False
    if not st.session_state.editing:
        st.dataframe(subjects[name_table])
        if st.button("Редактировать"):
            st.session_state.editing = True
            st.rerun()
    else:
        edited_df = st.data_editor(subjects[name_table], num_rows="fixed")
        if st.button("Сохранить изменения"):
            subjects[name_table] = edited_df
            save_subjects(subjects)
            st.session_state.editing = False
            st.success("Изменения сохранены!", icon="✅")
            time.sleep(1)
            st.rerun()
else:
    if name_table == "Все предметы":
        st.write(name_table)
        st.dataframe(func.info_subjects(subjects))
    elif name_table == "Данные студента":
        id_student = int(st.sidebar.text_input("ID студента", value=1001))
        if st.sidebar.button("Получить данные"):
            df_student, df_marks = func.info_student(subjects, id_student)
            st.write(name_table)
            st.dataframe(df_student)
            st.write("Оценки по предметам")
            st.dataframe(df_marks)
    else:
        st.write(name_table)
        st.dataframe(func.info_groups(subjects, list_groups))

st.sidebar.title("Действия")
action = st.sidebar.selectbox("", (["Не выбрано"] + actions))

if action == "Добавить студента":
    st.sidebar.subheader("Добавить студента")
    name = st.sidebar.text_input("Имя студента")
    group = int(st.sidebar.text_input("Группа", value = 1))
    if st.sidebar.button("Добавить студента"):
        func.add_student(subjects, name, group)
        save_subjects(subjects)
        st.success(f"Студент {name} ({group}) успешно добавлен!", icon="✅")
        time.sleep(1)
        st.rerun()

if action == "Удалить студента":
    st.sidebar.subheader("Удалить студента")
    id_student = int(st.sidebar.text_input("ID студента", value = 1))
    if st.sidebar.button("Удалить студента"):
        func.remove_student(subjects, id_student)
        save_subjects(subjects)
        st.success(f"Студент с ID {id_student} успешно удален!", icon="✅")
        time.sleep(1)
        st.rerun()

if action == "Добавить столбец":
    st.sidebar.subheader("Добавить столбец")
    title = st.sidebar.text_input("Название")
    type_column = st.sidebar.selectbox("Тип столбца", ("Для оценки", "Другое"))
    if st.sidebar.button("Добавить столбец"):
        if type_column == "Для оценки":
            for df_subject in subjects.values():
                func.add_column(df_subject, title)
        else:
            for df_subject in subjects.values():
                func.add_column(df_subject, title, place="end")
        save_subjects(subjects)
        st.success(f"Столбец {title} успешно создан!", icon="✅")
        time.sleep(1)
        st.rerun()

save_subjects(subjects)