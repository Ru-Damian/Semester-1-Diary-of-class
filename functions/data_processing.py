import pandas as pd
import numpy as np

def int_non_error_nan(data:int|float|np.Nan) -> int|np.Nan:
    """
    Переход из одного типа данных в другой: int|float -> int, np.Nan -> np.Nan
    
    :param data: Description
    :type data: int | float | np.Nan
    :return: int|float -> int | np.Nan -> np.Nan
    :rtype: int | np.Nan
    """
    if pd.isna(data):
        return data
    else:
        return int(data)

def count_mean_mark(df:pd.DataFrame, name_column:str = "Средняя оценка", output:str = "df") -> pd.DataFrame|pd.Series:
    """
    Считает среднюю оценку, беря оценки из столбцов перед столбцом name_column.
    
    :param df: pd.DataFrame, в котором нужно пересчитать среднюю оценку в столбце name_column
    :type df: pd.DataFrame
    :param name_column: Название столбца, который является столбцом для хранения средней оценки
    :type name_column: str
    :param output: "df" -- вернет pd.DataFrame | "col" -- вернет pd.Series с данными из столбца name_column
    :type output: str
    :return: pd.DataFrame|pd.Series, с подсчитанной средней оценкой
    :rtype: DataFrame | Series
    """
    id_mean = df.columns.get_loc(name_column)
    id_mark1 = ("Студент" in df.columns) + ("Группа" in df.columns) + ("Предмет" in df.columns)
    df[name_column] = list(map(int_non_error_nan, df.iloc[:, id_mark1:id_mean].mean(axis=1)))
    if output == "df":
        return df
    if output == "col":
        return df[name_column]

def create_df_subject(list_id:list[int], list_students:list[str], list_groups:list[int]) -> pd.DataFrame:
    """
    Создает таблицу предмета с синтетическими данными.
    
    :param list_id: Массив с последовательностью ID(ID -- студент)
    :type list_id: list[int]
    :param list_students: Массив с последовательностью ФИО(ФИО -- студент)
    :type list_students: list[str]
    :param list_groups: Массив с последовательностью номеров групп(номер группы -- студент)
    :type list_groups: list[int]
    :return: Таблица предмета с синтетическими данными
    :rtype: DataFrame
    """
    df_subject = pd.DataFrame({
        "ID": list_id,
        "Студент": list_students,
        "Группа": list_groups,
        "Оценка дз": np.random.randint(0, 101, len(list_students)),
        "Оценка проект": np.random.randint(0, 101, len(list_students)),
        "Оценка доклад": np.random.randint(0, 101, len(list_students)),
        "Средняя оценка": np.nan,
        "Посещаемость": np.random.randint(0, 101, len(list_students))
        })
    df_subject = df_subject.set_index("ID")
    df_subject["Средняя оценка"] = count_mean_mark(df_subject, output = "col")
    return df_subject

def filter_df_column(df_subject:pd.DataFrame, name_column:str, x:int|list[int], type_filter:str = "compare", low:bool = True) -> tuple[pd.DataFrame, int]:
    """
    Фильтрует таблицу предмета по столбцу name_column по значению x и подсчитывает количество подходящих студентов.
    
    :param df_subject: Таблица предмета, которую нужно отфильтровать
    :type df_subject: pd.DataFrame
    :param name_column: Название столбца, по которому будет происходить фильтрация
    :type name_column: str
    :param x: int, по которому будет фильтроваться name_column при type_filter = "compare"    |   int|list[int], по которому будет фильтроваться name_column при type_filter = "value"
    :type x: int | list[int]
    :param type_filter: "compare" -- оставляет студентов с name_column > или < значения x | "value" -- оставляет студентов со значениями name_column, которые совпадают со значениями в x
    :type type_filter: str
    :param low: True -- при type_filter = "compare" фильтрует name_column < x | False -- при type_filter = "value" фильтрует name_column > x
    :type low: bool
    :return: Отфильтрованный df_subject и кол-во подходящих студентов в нем
    :rtype: tuple[DataFrame, int]
    """
    if type_filter == "compare":
        if low:
            return df_subject[df_subject[name_column] < x], len(df_subject[df_subject[name_column] < x])
        return df_subject[df_subject[name_column] > x], len(df_subject[df_subject[name_column] > x])
    elif type_filter == "value":
        if type(x) != list():
            x = [x]
        return df_subject[df_subject[name_column].isin(x)], len(df_subject[df_subject[name_column].isin(x)])

def add_column(df:pd.DataFrame, title:str, auto_data:bool = False, place:str = "before", name_column_before:str = "Средняя оценка") -> pd.DataFrame:
    """
    Добавляет столбец к pd.DataFrame перед столбцом name_column_before или в конце таблице.
    
    :param df: pd.DataFrame, в который нужно добавить столбец
    :type df: pd.DataFrame
    :param title: Название нового столбца
    :type title: str
    :param auto_data: True -- заполняет столбец случайными числами от 0 до 100 | False -- заполняет столбец значением np.nan
    :type auto_data: bool
    :param place: "before" -- добавить столбец перед столбцом name_column_before | "end" -- добавить столбец в конец таблицы
    :type place: str
    :param name_column_before: Название столбца, перед которым нужно добавить столбец при place = "before"
    :type name_column_before: str
    :return: df, с добавленным столбцом
    :rtype: DataFrame
    """
    data = np.nan
    if auto_data:
        data = list(np.random.randint(0, 101, df.shape[0]))
    if place == "before":
        id_column = df.columns.get_loc(name_column_before)
        df.insert(loc=id_column, column=title, value=data)
    elif place == "end":
        df[title] = data
    return df

def remove_column(df:pd.DataFrame, title_column:str) -> pd.DataFrame:
    """
    Удаляет столбец с названием title_column из pd.DataFrame.
    
    :param df: pd.DataFrame, из которого нужно удалить столбец
    :type df: pd.DataFrame
    :param title_column: Название столбца, который нужно удалить
    :type title_column: str
    :return: Изменный df
    :rtype: DataFrame
    """
    df = df.drop(title_column, axis=1)
    return df

def replace_value(df:pd.DataFrame, name_column:str, id:int, value:int) -> None:
    """
    Поменять в df значение в ячейке df.loc[id, name_column] на value
    
    :param df: pd.DataFrame, в котором нужно поменять значение в ячейке
    :type df: pd.DataFrame
    :param name_column: Название столбца, где нужно поменять значение в ячейке
    :type name_column: str
    :param id: ID студента, у которого нужно поменять значение в ячейке
    :type id: int
    :param value: Новое значение, на которое будет произведена замена
    :type value: int
    """
    df_subject.loc[id, name_column] = value
    df_subject = count_mean_mark(df_subject)