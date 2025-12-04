def check_fio_input(fio:str):
    """
    Docstring for write_log
    
    :param fio: Description
    :param info: Description
    Проверка ввода fio на соответсвие требованиям: кол-во слов, длина слов, символы из correct_alf.
    Если fio соответствует требованиям, то возращает fio, где каждое слово начинает с заглавной буквы, а все остальные -- строчные.
    Если есть ошибки, то возвращает подсказка, как исправить fio.
    """
    words = fio.split(" ")
    if len(words) < 2:
        return "Error:Минимум 2 слова"
    if len(words) > 3:
        return "Error:Максимум 3 слова, можно соединить слова с помощью \"-\""
    correct_alf = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ-"
    for word in words:
        for letter in word.upper():
            if letter not in correct_alf:
                return f"Error:{word.capitalize()} содержит буквы не из русского языка/ цифры / специалные символы"
            if letter == "-" and (letter == word[0] or letter == word[-1]):
                return "Error:\"-\" не может быть в начале или в конце слова"
    fio = words[0].capitalize()
    for i in range(1, len(words)):
        fio += " " + words[i].capitalize()
    return fio

def check_title_column_input(title_column, type_column = "mark"):
    """
    Проверка ввода title_column.
    Убирает все вхождения "Оценка" и все пробелы в начале названия.
    Если type_column = "mark" в начало названия столбца ставится "Оценка ".
    Возвращает измененное title_column, где первое слово начинается с заглавной буквы.
    """
    title_column = title_column.upper().replace("ОЦЕНКА", "")
    while title_column[0] == " ":
        title_column = title_column.upper().replace(" ", "", 1)
    if type_column == "mark":
        title_column = "Оценка " + title_column.lower()
    if type_column == "other":
        title_column = title_column.capitalize()
        print(title_column)
    return title_column