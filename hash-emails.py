#!/usr/bin/python

from os import listdir
from os.path import isfile, join
from hashlib import sha256
import csv

FROM_DATADIR = 'olddata'
TO_DATADIR = 'data'

for f in listdir(FROM_DATADIR):
    if isfile(join(FROM_DATADIR, f)) and f.find('~') < 0 and f.find('.csv') > 0 and f.find('teams') > 0 and f.find('-hash.csv') < 0:
        name, ext = f.split('.')
        old_filename = join(FROM_DATADIR, f)
        new_filename = join(TO_DATADIR, '{}-hash.{}'.format(name, ext))
        print('converting {}'.format(old_filename))
        output = open(new_filename, 'w', newline = '')
        writer = csv.writer(output, delimiter=':',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)        
        reader = csv.reader(open(old_filename), delimiter=':')
        for row in reader:
            if len(row) < 3 or len(row) > 4 or row[0].find('@') < 0:
                continue
            if len(row[2].strip()) == 0:
                continue
            hashed_email = sha256(row[0].lower().encode('utf-8')).hexdigest()
            if len(row) == 4:
                teamid = str(row[3])
            else:
                teamid = ''
            writer.writerow([hashed_email, row[1], row[2], teamid])
        output.close()

SEX_FILE = 'talent-sex.csv'
OUTPUT_SEX_FILE = 'sex.csv'
if isfile(join(FROM_DATADIR, SEX_FILE)):
    name, ext = f.split('.')
    old_filename = join(FROM_DATADIR, SEX_FILE)
    new_filename = join(TO_DATADIR, OUTPUT_SEX_FILE)
    print('converting {}'.format(old_filename))
    output = open(new_filename, 'w', newline = '')
    writer = csv.writer(output, delimiter=':',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)        
    reader = csv.reader(open(old_filename), delimiter=':')
    for row in reader:
        if len(row) != 4 or row[0].find('@') < 0:
            continue
        hashed_email = sha256(row[0].lower().encode('utf-8')).hexdigest()
        writer.writerow([hashed_email] + row[1:4])
    output.close()

