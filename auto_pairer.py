import re
from posixpath import isdir
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from mentor_mentee_classes import *


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
        .get(spreadsheetId=spreadsheet_id, range="test_form")
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

    return (mentor_df, mentee_df)


def clean_text(text):
    if isinstance(text, str):  # Only apply to strings
        text = re.sub(r"\s+", "_", text)
        text = re.sub(r"[^\w_]", "", text)
    return text.strip("_")


def make_csvs(mentor_df, mentee_df):
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

    mentor_df.to_csv(os.path.join(folder, "mentors.csv"))
    mentee_df.to_csv(os.path.join(folder, "mentees.csv"))

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
        "spreadsheet_id.txt", "test_form", "test_form_2"
    )
    make_csvs(mentor_df, mentee_df)

    mentor_list = MentorList(os.path.join("csvs", "mentors.csv"))
    for row in mentee_df.itertuples():
        mentor_list.pair_mentee(Mentee(row))

    mentor_list.make_mentor_mentee_json()
