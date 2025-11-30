def check_text_input(text, type_field = "fio"):
    if type_field == "fio":
        words = text.split(" ")
        if len(words) < 2:
            return "Error:Минимум 2 слова"
        if len(words) > 3:
            return "Error:Максимум 3 слова, можно соединить слова с помощью \"-\""
        ru_alf = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ-"
        for word in words:
            for letter in word.upper():
                if letter not in ru_alf:
                    return f"Error:{word.capitalize()} содержит буквы не из русского языка/ цифры / специалные символы"
                if letter == "-" and (letter == word[0] or letter == word[-1]):
                    return "Error:\"-\" не может быть в начале или в конце слова"
        fio = words[0].capitalize()
        for i in range(1, len(words)):
            fio += " " + words[i].capitalize()
        return fio