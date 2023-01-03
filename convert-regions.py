#!/usr/bin/python

import csv
import re
from hashlib import sha256

REGIONS = (
    'olddata/regions-2.csv',
    'olddata/regions-3.csv',
    'olddata/regions-4.csv',
    'olddata/regions-1.csv',
    'olddata/regions-5.csv',
)

REGION_CODES = 'olddata/region-codes.csv'

FINAL = 'data/regions.csv'

S_RE = r'[^а-яА-Я]*'
def simplify(s):
    return re.sub(S_RE, '', s).lower()
def get_words(s):
    words = []
    for ss in s.split(' '):
        word = simplify(ss)
        if len(word) > 0:
            words.append(word)
    return words

def read_codes(filename):
    reader = csv.reader(open(filename), delimiter=':')
    regions = {}
    for row in reader:
        if len(row) != 4:
            continue
        code, fullname, typ, name = row
        for w in get_words(name):
            assert w not in regions
            regions[w] = code
    regions['мск'] = 77
    regions['спб'] = 78
    return regions

def save_users(filename, users):
    writer = csv.writer(open(filename, 'w', newline=''), delimiter=':',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)        
    for u,codes in users.items():
        writer.writerow([u, codes[0]])

def read_regions(filename, regions, users):
    reader = csv.reader(open(filename), delimiter=':')
    for row in reader:
        if len(row) == 3:
            email, reg1, reg2 = row
        elif len(row) == 2:
            email, reg2 = row
            reg1 = None
        else:
            continue
        if not reg1 and not reg2:
            continue
        user = sha256(row[0].lower().encode('utf-8')).hexdigest()
        if reg1 is not None:
            found_reg = None
            for w in get_words(reg1):
                if w in regions:
                    found_reg = regions[w]
                    break
            if found_reg:
                if user in users and users[user][0] != found_reg:
                    users[user] = [found_reg,] + users[user]
                else:
                    users[user] = [found_reg,]
                continue
        if reg2:
            for w in get_words(reg2):
                if w in regions:
                    if user in users and regions[w] not in users[user]:
                        users[user].append(regions[w])
                    else:
                        users[user] = [regions[w],]
                    break

regions = read_codes(REGION_CODES)
users = {}
for r in REGIONS:
    read_regions(r, regions, users)
print('total users:', len(users))
more_than_2 = 0
for codes in users.values():
    if len(codes) > 2:
        more_than_2 += 1
print('more than 2 regions:', more_than_2)
save_users(FINAL, users)
