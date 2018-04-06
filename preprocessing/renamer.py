#!/usr/bin/env
import os, re

rounds_path = os.path.join('Official_Samples','pdfs')
for filename in os.listdir(rounds_path):
    if filename.startswith('Set-7'):
        new_name = 'set'+filename[4]+'-round'+filename[12:-4]+'.pdf'
        print(new_name)
        os.rename(os.path.join(rounds_path, filename), os.path.join(rounds_path, new_name))
