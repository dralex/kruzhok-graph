#!/usr/bin/python

from os import listdir
from os.path import isfile, join
from hashlib import sha256
import csv

FROM_DATADIR = 'olddata'
PERSONS_FILE = 'persons.csv'
TEAMS_FILE = 'result-teams.csv'
OUTPUT_FILE = 'result-teams-emails.csv'
persons = {}
emails = {}

print('reading emails...')
for f in listdir(FROM_DATADIR):
    if isfile(join(FROM_DATADIR, f)) and f.find('~') < 0 and f.find('.csv') > 0 and f.find('teams') > 0 and f.find('-hash.csv') < 0:
        name, ext = f.split('.')
        old_filename = join(FROM_DATADIR, f)
        print('reading {}'.format(old_filename))
        reader = csv.reader(open(old_filename), delimiter=':')
        for row in reader:
            if len(row) != 3 or row[0].find('@') < 0:
                continue
            if len(row[2].strip()) == 0:
                continue
            eml = row[0].lower()
            hashed_email = sha256(eml.encode('utf-8')).hexdigest()
            emails[hashed_email] = eml

# print('reading persons...')
# reader = csv.reader(open(PERSONS_FILE), delimiter=':', quotechar='"')
# for row in reader:
#     if len(row) != 5 or row[0].find('@') < 0:
#         continue
#     email = row[0]
#     lastname = row[1].strip()
#     firstname = row[2]
#     middlename = row[3]
#     birthday = row[4]
#     if email not in persons or len(lastname) > len(persons[email][0]):
#         persons[email] = [lastname, firstname, middlename, birthday]

print('converting teams...')
reader = csv.reader(open(TEAMS_FILE), delimiter=':', quotechar='"')
output = open(OUTPUT_FILE, 'w', newline = '')
writer = csv.writer(output, delimiter=':',
                    quotechar='"', quoting=csv.QUOTE_MINIMAL)        
for row in reader:
    if len(row) < 5:
        continue
    static = row[0:5]
    hashes_num = int(row[4])
    names = []
    for h_idx in range(hashes_num):
        h = row[5 + h_idx]
        assert h in emails, h
        e = emails[h]
#        if e in persons and len(persons[e][0]) > 0:
#            data = ' '.join(persons[e])
#        else:
#            data = 'Неизвестный пользователь'
        names.append(e)
    writer.writerow(list(static) + names)
output.close()
