from typing import List, Tuple
import pandas as pd
import json
import csv
import os


class Mentor:
    def __init__(self, row):
        self.timestamp = row.Timestamp
        self.full_name = row.What_is_your_full_name
        self.gender = row.Are_you_a_brother_or_sister
        self.short_code = row.What_is_your_Imperial_shortcode
        self.phone_number = row.What_is_your_phone_number
        self.course = row.What_course_do_you_study
        self.year = row.What_year_of_study_are_you_in
        self.mentorship_type = row.What_form_of_mentorship_are_you_able_to_provide
        self.max_students = 6 if row.How_many_students_are_you_able_to_mentor == '5+' else int(row.How_many_students_are_you_able_to_mentor)
        self.current_students = row.current_student_numbers
            
    def __lt__(self, other):
        return (
            self.current_students < other.current_students
            and self.current_students < self.max_students
        )


class Mentee:
    def __init__(self, row) -> None:
        self.full_name = row.What_is_your_full_name
        self.email = row.What_is_your_email_address
        self.a_levels = row.What_A_Levels_are_you_currently_taking
        try:
            self.interested_subjects = [
                item.strip()
                for item in row.What_are_you_interested_in_studying_at_university_Select_all_that_you_may_be_interested_in.split(
                    ","
                )
            ]
        except:
            self.interested_subjects = None
        self.gender = row.Are_you_a_brother_or_sister
        self.phone_number = row.What_is_your_phone_number
        self.why_interested = (
            row.Why_are_you_interested_in_studying_this_subject_23_sentences
        )
        self.areas_of_advice = row.Which_areas_are_you_looking_for_advice_with
        self.is_year13 = row.Are_you_a_year_13_student_intending_to_apply_to_Imperial


class MentorList:
    def __init__(self, csv_path) -> None:
        self.exception_students: List[Mentee] = []

        df = pd.read_csv(csv_path)
        self.mentor_pairings: List[Tuple[Mentor, List[Mentee]]] = [
            (Mentor(row), []) for row in df.itertuples()
        ]

    def pair_mentee(self, mentee: Mentee):

        for mentor, mentors_mentees in self.mentor_pairings:
            try:
                if (
                    mentor.course in mentee.interested_subjects
                    and mentor.gender == mentee.gender
                    and mentor.max_students > mentor.current_students
                ):
                    print(
                    f"""{mentee.full_name} paired with {mentor.full_name} Mentor does {mentor.course}, mentee interested in {mentee.interested_subjects}
----------------------------------------------------------------------------"""
                    )
                    mentors_mentees.append(mentee)
                    self.mentor_pairings.sort()
                    mentor.current_students += 1
                    return
            except:
                break
        if mentee.interested_subjects != [""]:
            print(f"{mentee.full_name} could not be paired, \ngender: {mentee.gender}\ncourses: {mentee.interested_subjects}\n----------------------------------------")
            self.exception_students.append(mentee)

    def make_mentor_mentee_json(self):
        json_mentor_mentee_pairs_data = []
        json_unpaired_mentor_data = []
        json_unpaired_mentee_data = [
            {"mentee": vars(mentee)} for mentee in self.exception_students
        ]
        for (
            mentor,
            mentees,
        ) in self.mentor_pairings:
            if mentees:
                entry = {
                    "mentor": vars(mentor),
                    "mentees": [vars(mentee) for mentee in mentees],
                }
                json_mentor_mentee_pairs_data.append(entry)
            else:
                entry = {"mentor": vars(mentor)}
                json_unpaired_mentor_data.append(entry)

        json_mentor_mentee_pairs_string = json.dumps(
            json_mentor_mentee_pairs_data, indent=4
        )
        json_unpaired_mentee_string = json.dumps(json_unpaired_mentee_data, indent=4)
        json_unpaired_mentor_string = json.dumps(json_unpaired_mentor_data, indent=4)

        with open("mentor_mentee_pairings.json", "w") as f:
            f.write(json_mentor_mentee_pairs_string)
        with open("unpaired_mentors.json", "w") as f:
            f.write(json_unpaired_mentor_string)
        with open("unpaired_mentees.json", "w") as f:
            f.write(json_unpaired_mentee_string)

        unpaired_mentors = [] 
        for (mentor, mentees) in self.mentor_pairings:
            if not mentees:
                unpaired_mentors.append(list(vars(mentor).values())[:-1])
        
        with open(os.path.join('csvs', 'mentors.csv'), 'r') as f:
            reader = csv.reader(f)
            first_row = next(reader)

        with open(os.path.join('csvs', 'mentors.csv'), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(first_row)
            for (mentor, _) in self.mentor_pairings:
                writer.writerow(list(vars(mentor).values()))

        #Gets the top row of the csv
        with open(os.path.join('csvs', 'mentees.csv'), 'r') as f:
            reader = csv.reader(f)
            first_row = next(reader)
   
        mentees_df = pd.read_csv(os.path.join('csvs', 'mentees.csv')).rename(columns={'What_is_your_full_name' : 'full_name'})
        mentees_df['full_name'] = mentees_df['full_name'].str.strip()
        
        unpaired_mentees_df = pd.DataFrame([vars(mentee) for mentee in self.exception_students])
        unpaired_mentees_df['full_name'] = unpaired_mentees_df['full_name'].str.strip()
        merged_df = pd.merge(mentees_df, unpaired_mentees_df[['full_name']], on='full_name', how='inner')

        merged_df.to_csv(os.path.join('csvs', 'unpaired_mentees.csv'), index=False)




