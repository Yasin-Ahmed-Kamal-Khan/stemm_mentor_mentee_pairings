from mentor_mentee_classes import *
from auto_pairer import *
import pandas as pd
import os

def get_new_mentor_mentees(updated_mentors_df, updated_mentees_df):
    old_mentors_df = pd.read_csv(os.path.join('csvs', 'mentors.csv'))
    old_mentees_df = pd.read_csv(os.path.join('csvs', 'mentees.csv'))

    new_mentors_df = updated_mentors_df.merge(old_mentors_df, how='outer', indicator=True)
    new_mentors_df['current_student_numbers'] = 0

    return (pd.concat(new_mentors_df, old_mentors_df),
            updated_mentees_df.merge(old_mentees_df, how='outer', indicator=True))
    

if __name__ == "__main__":
    updated_mentors_df, updated_mentees_df = get_mentor_mentee_dfs(
        "spreadsheet_id.txt", "Form responses 1", "Form responses 2"
    )

    make_csvs(updated_mentors_df, updated_mentees_df)
    mentor_list = MentorList(os.path.join("csvs", "mentors.csv"))
    for row in updated_mentees_df.itertuples():
        if pd.notna(row):
            mentor_list.pair_mentee(Mentee(row))

    mentor_list.make_mentor_mentee_json()
