import re

def default_processing_text_input(text_input:str, is_full_name:bool = False, output:str = "words") -> list[str]|str:
    if is_full_name:
        if output == "words":
            return ["-".join(subword.capitalize() for subword in word.split("-")) for word in text_input.strip().split(" ") if word != ""]
        if output == "text_input":
            return " ".join(["-".join(subword.capitalize() for subword in word.split("-")) for word in text_input.strip().split(" ") if word != ""])
    if output == "words":
        return [word.lower() for word in text_input.strip().split(" ") if word != ""]
    if output == "text_input":
        return " ".join([word.lower() for word in text_input.strip().split(" ") if word != ""])

def check_full_name_input(full_name:str):
    """
    Проверка ввода full_name на соответсвие требованиям: кол-во слов, символы из correct_alf.
    Если full_name соответствует требованиям, то возращает full_name, где каждое слово начинает с заглавной буквы, а все остальные -- строчные.
    Если есть ошибки, то возвращает подсказка, как исправить full_name.
    """
    words = default_processing_text_input(full_name, is_full_name = True)
    if len(words) < 2:
        return "Error:Минимум 2 слова"
    if len(words) > 3:
        return "Error:Максимум 3 слова, можно соединить слова с помощью \"-\""
    word_pattern = r"[а-яё]+(\-[а-яё]+)*"
    for word in words:
        if not re.fullmatch(rf"^{word_pattern}$", word, re.IGNORECASE):
            if re.search(r'--', word):
                return f"Error:\"{word}\" не может быть несколько подряд идущих \"-\""
            elif re.fullmatch(rf"^-{word_pattern}$|^{word_pattern}-$|^-{word_pattern}-$", word, re.IGNORECASE):
                return f"Error:\"{word}\": \"-\" не может быть в начале или в конце слова"
            else:
                return f"Error:\"{word}\" содержит буквы не из русского языка / цифры / специальные символы"
    full_name = " ".join(words)
    return full_name

def check_title_column_input(title_column, type_column = "mark"):
    """
    Проверка ввода title_column.
    Убирает все вхождения "Оценка" и все пробелы в начале названия.
    Если type_column = "mark" в начало названия столбца ставится "Оценка ".
    Возвращает подсказки, если что-то введено неправильно.
    Инача возвращает измененное title_column, где первое слово начинается с заглавной буквы.
    """
    words = default_processing_text_input(title_column)
    if not words:
        return "Error:Пустое название столбца"
    title_column = " ".join(words).replace("оценка", "").capitalize()
    if title_column == "":
        return "Error:У вас пустое название, так как сочетание букв \"Оценка\" не может использоваться в название столбца (к столбцу для оценки, автоматически добавится \"Оценка\")"
    word_pattern = r"[а-яё]+"
    num_pattern = r"[0-9]+"
    mixed_pattern = r"[а-яё0-9]+"
    for word in words:
        if not re.fullmatch(rf"^{word_pattern}$|^{num_pattern}$", word, re.IGNORECASE):
            if re.fullmatch(rf"^{mixed_pattern}$", word, re.IGNORECASE):
                return f"Error:В \"{word}\" смешены цифры и буквы(разделите их или что-то уберите)"
            else:
                return f"Error:\"{word}\" содержит буквы не из русского языка / специальные символы"
    if type_column == "mark":
        title_column = "Оценка " + title_column.lower()
    if type_column == "other":
        title_column = title_column.capitalize()
    return title_column

def check_name_subject_input(name_subject:str, list_subject:list[str]) -> str:
    """
    Проверяет name_subject на корректность ввода. Если есть проблемы, возвращает подсказку. Иначе возвращает изменный name_subject.
    
    :param name_subject: Название предмета, которое проверяем на корректность ввода
    :type name_subject: str
    :param list_subject: Список предметов, для исключения дублирования предметов
    :type list_subject: list[str]
    :return: Подсказка, если ввод некорректен | Изменный name_subject
    :rtype: str
    """
    words = default_processing_text_input(name_subject)
    if not words:
        return "Error:Пустое название предмета"
    name_subject = " ".join(words).capitalize()
    if name_subject in list_subject:
        return "Error:Таблица для этого предмета уже существует"
    word_pattern = r"[а-яё]+"
    for word in words:
        if not re.fullmatch(rf"^{word_pattern}$", word, re.IGNORECASE):
            return f"Error:\"{word}\" содержит буквы не из русского языка / цифры / специальные символы"
    return name_subject

def check_text_input(text_input:str, type_text_input:str, type_column:None|str = None, list_subject:None|list[str] = None) -> str:
    """
    Вилка для вызова одной из функций проверки текстого ввода.
    
    :param text_input: Ввод, который нужно проверить через одну из функций
    :type text_input: str
    :param type_text_input: "full_name" -- check_full_name_input() | "title_column" -- check_title_column_input() | "name_subject" -- check_name_subject_input()
    :type type_text_input: str
    :param type_column: Параметр необходимый для check_title_column_input()
    :type type_column: None | str
    :param list_subject: Параметр необходимый для check_name_subject_input()
    :type list_subject: None | list[str]
    :return: Подсказка, если ввод некорректен | Изменный text_input
    :rtype: str
    """
    if type_text_input == "full_name":
        result = check_full_name_input(text_input)
    if type_text_input == "title_column":
        result = check_title_column_input(text_input, type_column = type_column)
    if type_text_input == "name_subject":
        result = check_name_subject_input(text_input, list_subject)
    return result