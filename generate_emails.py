import json
import os
import shutil


def generate_emails():
    if os.path.isdir("emails"):
        shutil.rmtree("emails")

    os.mkdir("emails")

    with open("mentor_mentee_pairings.json", "r") as f:
        pairings = json.load(f)

    for pair in pairings:
        mentor = pair["mentor"]
        mentees = pair["mentees"]

        he_she = "he" if mentor["gender"] == "Brother" else "she"
        his_her = "his" if mentor["gender"] == "Brother" else "her"
        him_her = "him" if mentor["gender"] == "Brother" else "her"

        for mentee in mentees:
            mentee_email_text = f""".... {mentee['full_name']}, you have been paired with {mentor['full_name']}
{he_she} studies {mentor['course']} and is a {mentor['year']} student."""


if __name__ == "__main__":
    generate_emails()
