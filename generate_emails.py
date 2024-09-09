import json
import os
import shutil
import re

full_name = lambda ment__: ment__['full_name'].strip().title()
first_name = lambda ment__: ment__['full_name'].split()[0].strip().capitalize()

def mentor_email(mentor):
    if re.match(r'^[a-zA-Z]{2,}[0-9]{2,}$', mentor['short_code']):
        return f"{mentor['short_code']}.ic.ac.uk"
    elif re.match(r'.*@[ic|imperial].ac.uk$', mentor['short_code']):
        return mentor['short_code']
    else:
        return "REPLACE WITH CORRECT EMAIL"

email_format = lambda mentee, mentor, his_her='their': (
f"""Assalamu Alaykum,

Firstly, thank you {full_name(mentee)}, for signing up for the UCAS Support Service. We are committed to assisting you throughout this pivotal phase of your academic journey. We hope the support you receive over the next coming weeks will be fruitful and beneficial inshaAllah. 

{first_name(mentee)}, I'm pleased to introduce you to {full_name(mentor)}, who is a {mentor['year']} Year studying {mentor['course']} at Imperial College London who will be your dedicated mentor, guiding you throughout your UCAS Application process. 

{first_name(mentor)}, I'd like to introduce to you {full_name(mentee)}, who is a diligent sixth form student also aspiring to study {mentor['course']} and we found you are a perfect match to support {first_name(mentee)} in {his_her} endeavours. 

I hope you both get acquainted with each other and make this journey a smooth and rewarding experience.
If you require any support with setting up meetings or anything else, please feel free to get in touch. 


Mentor’s email: {mentor_email(mentor)}

Mentee’s email: {mentee['email']}


Wishing you all the best,
STEM Muslims"""
)


def generate_emails():
    if os.path.isdir("emails"):
        shutil.rmtree("emails")

    os.mkdir("emails")

    with open("mentor_mentee_pairings.json", "r") as f:
        pairings = json.load(f)
    
    total_emails = 0
    for pair in pairings:
        mentor = pair["mentor"]
        mentees = pair["mentees"]
        
        folder = os.path.join(os.getcwd(),'emails', full_name(mentor).replace(' ', '_'))
        os.mkdir(folder)
        os.mkdir(os.path.join(folder, "mentees_details"))

        with open(os.path.join(folder, f"mentor_details.json"), 'w') as f:
                json.dump(mentor, f, indent=4)

        he_she = "he" if mentor["gender"] == "Brother" else "she"
        his_her = "his" if mentor["gender"] == "Brother" else "her"
        him_her = "him" if mentor["gender"] == "Brother" else "her"

        for mentee in mentees:
            with open(os.path.join(folder, f"{full_name(mentor).replace(' ', '_')}_{full_name(mentee).replace(' ', '_')}.txt"), 'w') as f:
                print(f.name)
                f.write(email_format(mentee, mentor, his_her))
            
            with open(os.path.join(folder, 'mentees_details', f"{full_name(mentee).replace(' ', '_')}.json"), 'w') as f:
                json.dump(mentee, f, indent=4)

            total_emails += 1

    print(total_emails)

if __name__ == "__main__":
    generate_emails()
