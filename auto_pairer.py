import re
from posixpath import isdir
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from mentor_mentee_classes import *
medicine_pattern = r"(medicine|pharmacy|dent.*|law)"

def remove_medics(interested_courses):
    if pd.isna(interested_courses):
        return interested_courses
    
    return ','.join([course.strip() for course in interested_courses.split(',') if not re.match(medicine_pattern, course.strip(), flags=re.IGNORECASE)])

def get_mentor_mentee_dfs(spreadsheet, mentee_form_name, mentor_form_name):
    with open(spreadsheet, "r") as f:
        spreadsheet_id = f.read().strip()

    credentials = service_account.Credentials.from_service_account_file(
        "key.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=credentials)

    mentee_request = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=mentee_form_name)
    )
    mentee_data = mentee_request.execute().get("values", [])

    mentor_request = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=mentor_form_name)
    )
    mentor_data = mentor_request.execute().get("values", [])

    mentee_df = pd.DataFrame(mentee_data[1:], columns=mentee_data[0])
    mentor_df = pd.DataFrame(mentor_data[1:], columns=mentor_data[0])
    mentee_df.columns = [clean_text(col) for col in mentee_df.columns]
    mentor_df.columns = [clean_text(col) for col in mentor_df.columns]
   
    mentee_df['What_are_you_interested_in_studying_at_university_Select_all_that_you_may_be_interested_in'] = mentee_df['What_are_you_interested_in_studying_at_university_Select_all_that_you_may_be_interested_in'].apply(remove_medics)

    mentee_df = mentee_df[~mentee_df.duplicated(subset='What_is_your_email_address', keep='first')]
    print(mentee_df)
    return (mentor_df.dropna(), mentee_df.dropna())


def clean_text(text):
    if isinstance(text, str):  # Only apply to strings
        text = re.sub(r"\s+", "_", text)
        text = re.sub(r"[^\w_]", "", text)
    return text.strip("_")


def make_csvs(mentor_df, mentee_df, from_scratch=True):
    brother_mentors = [mentor_df.columns.tolist()]
    sister_mentors = [mentor_df.columns.tolist()]
    brother_mentees = [mentee_df.columns.tolist()]
    sister_mentees = [mentee_df.columns.tolist()]

    for row in mentor_df.itertuples():
        if row.Are_you_a_brother_or_sister == "Brother":
            brother_mentors.append(row)

        else:
            sister_mentors.append(row)

    for row in mentee_df.itertuples():
        if row.Are_you_a_brother_or_sister == "Brother":
            brother_mentees.append(row)

        else:
            sister_mentees.append(row)

    folder = os.path.join(os.getcwd(), "csvs")
    if not os.path.isdir(os.path.join(os.getcwd(), "csvs")):
        os.mkdir(folder)
    if from_scratch:
        mentor_df['current_student_numbers'] = 0
    mentor_df.to_csv(os.path.join(folder, "mentors.csv"), index=False)
    mentee_df.to_csv(os.path.join(folder, "mentees.csv"), index=False)

    brother_mentors_df = pd.DataFrame(brother_mentors)
    brother_mentors_df.to_csv(
        os.path.join(folder, "brother_mentors.csv"), index=False, header=False
    )
    sister_mentors_df = pd.DataFrame(sister_mentors)
    sister_mentors_df.to_csv(
        os.path.join(folder, "sister_mentors.csv"), index=False, header=False
    )

    brother_mentees_df = pd.DataFrame(brother_mentees)
    brother_mentees_df.to_csv(
        os.path.join(folder, "brother_mentees.csv"), index=False, header=False
    )
    sister_mentees_df = pd.DataFrame(sister_mentees)
    sister_mentees_df.to_csv(
        os.path.join(folder, "sister_mentees.csv"), index=False, header=False
    )


if __name__ == "__main__":
    mentor_df, mentee_df = get_mentor_mentee_dfs(
        "spreadsheet_id.txt", "Form responses 1", "Form responses 2"
    )
    make_csvs(mentor_df, mentee_df)

    mentor_list = MentorList(os.path.join("csvs", "mentors.csv"))
    for row in mentee_df.itertuples():
        if pd.notna(row):
            mentor_list.pair_mentee(Mentee(row))

    mentor_list.make_mentor_mentee_json()
