import pandas as pd
import numpy as np
import functions as func

list_students = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH", "III", "JJJ"]
list_groups = np.random.randint(1, 5, len(list_students))

df_russian = func.create_df_subject(list_students, list_groups)
df_mathematics = func.create_df_subject(list_students, list_groups)
df_history = func.create_df_subject(list_students, list_groups)
df_physics = func.create_df_subject(list_students, list_groups)
df_chemistry = func.create_df_subject(list_students, list_groups)