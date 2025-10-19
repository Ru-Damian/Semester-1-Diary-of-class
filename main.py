import pandas as pd
import numpy as np
import functions as f

list_students = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH", "III", "JJJ"]
list_groups = np.random.randint(1, 5, len(list_students))

df_russian = f.create_df_subject(list_students, list_groups)
df_mathematics = f.create_df_subject(list_students, list_groups)
df_history = f.create_df_subject(list_students, list_groups)
df_physics = f.create_df_subject(list_students, list_groups)
df_chemistry = f.create_df_subject(list_students, list_groups)