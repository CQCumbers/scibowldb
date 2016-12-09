#!flask/bin/python
from app import app, db
from app.models import Question
import os, re, json, unicodedata

rounds_path = 'CSUB_Samples/text' # A folder of OCR'd Science Bowl sample rounds
questions = []
regex = re.compile(r'TOSS-UP\s*'  # type of question
                    r'(\d+)(?:\)|\.)\s'   # question number
                    r'(PHYSICS|GENERAL SCIENCE|ENERGY|EARTH AND SPACE|EARTH SCIENCE|CHEMISTRY|BIOLOGY|ASTRONOMY) '   # category of question, no MATH because OCR problems
                    #r'(ASTR|BIOL|CHEM|ERSC|GENR|PHYS); '
                    r'(Short Answer|Multiple Choice) '  # format of question
                    #r'(Short Answer|Multiple Choice): '
                    r'([\s\S]+?(?=ANSWER))'  # actual question text
                    r'ANSWER: ([\s\S]+?(?=\n\s|\n\d{4}|High|Round|TOSS-UP|BONUS|$))'
                    r'BONUS\s*'  # type of question
                    r'(\d+)(?:\)|\.)\s'   # question number
                    r'(PHYSICS|GENERAL SCIENCE|ENERGY|EARTH AND SPACE|EARTH SCIENCE|CHEMISTRY|BIOLOGY|ASTRONOMY) '   # category of question, no MATH because OCR problems
                    #r'(ASTR|BIOL|CHEM|ERSC|GENR|PHYS); '
                    r'(Short Answer|Multiple Choice) '  # format of question
                    #r'(Short Answer|Multiple Choice): '
                    r'([\s\S]+?(?=ANSWER))'  # actual question text
                    r'ANSWER: ([\s\S]+?(?=\n\s|\n\d{4}|High|Round|TOSS-UP|BONUS|$))', re.I)   # answer to question

for filename in os.listdir(rounds_path):
    with open(os.path.join(rounds_path, filename), encoding='utf8') as file:
        source = 'CSUB-' + filename[1:-4]
        #source = 'NSB-set' + re.search(r'(\d+.+(?=\.txt))', filename).group(0)
        #source = '05Nats-' + filename[:-4]
        #source = '98Nats-' + filename[:-4]
        for match in regex.findall(file.read()):
            category = 'ERROR'
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
            else:
                print('No proper category on ' + source + ', question ' + match[0])

            db.session.add(Question(
                #category=category,
                category=match[1],
                source=source,
                tossup_format=match[2],
                tossup_question=re.sub(r'\n\s+', '\n', match[3]),
                tossup_answer=unicodedata.normalize('NFKD', re.sub(r'\n', ' ', match[4])).encode('ASCII', 'ignore').decode('utf8'),   # replace letters that cannot be typed on keyboard
                bonus_format=match[7],
                bonus_question=re.sub(r'\n\s+', '\n', match[8]),
                bonus_answer=unicodedata.normalize('NFKD', re.sub(r'\n', ' ', match[9])).encode('ASCII', 'ignore').decode('utf8')   # replace letters that cannot be typed on keyboard
            ))


#json.dump(questions, open('questions.json', 'a+'), indent=4, separators=(',', ': '), sort_keys=True)  # make JSON pretty looking
db.session.commit()
