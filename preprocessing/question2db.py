import os, re, json, unicodedata, sqlalchemy, question_re, glob
from app.models import db, Question

testing = False 
# if testing, output is to JSON instead of database
root_path = os.path.expanduser('~/path/to/questions')
# Folder names after root_path (except last text folder) are listed in source, along with name of file
# path should include all folders before 'text' folder that the regex will be applied to
#paths = glob.glob(root_path+'16Exchange/*')
paths = glob.glob(root_path+'00Regs')
regex = question_re.exchange16_regex

questions = []
print('Searching folders: ')
for folder in paths:
    # A folder of OCR'd Science Bowl sample rounds
    rounds_path = folder+'/text' 
    folder = folder[len(root_path):]
    print(folder)
    for filename in os.listdir(rounds_path):
        with open(os.path.join(rounds_path, filename), encoding='utf8') as file:
            source = folder[:].replace('/','-')+'-'+filename[:-4]
            for match in regex.findall(file.read()):
                # special case for 98Nats regex output
                if regex == question_re.nats98_regex: 
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

                # strip trailing whitespace from all fields
                match = [item.rstrip() for item in match] 
                questions.append({
                    'category': category.upper(),
                    'source': source,
                    'tossup_format': match[2],
                    'tossup_question': re.sub(r'\n\s+', '\n', match[3]),
                    'tossup_answer': match[4],
                    'bonus_format': match[7],
                    'bonus_question': re.sub(r'\n\s+', '\n', match[8]),
                    'bonus_answer': match[9]
                })

print('\n'+str(len(questions))+' questions found')
if testing: # make JSON pretty looking
    json.dump(questions, open('questions_test.json', 'w+'), indent=4, separators=(',', ': '), sort_keys=True)  
else:
    dupes = 0
    for question in questions:
        try:
            existing = db.session.query(Question).filter_by(**{k:question[k] for k in ('tossup_question','bonus_question')}).one()
        except sqlalchemy.orm.exc.NoResultFound:
            db.session.add(Question(**question))
        else:
            print(question['tossup_question'])
            dupes += 1
    print(str(dupes)+' duplicates found')
    db.session.commit()
