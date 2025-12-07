import pandas as pd
import numpy as np

def add_student(subjects:dict[str, pd.DataFrame], name:str, group:int) -> int:
    """
    Добавление студента во всем таблицы предметов.
    
    :param subjects: Словарь {название предмета:таблица предмета} со всеми таблицами предметов
    :type subjects: dict[str, pd.DataFrame]
    :param name: ФИО нового студента
    :type name: str
    :param group: Номер группы нового студента
    :type group: int
    :return: ID, которое было присвоено новому студенту
    :rtype: int
    """
    id = np.nan
    for df_subject in subjects.values():
        if np.isnan(id):
            id = df_subject.index.tolist()[-1] + 1
        df_subject.loc[id] = [name, group] + [np.nan for p in range(df_subject.shape[1] - 2)]
    return id

def remove_student(subjects:dict[str, pd.DataFrame], id:int) -> tuple[str, int]:
    """
    Удаление студента из всех таблиц предметов.
    
    :param subjects: Словарь {название предмета:таблица предмета} со всеми таблицами предметов
    :type subjects: dict[str, pd.DataFrame]
    :param id: ID студента, которого нужно удалить
    :type id: int
    :return: ФИО и номер группы студента, который был удален
    :rtype: tuple[str, int]
    """
    name = ""
    group = 0
    for subject, df_subject in subjects.items():
        if name == "" or group == 0:
            name = df_subject.loc[id, "Студент"]
            group = df_subject.loc[id, "Группа"]
        subjects[subject] = df_subject.drop(id, axis=0)
    return name, group