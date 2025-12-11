import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import functions.init as func
import time
import io

def write_log(action:str, info:str) -> None:
    """
    Записывает лог в файл logs.log
    
    :param action: Действие, которое было сделано
    :type action: str
    :param info: Детали того действия, которое произошло
    :type info: str
    """
    with open("logs.log", "a", encoding="utf-8") as file:
        file.write(f"{time.strftime('[%d-%m-%Y %H:%M:%S]')} {action}: {info}\n")

def write_students(id:int, name:str, group:int, action:str = "add") -> None:
    """
    Сохраняет добавление или удаление студента в файле student.txt
    
    :param id: ID студента, которого добавляют или удаляют из файла students.txt
    :type id: int
    :param name: ФИО студента, которого добавляют или удаляют из файла students.txt
    :type name: str
    :param group: Номер группы студента, которого добавляют или удаляют из файла students.txt
    :type group: int
    :param action: Значение "add" активирует добавление студента, значение "remove" -- удаление студента
    :type action: str
    """
    student = f"{str(id)};{name};{str(group)}\n"
    if action == "add":
        with open("students.txt", "a", encoding="utf-8") as file:
            file.write(student)
    if action == "remove":
        with open("students.txt", "r", encoding="utf-8") as file:
            students = [line for line in file.readlines() if line != student]
        with open("students.txt", "w", encoding="utf-8") as file:
            file.writelines(students)

def write_changes_students(id, df_student):
    """
    Сохраняет изменения ФИО студента и/или номера группы в файле student.txt
    
    :param id: ID студента, чьи ФИО и/или группа изменились
    :param df_student: Description
    """
    name = func.default_processing_text_input(df_student["Студент"].iloc[0], is_full_name=True, output="text_input")
    group = df_student["Группа"].iloc[0]
    with open("students.txt", "r", encoding="utf-8") as file:
        students = [f"{id};{name};{group}\n" if line.split(";")[0] == str(id) else line for line in file.readlines()]
    with open("students.txt", "w", encoding="utf-8") as file:
        file.writelines(students)

def load_subjects() -> tuple[dict[str, pd.DataFrame], list[str], list[int], bool]:
    """
    Выгружает список предметов из subjects.txt. Создает словарь {название предмета:pd.Dataframe}.
    pd.Dataframe создается из файла .csv, если такого нет используется func.create_df_subject(), а данные для нее берутся из "students.txt".
    
    :return: Словарь {название предмета:таблица предмета}, массив с названием всех предметов, массив с номерами всех групп, флаг, который указывает создавались ли новые таблицы
    :rtype: tuple[dict[str, pd.DataFrame], list[str], list[int], bool]
    """
    with open("subjects.txt", "r", encoding="utf-8") as file:
        list_subjects = [s.strip() for s in file]
    subjects = dict()
    creating_subject = False
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
            creating_subject = True
            write_log("Создать таблицу предмета", f"Предмет = {subject}") # log
    list_groups = sorted(set(subjects[list_subjects[0]]["Группа"].to_list()))
    return subjects, list_subjects, list_groups, creating_subject

def save_subjects(subjects:dict[str, pd.DataFrame]) -> None:
    """
    Сохраняет все pd.DataFrames из словаря subjects по файлам .csv.
    
    :param subjects: Словарь {название предмета:таблица предмета} со всеми таблицами предметов
    :type subjects: dict[str, pd.DataFrame]
    """
    for subject, df_subject in subjects.items():
        df_subject.to_csv(f"{subject}.csv")

def save_info_student(id:int, df_student:pd.DataFrame, df_marks:pd.DataFrame) -> None:
    """
    Сохраняет изменения в df_student и df_marks во все таблицы предметов.
    
    :param id: ID студента, чьи оценки были изменены
    :type id: int
    :param df_student: pd.Dataframe с ФИО студента и номером группы
    :type df_student: pd.DataFrame
    :param df_marks: pd.Dataframe с оценками студента по всем предметам
    :type df_marks: pd.DataFrame
    """
    for subject, df_subject in subjects.items():
        df_subject.loc[id, "Студент"] = func.default_processing_text_input(df_student["Студент"].iloc[0], is_full_name=True, output="text_input")
        df_subject.loc[id, "Группа"] = df_student["Группа"].iloc[0]
        new_marks_row = df_marks.loc[subject, df_subject.columns[2:]]
        df_subject.loc[id, df_subject.columns[2]:] = new_marks_row
        df_subject = func.count_mean_mark(df_subject)
    save_subjects(subjects)

def make_non_editable_column_config(df:pd.DataFrame, non_editable_columns:list[str], index:any = "ID", block_index:bool = True) -> dict[str, dict]:
    """
    Создает column_config с блоком на редактирование столбцов из non_editable_columns для st.data_editor.
    
    :param df: pd.DataFrame, для которого нужно создать column_config
    :type df: pd.DataFrame
    :param non_editable_columns: Массив из названий столбцов, которым нужно установить блок на редактирование
    :type non_editable_columns: list[str]
    :param index: Название столбца индексов
    :type index: any
    :param block_index: True -- блокировать индексы, False -- не блокировать индексы
    :type block_index: bool
    :return: готовый column_config для st.data_editor
    :rtype: dict[str, dict]
    """
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

def edit_button(flag_key:str) -> None:
    """
    Создает кнопку, которая меняет st.session_state[flag_key] на True
    
    :param flag_key: Ключ к флагу, который сохранен в st.session_state
    :type flag_key: str
    """
    if st.button("Редактировать"):
        st.session_state[flag_key] = True
        write_log("Редактировать", f"Предмет = {name_table}") # log
        st.rerun()

def show_filtered_subject_table() -> None:
    """
    Отображает отфильтрованный pd.dataframe и создает кнопку, чтобы вернуть исходный pd.dataframe.
    """
    filtered_df_subject = st.session_state.filtered_df_subject
    filtered_cnt_row = st.session_state.filtered_cnt_row
    word_ending = "ов"
    if str(filtered_cnt_row)[-1] in ("2", "3", "4"):
        word_ending = "а"
    elif str(filtered_cnt_row)[-1] == "1":
        word_ending = ""
    st.dataframe(filtered_df_subject)
    st.write(f"Подходит {filtered_cnt_row} студент{word_ending}")
    if st.button("Сбросить"):
        st.session_state.filtering_subject = False
        st.rerun()

def show_edited_subject_table(subjects:dict[str, pd.Dataframe], subject:str) -> None:
    """
    Отображает редактируемый pd.dataframe через st.data_editor и создает кнопку, чтобы сохранить измения в pd.dataframe.
    
    :param subjects: Словарь {название предмета:таблица предмета} со всеми таблицами предметов
    :type subjects: dict[str, pd.Dataframe]
    :param subject: Название предмета, таблицу которого нужно отредактировать
    :type subject: str
    """
    config_edited_subject = make_non_editable_column_config(subjects[subject], ["Студент", "Группа", "Средняя оценка"])
    edited_df_subject = st.data_editor(subjects[subject], num_rows="fixed", column_config=config_edited_subject)
    edited_df_subject = func.count_mean_mark(edited_df_subject)
    if st.button("Сохранить изменения"):
        time.sleep(0.1)
        subjects[subject] = edited_df_subject
        save_subjects(subjects)
        st.session_state.editing_subject = False
        write_log("Сохранить", f"Предмет = {subject}") # log
        st.success("Изменения сохранены!", icon="✅")
        time.sleep(1)
        st.rerun()

def show_subject_table(subjects:dict[str, pd.Dataframe], subject:str) -> None:
    """
    Создает флаги состояний. 
    st.session_state.filtering_subject == True -> вызывает show_filtered_subject_table()
    st.session_state.editing_subject == True -> вызывает show_edited_subject_table()
    Если оба флага не активны, то отбражается pd.Dataframe с кнопками "Редактировать" и "Скачать"
    
    :param subjects: Словарь {название предмета:таблица предмета} со всеми таблицами предметов
    :type subjects: dict[str, pd.Dataframe]
    :param subject: Название предмета, таблицу которого нужно показать
    :type subject: str
    """""
    if "filtering_subject" not in st.session_state:
        st.session_state.filtering_subject = False
    if "editing_subject" not in st.session_state:
        st.session_state.editing_subject = False
    st.write(subject)
    if st.session_state.filtering_subject:
        show_filtered_subject_table()
    elif st.session_state.editing_subject:
        show_edited_subject_table(subjects, subject)
    else:
        st.dataframe(subjects[subject])
        edit_button("editing_subject")
        st.download_button("Скачать", subjects[subject].to_csv().encode("utf-8"), f"{subject}.csv")

def show_edited_info_student_table(subjects:dict[str, pd.Dataframe], id_student:int) -> None:
    """
    Отображает редактируемый pd.dataframe через st.data_editor и создает кнопку, чтобы сохранить измения в pd.dataframe.
    
    :param subjects: Словарь {название предмета:таблица предмета} со всеми таблицами предметов
    :type subjects: dict[str, pd.Dataframe]
    :param id_student: ID студента, таблицы которого нужно отредактировать
    :type id_student: int
    """
    df_student, df_marks = func.info_student(subjects, id_student)
    st.write("Данные студента")
    config_edited_df_student = make_non_editable_column_config(df_student, ["Средний балл", "Посещаемость"])
    config_edited_df_student["Студент"] = st.column_config.TextColumn(
        "Студент", max_chars=50, validate=r"^\s*[А-ЯЁа-яё]+(?:-[А-ЯЁа-яё]+)*(?:\s+[А-ЯЁа-яё]+(?:-[А-ЯЁа-яё]+)*){1,2}\s*$",
        help="ФИО студента: минимум 2 слова; максимум 3 слова(можно соединять с помощью \"-\"); символы русского алфавита и \"-\"; \"-\" не должен стоять в начале или в конце слова"
        )
    config_edited_df_student["Группа"] = st.column_config.NumberColumn("Группа", min_value=1, max_value=15)
    edited_df_student = st.data_editor(df_student, num_rows="fixed", column_config=config_edited_df_student)
    st.write("Оценки по предметам")
    config_edited_df_marks = make_non_editable_column_config(df_marks, ["Средняя оценка"], index="Предмет")
    edited_df_marks = st.data_editor(df_marks, num_rows="fixed", column_config=config_edited_df_marks)
    edited_df_marks = func.count_mean_mark(edited_df_marks)
    if st.button("Сохранить изменения"):
        time.sleep(0.1)
        save_info_student(id_student, edited_df_student, edited_df_marks)
        write_changes_students(id_student, edited_df_student)
        st.session_state.editing_student = False
        st.success("Изменения сохранены!", icon="✅")
        time.sleep(1)
        st.rerun()

def show_info_student_table(subjects:dict[str, pd.Dataframe], id_student:int) -> None:
    """
    Создает флаг редактирования. 
    st.session_state.editing_student == True -> вызывает show_edited_info_student_table()
    Если флаг не активен, то отбражается pd.Dataframe с кнопкой "Редактировать"
    
    :param subjects: Словарь {название предмета:таблица предмета} со всеми таблицами предметов
    :type subjects: dict[str, pd.Dataframe]
    :param id_student: ID студента, таблицы которого нужно показать
    :type id_student: int
    """
    if "editing_student" not in st.session_state:
        st.session_state.editing_student = False
    if st.session_state.editing_student:
        show_edited_info_student_table(subjects, id_student)
    else:
        try:
            df_student, df_marks = func.info_student(subjects, id_student)
            st.write(name_table)
            st.dataframe(df_student)
            st.write("Оценки по предметам")
            st.dataframe(df_marks)
            edit_button("editing_student")
        except KeyError:
            st.warning("Студента с таким ID не существует", icon = "❌")

def check_text_input(flag_key:str, text_input:str, type_text_input:str, type_column:None|str = None, list_subject:None|list[str] = None) -> None|str:
    """
    Создает флаг в st.session_state. Выводит подсказку для исправления ввода | Возвращает изменный text_input.
    
    :param flag_key: Название флага, который будет создан в st.session_state
    :type flag_key: str
    :param text_input: Ввод, который нужно проверить через одну из функций
    :type text_input: str
    :param type_text_input: "full_name" -- для проверки ФИО | "title_column" -- для проверки названия столбца | "name_subject" -- для проверки названия предмета
    :type type_text_input: str
    :param type_column: "mark" | "other". Параметр необходимый для проверки названия нового столбца.
    :type type_column: None | str
    :param list_subject: Список предметов, для проверки названия нового предмета
    :type list_subject: None | list[str]
    :return: Подсказка, если ввод некорректен | Изменный text_input
    :rtype: str | None
    """
    if flag_key not in st.session_state:
        st.session_state[flag_key] = False
    if "Error:" not in func.check_text_input(text_input, type_text_input, type_column, list_subject):
        text_input = func.check_text_input(text_input, type_text_input, type_column, list_subject)
        st.session_state[flag_key] = True
        return text_input
    else:
        st.sidebar.warning(func.check_text_input(text_input, type_text_input, type_column, list_subject)[6:], icon = "❌")
        st.session_state[flag_key] = False

def add_column_by_target(subjects:dict[str, pd.Dataframe], target:str, title_column:str, type_column:None|str = None, subject:None|str = None) -> bool:
    """
    Добавляет столбец к одному предмету или ко всем.
    
    :param subjects: Словарь {название предмета:таблица предмета} со всеми таблицами предметов
    :type subjects: dict[str, pd.Dataframe]
    :param target: "one" -- добавляет столбец к одному предмету | "all" -- добавляет столбец ко всем предметам 
    :type target: str
    :param title_column: Название нового столбца
    :type title_column: str
    :param type_column: "mark" -- создает столбец для оценки перед "Средняя оценка" | None -- создает столбец в конце таблицы
    :type type_column: str
    :param subject: None при target = "all" | Название предмета при target = "one"
    :type subject: None|str
    :return: True, если был(и) создан(ы) столбцы | False, если столбец с таким названием уже существует(в конкретной таблице | во всех таблицах)
    :rtype: bool
    """
    place = "before" if type_column == "mark" else "end"
    if target == "one":
        if title_column not in subjects[subject].columns:
            func.add_column(subjects[subject], title_column, place=place)
        else:
            st.sidebar.warning("Столбец с таким названием уже существует", icon = "❌")
            return False
    if target == "all":
        cnt_subjects = len(subjects)
        cnt_is = 0
        for df_subject in subjects.values():
            if title_column not in df_subject.columns:
                func.add_column(df_subject, title_column, place=place)
            else:
                cnt_is += 1
                if cnt_is == cnt_subjects:
                    st.sidebar.warning("Столбец с таким названием уже существует", icon = "❌")
                    return False
    return True

subjects, list_subjects, list_groups, creating_subject = load_subjects()

# Если была создана новая таблица, обновляет страницу, чтобы не было ошибок
if creating_subject:
    save_subjects(subjects)
    creating_subject = False
    st.rerun()

if "subjects" not in st.session_state:
    st.session_state.subjects = subjects
subjects = st.session_state.subjects
st.set_page_config(layout="wide")


# Таблицы
st.sidebar.title("Таблицы")
name_table = st.sidebar.selectbox(" ", (["Все предметы", "Данные студента", "Данные по группам"] + list_subjects))

if name_table in list_subjects:
    show_subject_table(subjects, name_table)
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
        show_info_student_table(subjects, id_student)
else:
    st.session_state.clicking_student = False
    st.session_state.editing_student = False

if name_table == "Данные по группам":
    st.write(name_table)
    df_groups = func.info_groups(subjects, list_groups)
    st.dataframe(df_groups)
    st.download_button("Скачать", df_groups.to_csv().encode("utf-8"), f"{name_table}.csv")
    for i in range(3): st.write(" ")
    # Графики средних баллов по предмету по группам
    st.write("Средний балл по предмету по группам")
    name_graph_group_mean = st.radio(" ", ["Все предметы"] + list_subjects, horizontal=True)
    fig, ax = plt.subplots(figsize=(8, 3))
    if name_graph_group_mean != "Все предметы":
        df_groups[name_graph_group_mean].plot.bar(ax=ax, color = "salmon")
        ax.set_title(f"Средний балл по предмету: {name_graph_group_mean}")
    else:
        df_groups["Средний балл"].plot.bar(ax=ax, color = "salmon")
        ax.set_title(f"Средний балл по всем предметам")
    ax.set_xlabel("Группы")
    ax.set_ylabel("Средний балл")
    ax.grid(axis='y', linestyle='-.', alpha=0.7)
    fig.tight_layout()
    st.pyplot(fig, width=1000)
    buf_graph_group_mean = io.BytesIO()
    fig.savefig(buf_graph_group_mean, format="png", bbox_inches="tight")
    buf_graph_group_mean.seek(0)
    st.download_button("Скачать график", buf_graph_group_mean, f"Группа. Средние баллы. Предмет - {name_graph_group_mean}.png")
    plt.close(fig)
    for i in range(3): st.write(" ")
    # Графики сложности предметов для групп
    st.write(f"Сложность предметов по группам")
    name_graph_group_difficulty = st.radio(" ", ["Все группы"] + list(map(str, list_groups)), horizontal=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    if name_graph_group_difficulty != "Все группы":
        df_groups.loc[int(name_graph_group_difficulty), :list_subjects[-1]].plot(ax=ax, marker = "o", color = "turquoise")
        ax.set_title(f"Средний балл предметов для группы {name_graph_group_difficulty}")
    else:
        df_groups.iloc[:, :-2].mean(axis=0).plot(ax=ax, marker = "o", color = "turquoise")
        ax.set_title(f"Средний балл по всем группам")
    ax.set_xlabel("Предметы")
    ax.set_ylabel("Средний балл")
    ax.grid(axis='y', linestyle='-.', alpha=0.7)
    ax.set_xticks(range(len(list_subjects)))
    ax.set_xticklabels(list_subjects, rotation=45, ha="right")
    fig.tight_layout()
    st.pyplot(fig, width=1000)
    buf_graph_group_difficulty = io.BytesIO()
    fig.savefig(buf_graph_group_difficulty, format="png", bbox_inches="tight")
    buf_graph_group_difficulty.seek(0)
    st.download_button("Скачать график", buf_graph_group_difficulty, f"Группа. Сложность предметов. Группа - {name_graph_group_difficulty}.png")
    plt.close(fig)


# Действия
actions = ["Добавить столбец", "Добавить студента", "Удалить студента"]
if name_table in list_subjects:
    actions = ["Отфильтровать"] + actions

st.sidebar.title("Действия")
action = st.sidebar.selectbox(" ", (["Не выбрано"] + actions))

if action == "Добавить студента":
    st.sidebar.subheader("Добавить студента")
    full_name_student = st.sidebar.text_input("ФИО студента", max_chars = 50, value = "Петров Иван Сергеевич", placeholder = "Петров Иван Сергеевич")
    group_student = st.sidebar.number_input("Группа", value = 1, min_value = 1, max_value = 15)
    full_name_student = check_text_input("checked_full_name_student", full_name_student, "full_name")
    if st.sidebar.button("Добавить студента") and st.session_state["checked_full_name_student"]:
        id_student = func.add_student(subjects, full_name_student, group_student)
        save_subjects(subjects)
        write_students(id_student, full_name_student, group_student)
        write_log(action, f"ФИО = {full_name_student}, Группа = {group_student}") # log
        st.success(f"Студент {full_name_student} ({group_student}) успешно добавлен!", icon="✅")
        time.sleep(1)
        st.rerun()

if action == "Удалить студента":
    st.sidebar.subheader("Удалить студента")
    id_student = st.sidebar.number_input("ID студента", value = 1000, min_value=1000)
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
    if name_table in list_subjects:
        st.sidebar.write(f"(к таблице \"{name_table}\")")
        target = "one"
        subject = name_table
    else:
        st.sidebar.write("(ко всем предметам)")
        target = "all"
        subject = None
    title_column = st.sidebar.text_input("Название", max_chars = 20)
    type_column = st.sidebar.selectbox("Тип столбца", ("Для оценки", "Другое"))
    type_column = "mark" if type_column == "Для оценки" else None
    title_column = check_text_input("checked_title_column", title_column, "title_column", type_column=type_column)
    if st.sidebar.button("Добавить столбец") and st.session_state["checked_title_column"] and add_column_by_target(subjects, target, title_column, type_column=type_column, subject=subject):
        save_subjects(subjects)
        write_log(action, f"Название = {title_column}, Тип столбца = {type_column}") # log
        st.success(f"Столбец {title_column} успешно создан!", icon="✅")
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
        st.session_state.filtered_cnt_row = filtered_cnt_row
        st.rerun()


# Другие действия
st.sidebar.title("Другое")
other = st.sidebar.selectbox(" ", (["Не выбрано", "Добавить предмет", "Посмотреть логи"]))

if other == "Добавить предмет":
    name_subject = st.sidebar.text_input("Название предмета")
    name_subject = check_text_input("checked_name_subject", name_subject, "name_subject", list_subject=list_subjects)
    if st.sidebar.button("Добавить предмет") and st.session_state["checked_name_subject"]:
        with open("subjects.txt", "a", encoding="utf-8") as file:
            file.write(f"{name_subject}\n")
        subjects, list_subjects, list_groups, creating_subject = load_subjects()
        save_subjects(subjects)
        st.session_state.subjects = subjects
        write_log("Добавить новый предмет", f"Предмет = {name_subject}") # log
        st.success(f"Таблица для предмета {name_subject} успешно создан!", icon="✅")
        time.sleep(1)
        st.rerun()

if other == "Посмотреть логи":
    with open("logs.log", "r", encoding="utf-8") as file:
        logs = file.readlines()[::-1]
    if st.sidebar.button("Посмотреть логи"):
        st.header("История логов")
        st.download_button("Скачать логи", "".join(logs[::-1]), "logs.log")
        for log in logs:
            st.write(log)

save_subjects(subjects)