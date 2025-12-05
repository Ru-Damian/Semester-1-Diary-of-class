nums = "0123456789"
ru_alf = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
special_symbs = "-"

def check_full_name_input(full_name:str):
    """
    Проверка ввода full_name на соответсвие требованиям: кол-во слов, символы из correct_alf.
    Если full_name соответствует требованиям, то возращает full_name, где каждое слово начинает с заглавной буквы, а все остальные -- строчные.
    Если есть ошибки, то возвращает подсказка, как исправить full_name.
    """
    words = [word for word in full_name.split(" ") if word != ""]
    if len(words) < 2:
        return "Error:Минимум 2 слова"
    if len(words) > 3:
        return "Error:Максимум 3 слова, можно соединить слова с помощью \"-\""
    correct_alf = ru_alf + special_symbs
    for word in words:
        for letter in word.upper():
            if letter not in correct_alf:
                return f"Error:{word.capitalize()} содержит буквы не из русского языка / цифры / специальные символы"
            if letter == "-" and (letter == word[0] or letter == word[-1]):
                return "Error:\"-\" не может быть в начале или в конце слова"
    full_name = words[0].capitalize()
    for i in range(1, len(words)):
        full_name += " " + words[i].capitalize()
    return full_name

def check_title_column_input(title_column, type_column = "mark"):
    """
    Проверка ввода title_column.
    Убирает все вхождения "Оценка" и все пробелы в начале названия.
    Если type_column = "mark" в начало названия столбца ставится "Оценка ".
    Возвращает подсказки, если что-то введено неправильно.
    Инача возвращает измененное title_column, где первое слово начинается с заглавной буквы.
    """
    if title_column == "" or (len(set(title_column)) == 1 and title_column[0] == " "):
        return "Error:Пустое название столбца"
    correct_alf = ru_alf + nums
    for word in [_word for _word in title_column.split(" ") if _word != ""]:
        for symb in word.upper():
            if symb not in correct_alf:
                return f"Error:{word} содержит буквы не из русского языка / специальные символы"
    title_column = title_column.upper().replace("ОЦЕНКА", "")
    if title_column == "" or (len(set(title_column)) == 1 and title_column[0] == " "):
        return "Error:У вас пустое название, так как сочетание букв \"Оценка\" не может использоваться в название столбца (к столбцу с оценкой, автоматически добавится \"Оценка\")"
    while title_column[0] == " ":
        title_column = title_column.upper().replace(" ", "", 1)
    if type_column == "mark":
        title_column = "Оценка " + title_column.lower()
    if type_column == "other":
        title_column = title_column.capitalize()
    return title_column

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
    return result