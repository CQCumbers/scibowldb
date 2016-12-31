#!flask/bin/python
from app import app, db
from app.models import Question
import os, re, json, unicodedata

source_name = 'CSUB' # Use Official, 98Nats, 05Nats, or CSUB (folder names)

rounds_path = source_name+'/text' # A folder of OCR'd Science Bowl sample rounds
if source_name == '98Nats':
    regex = re.compile(r'TOSS-UP\s' 
                        r'(\d+)(?:\)|\.) ' # question number
                        r'(ASTR|BIOL|CHEM|ERSC|GENR|PHYS|MATH|COMP); ' # category of question
                        r'(Short Answer|Multiple Choice): ' # format of toss up
                        r'([\s\S]+?(?=ANSWER))' # toss up question text
                        r'ANSWER: ([\s\S]+?(?=BONUS))' # toss up answer
                        r'\s*BONUS\s'
                        r'(\d+)(?:\)|\.) '
                        r'(ASTR|BIOL|CHEM|ERSC|GENR|PHYS|MATH|COMP); '
                        r'(Short Answer|Multiple Choice): ' # format of bonus
                        r'([\s\S]+?(?=ANSWER))' #  bonus question text
                        r'ANSWER: ([\s\S]+?(?=TOSS-UP|ROUND|\Z))', re.M) # bonus answer
else:
    regex = re.compile(r'TOSS-UP\s'
                        r'(\d+)(?:\)|\.) ' # question number
                        r'(PHYSICS|GENERAL SCIENCE|ENERGY|EARTH AND SPACE|EARTH SCIENCE|CHEMISTRY|BIOLOGY|ASTRONOMY|MATH|COMPUTER SCIENCE) ' # category of question
                        r'(Short Answer|Multiple Choice) ' # format of toss up
                        r'([\s\S]+?(?=ANSWER))' # toss up question text
                        r'ANSWER: ([\s\S]+?(?=BONUS))' # toss up answer
                        r'\s*BONUS\s'
                        r'(\d+)(?:\)|\.) ' 
                        r'(PHYSICS|GENERAL SCIENCE|ENERGY|EARTH AND SPACE|EARTH SCIENCE|CHEMISTRY|BIOLOGY|ASTRONOMY|MATH|COMPUTER SCIENCE) '
                        r'(Short Answer|Multiple Choice) ' # format of bonus
                        r'([\s\S]+?(?=ANSWER))' # bonus question text
                        r'ANSWER: ([\s\S]+?(?=TOSS-UP|ROUND|\Z))', re.M) # bonus answer

for filename in os.listdir(rounds_path):
    if filename.endswith('.txt'):
        with open(os.path.join(rounds_path, filename), encoding='utf8') as file:

            source = source_name+'-'+filename[:-4]

            for match in regex.findall(file.read()):
                if source_name == '98Nats':
                    if match[1] == 'ASTR':
                        category = 'ASTRONOMY'
                    elif match[1] == 'BIOL':
                        category = 'BIOLOGY'
                    elif match[1] == 'CHEM':
                        category = 'CHEMISTRY'
                    elif match[1] == 'ERSC':
                        category = 'EARTH SCIENCE'
                    elif match[1] == 'GENR':
                        category = 'GENERAL SCIENCE'
                    elif match[1] == 'PHYS':
                        category = 'PHYSICS'
                    elif match[1] == 'MATH':
                        category = 'MATH'
                    elif match[1] == 'COMP':
                        category = 'COMPUTER SCIENCE'
                    else:
                        print('No proper category on ' + source + ', question ' + match[0])
                else:
                    category = match[1]

                match = [item.rstrip() for item in match] # strip trailing whitespace from all fields
                db.session.add(Question(
                    category=category,
                    source=source,
                    tossup_format=match[2],
                    tossup_question=re.sub(r'\n\s+', '\n', match[3]),
                    tossup_answer=match[4],
                    bonus_format=match[7],
                    bonus_question=re.sub(r'\n\s+', '\n', match[8]),
                    bonus_answer=match[9]
                ))

db.session.commit()
