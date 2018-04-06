import re
# For preprocessing H-W questions (make sure all category labels are preceded by newline):
# Find:  (\S[\S\s]+?)\n\n([\S\s]+?)\n\n
# Replace:  TOSS-UP\n1) \1\n\nBONUS\n1) \2\n\n
# For adding full answers to HW multiple choice questions (unprocessed has one letter answers)
# Find: ((w\) [ \S]+)\n(x\) [ \S]+)\n(y\) [ \S]+)\n(z\) [ \S]+)\nANSWER:) Z     (replace Z with W, X, Y)
# Replace: \1 \5    (change second group depending on W, X, Y)
# For removing page footers from official rounds
# Find: \n1999 Regional Round [1-9]B[\s\S]*?\n
# Replace: \n

official_regex = re.compile(r'TOSS-UP\s*'  # type of question
                    r'(\d+)(?:\)|\.)\s*'   # question number
                    r'(PHYSICS|GENERAL SCIENCE|ENERGY|EARTH AND SPACE|EARTH SCIENCE|CHEMISTRY|BIOLOGY|ASTRONOMY|MATH|COMPUTER SCIENCE) '   # category of question
                    r'(Short Answer|Multiple Choice) '  # format of question
                    r'([\s\S]+?(?=ANSWER))'  # actual question text
                    r'ANSWER: ([\s\S]+?(?=BONUS))'
                    r'\s*BONUS\s*'  # type of question
                    r'(\d+)(?:\)|\.)\s'   # question number
                    r'(PHYSICS|GENERAL SCIENCE|ENERGY|EARTH AND SPACE|EARTH SCIENCE|CHEMISTRY|BIOLOGY|ASTRONOMY|MATH|COMPUTER SCIENCE) '   # category of bonus
                    r'(Short Answer|Multiple Choice) '  # format of question
                    r'([\s\S]+?(?=ANSWER))'  # actual question text
                    r'ANSWER: ([\s\S]+?(?=\n\s|\n\d{4}|High|Round|ROUND|TOSS-UP|BONUS|$))', re.I)   # answer to question
                    #ROUND (\d+)[\s\S]+?(?=ROUND|$) //seperate file into rounds

nats98_regex = re.compile(r'TOSS-UP\s*'  # type of question
                    r'(\d+)(?:\)|\.)\s*'   # question number
                    r'(ASTR|BIOL|CHEM|ERSC|GENR|PHYS|MATH|COMP); '
                    r'(Short Answer|Multiple Choice): '
                    r'([\s\S]+?(?=ANSWER))'  # actual question text
                    r'ANSWER: ([\s\S]+?(?=BONUS))'
                    r'\s*BONUS\s*'  # type of question
                    r'(\d+)(?:\)|\.)\s'   # question number
                    r'(ASTR|BIOL|CHEM|ERSC|GENR|PHYS|MATH|COMP); '
                    r'(Short Answer|Multiple Choice): '
                    r'([\s\S]+?(?=ANSWER))'  # actual question text
                    r'ANSWER: ([\s\S]+?(?=\n\s|\n\d{4}|High|Round|ROUND|TOSS-UP|BONUS|$))', re.I)   # answer to question

exchange16_regex = re.compile(r'TOSS-UP\s*'  # type of question
                    r'(\d+)(?:\)|\.)\s*'   # question number
                    r'(PHYSICS|GENERAL SCIENCE|ENERGY|EARTH AND SPACE|EARTH SCIENCE|CHEMISTRY|BIOLOGY|ASTRONOMY|MATH|COMPUTER SCIENCE):?\s+'   # category of question
                    r'(Short Answer|Multiple Choice):?\s+'  # format of question
                    r'([\s\S]+?(?=ANSWER))'  # actual question text
                    r'ANSWER:\s*([\s\S]+?(?=BONUS))'
                    r'\s*BONUS\s*'  # type of question
                    r'(\d+)(?:\)|\.)\s'   # question number
                    r'(PHYSICS|GENERAL SCIENCE|ENERGY|EARTH AND SPACE|EARTH SCIENCE|CHEMISTRY|BIOLOGY|ASTRONOMY|MATH|COMPUTER SCIENCE):?\s+'   # category of bonus
                    r'(Short Answer|Multiple Choice):?\s+'  # format of question
                    r'([\s\S]+?(?=ANSWER))'  # actual question text
                    r'ANSWER:\s*([\s\S]+?(?=\n\s|\n\d{4}|TOSS-UP|BONUS|$))', re.I)   # answer to question
