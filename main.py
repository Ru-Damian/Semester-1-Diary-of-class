import pandas as pd
import numpy as np
import functions as func

list_subjects = ["Русский язык", "Математика", "История", "Физика", "Химия"]
list_students = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH", "III", "JJJ"]
list_groups = np.random.randint(1, 5, len(list_students))

subjects = dict()
for subject in list_subjects:
    subjects[subject] = func.create_df_subject(list_students, list_groups)

print(subjects["Химия"])