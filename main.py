import pandas as pd
import numpy as np
import streamlit as st
import functions.init as func
import time

def write_log(action, info):
    with open("logs.log", "a", encoding="utf-8") as file:
        file.write(f"{time.strftime('[%Y-%m-%d %H:%M:%S]')} {action}: {info}\n")

def write_students(id, name, group, action = "add"):
    student = f"{str(id)};{name};{str(group)}\n"
    if action == "add":
        with open("students.txt", "a", encoding="utf-8") as file:
            file.write(student)
    if action == "remove":
        with open("students.txt", "r", encoding="utf-8") as file:
            students = [line for line in file.readlines() if line != student]
        with open("students.txt", "w", encoding="utf-8") as file:
            file.writelines(students)

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
                        list_id.append(int(id))
                        list_students.append(fio)
                        list_groups.append(int(group))
                subjects[subject] = func.create_df_subject(list_id, list_students, list_groups)
            write_log("Создать таблицу предмета", f"Предмет = {subject}") # log
    list_groups = subjects[list_subjects[0]]["Группа"].to_list()
    return subjects, list_subjects, list_groups

def save_subjects(subjects):
    for subject, df_subject in subjects.items():
        df_subject.to_csv(f"{subject}.csv")

def save_info_student(id, df_marks):
    for subject, df_subject in subjects.items():
        new_student_row = df_marks.loc[subject, df_subject.columns[2:]]
        df_subject.loc[id, df_subject.columns[2]:] = new_student_row
        df_subject = func.count_mean_mark(df_subject)
    save_subjects(subjects)

def make_non_editable_column_config(df, non_editable_columns, index = "ID", block_index = True):
    config = dict()
    if block_index:
        if df.index.dtype in ['int64', 'float64']:
            config[index] = st.column_config.NumberColumn(index, disabled=True)
        else:
            config[index] = st.column_config.TextColumn(index, disabled=True)
    for col in df.columns:
        if col in non_editable_columns:
            if df[col].dtype in ['int64', 'float64']:
                config[col] = st.column_config.NumberColumn(col, disabled=True)
            else:
                config[col] = st.column_config.TextColumn(col, disabled=True)
        else:
            if df[col].dtype in ['int64', 'float64']:
                config[col] = st.column_config.NumberColumn(col, min_value=0, max_value=100)
            else:
                config[col] = st.column_config.TextColumn(col, max_chars=50)
    return config

def edit_button(edit_key):
    if st.button("Редактировать"):
        st.session_state[edit_key] = True
        write_log("Редактировать", f"Предмет = {name_table}") # log
        st.rerun()

def show_filtered_subject_table():
    filtered_df_subject = st.session_state.filtered_df_subject
    st.dataframe(filtered_df_subject)
    if st.button("Сбросить"):
        st.session_state.filtering_subject = False
        st.rerun()

def show_edited_subject_table(name_table):
    config_edited_subject = make_non_editable_column_config(subjects[name_table], ["Студент", "Группа", "Средняя оценка"])
    edited_df_subject = st.data_editor(subjects[name_table], num_rows="fixed", column_config=config_edited_subject)
    edited_df_subject = func.count_mean_mark(edited_df_subject)
    if st.button("Сохранить изменения"):
        time.sleep(0.1)
        subjects[name_table] = edited_df_subject
        save_subjects(subjects)
        st.session_state.editing_subject = False
        write_log("Сохранить", f"Предмет = {name_table}") # log
        st.success("Изменения сохранены!", icon="✅")
        time.sleep(1)
        st.rerun()

def show_subject_table(name_table):
    if "filtering_subject" not in st.session_state:
        st.session_state.filtering_subject = False
    if "editing_subject" not in st.session_state:
        st.session_state.editing_subject = False
    st.write(name_table)
    if st.session_state.filtering_subject:
        show_filtered_subject_table()
    elif st.session_state.editing_subject:
        show_edited_subject_table(name_table)
    else:
        st.dataframe(subjects[name_table])
        edit_button("editing_subject")
        st.download_button("Скачать", subjects[name_table].to_csv().encode("utf-8"), f"{name_table}.csv")

def show_edited_info_student_table(id):
    df_student, df_marks = func.info_student(subjects, id)
    st.write(name_table)
    st.dataframe(df_student)
    # config_edited_df_student = make_non_editable_column_config(df_student, ["Средний балл", "Посещаемость"])
    # edited_df_student = st.data_editor(df_student, num_rows="fixed", column_config=config_edited_df_student)
    st.write("Оценки по предметам")
    config_edited_df_marks = make_non_editable_column_config(df_marks, ["Средняя оценка"], index="Предмет")
    edited_df_marks = st.data_editor(df_marks, num_rows="fixed", column_config=config_edited_df_marks)
    edited_df_marks = func.count_mean_mark(edited_df_marks)
    if st.button("Сохранить изменения"):
        time.sleep(0.1)
        save_info_student(id, edited_df_marks)
        st.session_state.editing_student = False
        write_log("Сохранить", f"Предмет = {name_table}") # log
        st.success("Изменения сохранены!", icon="✅")
        time.sleep(1)
        st.rerun()

def show_info_student_table(id):
    if "editing_student" not in st.session_state:
        st.session_state.editing_student = False
    if st.session_state.editing_student:
        show_edited_info_student_table(id)
    else:
        try:
            df_student, df_marks = func.info_student(subjects, id)
            st.write(name_table)
            st.dataframe(df_student)
            st.write("Оценки по предметам")
            st.dataframe(df_marks)
            edit_button("editing_student")
        except KeyError:
            st.warning("Студента с таким ID не существует", icon = "❌")

subjects, list_subjects, list_groups = load_subjects()

if "subjects" not in st.session_state:
    st.session_state.subjects = subjects
subjects = st.session_state.subjects
st.set_page_config(layout="wide")


# Таблицы
st.sidebar.title("Таблицы")
name_table = st.sidebar.selectbox(" ", (["Все предметы", "Данные студента", "Данные по группам"] + list_subjects))

if name_table in list_subjects:
    show_subject_table(name_table)
else:
    st.session_state.editing_subject = False
    st.session_state.filtering_subject = False

if name_table == "Все предметы":
    st.write(name_table)
    df_all_subjects = func.info_subjects(subjects)
    st.dataframe(df_all_subjects)
    st.download_button("Скачать", df_all_subjects.to_csv().encode("utf-8"), f"{name_table}.csv")

if name_table == "Данные студента":
    st.write("Все предметы")
    st.dataframe(func.info_subjects(subjects))
    id_student = st.sidebar.number_input("ID студента", value=1001, min_value=1001)
    if "clicking_student" not in st.session_state:
        st.session_state.clicking_student = False
    if st.sidebar.button("Получить данные") or st.session_state.clicking_student:
        st.session_state.clicking_student = True
        show_info_student_table(id_student)
else:
    st.session_state.clicking_student = False
    st.session_state.editing_student = False

if name_table == "Данные по группам":
    st.write(name_table)
    df_groups = func.info_groups(subjects, list_groups)
    st.dataframe(df_groups)
    st.download_button("Скачать", df_groups.to_csv().encode("utf-8"), f"{name_table}.csv")


# Действия
actions = ["Добавить студента", "Удалить студента"]
if name_table in list_subjects:
    actions = ["Отфильтровать"] + actions + ["Добавить столбец"]

st.sidebar.title("Действия")
action = st.sidebar.selectbox(" ", (["Не выбрано"] + actions))

if action == "Добавить студента":
    st.sidebar.subheader("Добавить студента")
    name = st.sidebar.text_input("ФИО студента", max_chars = 50, value = "Петров Иван Сергеевич", placeholder = "Петров Иван Сергеевич")
    group = st.sidebar.number_input("Группа", value = 1, min_value = 1, max_value = 15)

    if "checking" not in st.session_state:
        st.session_state.checking = False
    
    if "Error:" not in func.check_fio_input(name):
        name = func.check_fio_input(name)
        st.session_state.checking = True
    else:
        st.sidebar.warning(func.check_fio_input(name)[6:], icon = "❌")
        st.session_state.checking = False
    
    if st.sidebar.button("Добавить студента") and st.session_state.checking:
        id_student = func.add_student(subjects, name, group)
        save_subjects(subjects)
        write_students(id_student, name, group)
        write_log(action, f"ФИО = {name}, Группа = {group}") # log
        st.success(f"Студент {name} ({group}) успешно добавлен!", icon="✅")
        time.sleep(1)
        st.rerun()

if action == "Удалить студента":
    st.sidebar.subheader("Удалить студента")
    id_student = st.sidebar.number_input("ID студента", value = 1002, min_value=1001)
    if st.sidebar.button("Удалить студента"):
        try:
            name, group = func.remove_student(subjects, id_student)
            save_subjects(subjects)
            write_students(id_student, name, group, action = "remove")
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
            title = func.check_title_column_input(title)
            func.add_column(subjects[name_table], title)
        else:
            title = func.check_title_column_input(title, type_column="other")
            func.add_column(subjects[name_table], title, place="end")
        save_subjects(subjects)
        write_log(action, f"Название = {title}, Тип столбца = {type_column}") # log
        st.success(f"Столбец {title} успешно создан!", icon="✅")
        time.sleep(1)
        st.rerun()

if action == "Отфильтровать":
    st.sidebar.subheader("Параметры фильтра")
    column_filter = st.sidebar.selectbox("Столбец для фильтрации", (subjects[name_table].columns[2:]))
    x_filter = st.sidebar.slider(f"{column_filter} > значения", value=50, min_value=10, max_value=90)
    low_filter = st.sidebar.checkbox(f"{column_filter} < значения")
    if st.sidebar.button("Показать результат"):
        st.write(name_table)
        filtered_df_subject, filtered_cnt_row = func.filter_df_column(subjects[name_table], column_filter, x_filter, low = low_filter)
        st.session_state.filtering_subject = True
        st.session_state.filtered_df_subject = filtered_df_subject
        st.rerun()


# Другие действия
st.sidebar.title("Другое")
other = st.sidebar.selectbox(" ", (["Не выбрано", "Добавить предмет", "Посмотреть логи"]))

if other == "Добавить предмет":
    name_subject = st.sidebar.text_input("Название предмета")
    if st.sidebar.button("Добавить предмет"):
        with open("subjects.txt", "a", encoding="utf-8") as file:
            file.write(f"{name_subject}\n")
        subjects, list_subjects, list_groups = load_subjects()
        save_subjects(subjects)
        st.session_state.subjects = subjects
        write_log("Добавить новый предмет", f"Предмет = {name_subject}") # log
        st.success(f"Таблица для предмета {name_subject} успешно создан!", icon="✅")
        time.sleep(1)
        st.rerun()

if other == "Посмотреть логи":
    with open("logs.log", "r", encoding="utf-8") as file:
        logs = file.readlines()
    if st.sidebar.button("Посмотреть логи"):
        st.header("История логов")
        for log in logs:
            st.write(log)

save_subjects(subjects)