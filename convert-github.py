#!/usr/bin/python3

import csv
import re
from hashlib import sha256

GITHUBS = (
    'olddata/githubs.csv',
)

FINAL = 'data/github-users.csv'

def save_users(filename, users):
    writer = csv.writer(open(filename, 'w', newline = ''), delimiter=':',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for u in users:
        writer.writerow([u])

def read_githubs(filename, users):
    reader = csv.reader(open(filename), delimiter=':')
    for row in reader:
        if len(row) != 2:
            continue
        email = row[0]
        user = sha256(row[0].lower().encode('utf-8')).hexdigest()
        users.add(user)
        
users = set([])
for r in GITHUBS:
    read_githubs(r, users)
print('total users:', len(users))
save_users(FINAL, users)
