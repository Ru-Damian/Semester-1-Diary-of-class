import pandas as pd
import numpy as np
import streamlit as st
import functions as func
import time

def write_log(action, info):
    with open("logs.log", "a", encoding="utf-8") as file:
        file.write(f"{time.strftime('[%Y-%m-%d %H:%M:%S]')} {action}: {info}\n")

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
            write_log("Создать таблицу предмета", f"Предмет = {subject}") # log
    list_groups = subjects[list_subjects[0]]["Группа"].to_list()
    return subjects, list_subjects, list_groups

def save_subjects(subjects):
    for subject, df_subject in subjects.items():
        df_subject.to_csv(f"{subject}.csv")

subjects, list_subjects, list_groups = load_subjects()
actions = ["Отфильтровать", "Добавить студента", "Удалить студента", "Добавить столбец"]

if "subjects" not in st.session_state:
    st.session_state.subjects = subjects
subjects = st.session_state.subjects
st.set_page_config(layout="wide")

st.sidebar.title("Таблицы")
name_table = st.sidebar.selectbox("", (["Все предметы", "Данные студента", "Данные по группам"] + list_subjects))

if name_table in list_subjects:
    if "filtering" not in st.session_state:
        st.session_state.filtering = False
    if not st.session_state.filtering:
        st.write(name_table)
        if "editing" not in st.session_state:
            st.session_state.editing = False
        if not st.session_state.editing:
            st.dataframe(subjects[name_table])
            if st.button("Редактировать"):
                st.session_state.editing = True
                write_log("Редактировать", f"Предмет = {name_table}") # log
                st.rerun()
        else:
            edited_df = st.data_editor(subjects[name_table], num_rows="fixed")
            edited_df["Группа"] = edited_df["Группа"].clip(lower=1, upper=15)
            for col in edited_df.columns[2:]:
                edited_df[col] = edited_df[col].clip(lower=0, upper=100)
            edited_df = func.count_mean_mark(edited_df)
            if st.button("Сохранить изменения"):
                time.sleep(0.1)
                subjects[name_table] = edited_df
                save_subjects(subjects)
                st.session_state.editing = False
                write_log("Сохранить", f"Предмет = {name_table}") # log
                st.success("Изменения сохранены!", icon="✅")
                time.sleep(1)
                st.rerun()
        st.download_button("Скачать", subjects[name_table].to_csv().encode("utf-8"), f"{name_table}.csv")
    else:
        st.write(name_table)
        filtered_df = st.session_state.filtered_df
        st.dataframe(filtered_df)
        if st.button("Сбросить"):
            st.session_state.filtering = False
            st.rerun()
else:
    if name_table == "Все предметы":
        st.write(name_table)
        st.dataframe(func.info_subjects(subjects))
    elif name_table == "Данные студента":
        st.write("Все предметы")
        st.dataframe(func.info_subjects(subjects))
        id_student = st.sidebar.number_input("ID студента", value=1001, min_value=1001)
        if st.sidebar.button("Получить данные"):
            try:
                df_student, df_marks = func.info_student(subjects, id_student)
                st.write(name_table)
                st.dataframe(df_student)
                st.write("Оценки по предметам")
                st.dataframe(df_marks)
            except KeyError:
                st.warning("Студента с таким ID не существует", icon = "❌")
    else:
        st.write(name_table)
        st.dataframe(func.info_groups(subjects, list_groups))

st.sidebar.title("Действия")
action = st.sidebar.selectbox("", (["Не выбрано"] + actions))

if action == "Добавить студента":
    st.sidebar.subheader("Добавить студента")
    name = st.sidebar.text_input("Имя студента")
    group = st.sidebar.number_input("Группа", value = 1, min_value = 1, max_value = 15)
    if st.sidebar.button("Добавить студента"):
        func.add_student(subjects, name, group)
        save_subjects(subjects)
        write_log(action, f"ФИО = {name}, Группа = {group}") # log
        st.success(f"Студент {name} ({group}) успешно добавлен!", icon="✅")
        time.sleep(1)
        st.rerun()

if action == "Удалить студента":
    st.sidebar.subheader("Удалить студента")
    id_student = st.sidebar.number_input("ID студента", value = 1002, min_value=1001)
    if st.sidebar.button("Удалить студента"):
        try:
            func.remove_student(subjects, id_student)
            save_subjects(subjects)
            write_log(action, f"ID студента = {id_student}")
            st.success(f"Студент с ID {id_student} успешно удален!", icon="✅")
            time.sleep(1)
            st.rerun()
        except KeyError:
            st.warning("Студента с таким ID не существует", icon = "❌")

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
        write_log(action, f"Название = {title}, Тип столбца = {type_column}") # log
        st.success(f"Столбец {title} успешно создан!", icon="✅")
        time.sleep(1)
        st.rerun()

if action == "Отфильтровать":
    try:
        error = subjects[name_table]
        st.sidebar.subheader("Параметры фильтра")
        column_filter = st.sidebar.selectbox("Столбец для фильтрации", (subjects[name_table].columns[2:]))
        x_filter = st.sidebar.slider(f"{column_filter} > значения", value=50, min_value=10, max_value=90)
        low_filter = st.sidebar.checkbox(f"{column_filter} < значения")
        if st.sidebar.button("Показать результат"):
            st.write(name_table)
            filtered_df, filtered_cnt_row = func.filter_df_column(subjects[name_table], column_filter, x_filter, low = low_filter)
            st.session_state.filtering = True
            st.session_state.filtered_df = filtered_df
            st.rerun()
    except KeyError:
        st.sidebar.warning("Находится в разработке", icon="⚠️")

st.sidebar.title("Другое")
other = st.sidebar.selectbox("", (["Не выбрано", "Посмотреть логи"])) #, "Добавить предмет"

# Создает предмет, новую таблицу можно посмотреть, ломает таблицы "Все предметы", "Данные студента", "Данные по группам" до перезапуска streamlit
# if other == "Добавить предмет":
#     name_subject = st.sidebar.text_input("Название предмета")
#     if st.sidebar.button("Добавить предмет"):
#         with open("subjects.txt", "a", encoding="utf-8") as file:
#             file.write(f"{name_subject}\n")
#         subjects, list_subjects, list_groups = load_subjects()
#         save_subjects(subjects)
#         st.session_state.subjects = subjects
#         write_log("Добавить новый предмет", f"Предмет = {name_subject}") # log
#         st.success(f"Таблица для предмета {name_subject} успешно создан!", icon="✅")
#         time.sleep(1)
#         st.rerun()

if other == "Посмотреть логи":
    with open("logs.log", "r", encoding="utf-8") as file:
        logs = file.readlines()
    if st.sidebar.button("Посмотреть логи"):
        st.header("История логов")
        for log in logs:
            st.write(log)

save_subjects(subjects)