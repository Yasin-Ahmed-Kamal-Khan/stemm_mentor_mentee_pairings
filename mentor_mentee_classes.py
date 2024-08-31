from typing import List, Tuple
import pandas as pd
import json


class Mentor:
    def __init__(self, row):
        self.full_name = row.What_is_your_full_name
        self.gender = row.Are_you_a_brother_or_sister
        self.short_code = row.What_is_your_Imperial_shortcode
        self.phone_number = row.What_is_your_phone_number
        self.course = row.What_course_do_you_study
        self.year = row.What_year_of_study_are_you_in
        self.mentorship_type = row.What_form_of_mentorship_are_you_able_to_provide
        self.max_students = row.How_many_students_are_you_able_to_mentor
        self.current_students = 0

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
        self.interested_subjects = row.What_are_you_interested_in_studying_at_university_Select_all_that_you_may_be_interested_in.split(
            ","
        )
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
            if mentor.course in mentee.interested_subjects:
                print(
                    f"""{mentee.full_name} paired with {mentor.full_name}
Mentor does {mentor.course}, mentee interested in {mentee.interested_subjects}"""
                )
                mentors_mentees.append(mentee)
                self.mentor_pairings.sort()
                return

        print(f"{mentee.full_name} could not be paired")
        self.exception_students.append(mentee)

    def make_mentor_mentee_json(self):
        json_data = []
        for (
            mentor,
            mentees,
        ) in self.mentor_pairings:
            entry = {
                "mentor": vars(mentor),
                "mentees": [vars(mentee) for mentee in mentees],
            }
            json_data.append(entry)

        json_string = json.dumps(json_data, indent=4)
        with open("pairings.json", "w") as f:
            f.write(json_string)
