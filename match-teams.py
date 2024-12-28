#!/usr/bin/python3
# ------------------------------------------------------------------------------
# Kruzhok Movement teams matching tool
#
# Alexey Fedoseev <aleksey@fedoseev.net>, 2020-2023
# ------------------------------------------------------------------------------

import csv
import igraph
import datetime
from os.path import join
import re
import random

# ------------------------------------------------------------------------------
# Global constants and flags
# ------------------------------------------------------------------------------

DEBUG = True
TEAM_SIZE = 2
USE_GITHUB = True
BUILD_GRAPH = True
CALCULATE_CLUSTERS = False
PLOT_GRAPH = True
FULL_GRAPH = True
SKIP_SELECTION = False
PLOT_LABELS = False
LABELS_COLOR = '#00000088'
EDGES_COLOR = '#00000088'
USE_TOPICS = False
SAVE_CSV = False
COLOR_SCHEME = 'sex' # 'events' 'sex' 'reg'
SAVE_SVG = True
SAVE_PNG = True
PICTURE_SIZE = 4000 #4000
FILTER_ORIGIN = None #['ВОСТОК', 'Rukami(отбор)', 'Rukami(финал)']
FILTER_PARTICIPANT = None
FILTER_REGIONS = []
ALL_REGIONS = False

RESULT_CSV = 'result.csv'
RESULT_TEAMS_CSV = 'result-teams.csv'
RESULT_PNG = 'graph.png'
RESULT_SVG = 'graph.svg'
RESULT_REGS_PNG = 'reggraph-{}.png'
RESULT_REGS_SVG = 'reggraph-{}.svg'
TEAM_NAME_LIMIT = 15
DATADIR = 'data'
COLORS_FILE = join(DATADIR, 'event-colors.csv')
REGIONS_FILE = join(DATADIR, 'regions.csv')
SEX_FILE = join(DATADIR, 'sex.csv')
TOPICS_FILE = join(DATADIR, 'topics.csv')
AUTOTEAMS_FILE = join(DATADIR, 'talent-autoteams.csv')
EVENT_TOPICS_FILE = join(DATADIR, 'events-topics.csv')
GITHUBS_FILE = join(DATADIR, 'github-users.csv')
RUKAMI_REST_TOPIC = 'Прочее'

# teaminfo indexes

TI_ORIGIN = 0
TI_EVENT = 1
TI_TEAM = 2
TI_TEAM_LABEL = 3
TI_TALENT_TEAM = 4
TI_FEMALE = 5
TI_SEX = 6
TI_REGIONS = 7
TI_WITH_REG = 8

# ------------------------------------------------------------------------------
# Data structure
# ------------------------------------------------------------------------------

TeamOrigins = {
    'НКФП':{
        'active': True,
        'type': 'hackathon',
        'season': None,
        'teams': join(DATADIR, 'talent-nkfp-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-nkfp-dates.csv'),
        'selections': None,
        'limit': 10
    },
    'ПБ':{
        'active': True,
        'type': 'hackathon',
        'season': None,
        'teams': join(DATADIR, 'talent-pb-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-pb-dates.csv'),
        'selections': None,
        'limit': 10
    },
    'ОРЗ':{
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'talent-orz-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-orz-dates.csv'),
        'selections': None,
        'limit': 10
    },
    'KRUZHOK.PRO': {
        'active': True,
        'type': 'hackathon',
        'season': None,
        'teams': join(DATADIR, 'talent-kruzhokpro-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-kruzhokpro-dates.csv'),
        'selections': None,
        'limit': None
    },
    'FOSS': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'talent-opensource-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-opensource-dates.csv'),
        'selections': None,
        'limit': None
    },
    'ВОСТОК': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'talent-vostok-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-vostok-dates.csv'),
        'selections': None,
        'limit': None
    },
    'ДЕЖУРНЫЙ': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'talent-planet-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-planet-dates.csv'),
        'selections': None,
        'limit': None
    },
    'ТАЛАНТ-2035': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'talent-2035-proj-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-2035-proj-dates.csv'),
        'selections': None,
        'limit': None
    },
    'МОРРОБ': {
        'active': True,
        'type': 'contest',
        'season': None,
        'teams': join(DATADIR, 'talent-sea-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-sea-dates.csv'),
        'selections': None,
        'limit': None
    },
    'УЧЕБУ': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'talent-futsci-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-futsci-dates.csv'),
        'selections': None,
        'limit': None
    },
    'Rukami(отбор)': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'rukami-teams-hash.csv'),
        'level': 1,
        'dates': datetime.date(2020, 9, 11),
        'selections': None,
        'limit': None
    },
    'Rukami(финал)': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'rukami-final-teams-hash.csv'),
        'level': 1,
        'dates': datetime.date(2020, 11, 28),
        'selections': None,
        'limit': None
    },
    'ОНТИ-2018/19(2)': {
        'active': True,
        'type': 'onti',
        'season': 2018,
        'teams': join(DATADIR, 'onti-teams-1819-hash.csv'),
        'level': 1,
        'dates': datetime.date(2018, 11, 15),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-2018/19(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2018,
        'teams': join(DATADIR, 'onti-teams-1819-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2019, 3, 1),
        'selections': 'ОНТИ-2018/19(2)',
        'limit': 6
    },
    'ОНТИ-СТУД-2018/19(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2018,
        'teams': join(DATADIR, 'talent-onti-teams-stud-1819-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2019, 3, 1),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-2019/20(2)': {
        'active': True,
        'type': 'onti',
        'season': 2019,
        'teams': join(DATADIR, 'onti-teams-1920-hash.csv'),
        'level': 1,
        'dates': datetime.date(2019, 11, 15),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-2019/20(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2019,
        'teams': join(DATADIR, 'onti-teams-1920-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2020, 3, 1),
        'selections': 'ОНТИ-2019/20(2)',
        'limit': 6
    },
    'ОНТИ-СТУД-2019/20(2)': {
        'active': True,
        'type': 'onti',
        'season': 2019,
        'teams': join(DATADIR, 'talent-onti-teams-stud-1920-hash.csv'),
        'level': 1,
        'dates': datetime.date(2020, 3, 1),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-СТУД-2019/20(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2019,
        'teams': join(DATADIR, 'talent-onti-teams-stud-1920-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2020, 3, 1),
        'selections': 'ОНТИ-СТУД-2019/20(2)',
        'limit': 6
    },
    'ОНТИ-2020/21(2)': {
        'active': True,
        'type': 'onti',
        'season': 2020,
        'teams': join(DATADIR, 'talent-onti-teams-2021-hash.csv'),
        'level': 1,
        'dates': datetime.date(2020, 11, 15),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-2020/21(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2020,
        'teams': join(DATADIR, 'talent-onti-teams-2021-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2021, 3, 1),
        'selections': 'ОНТИ-2020/21',
        'limit': 6
    },
    'ОНТИ-СТУД-2020/21': {
        'active': True,
        'type': 'onti',
        'season': 2020,
        'teams': join(DATADIR, 'talent-onti-teams-stud-2021-hash.csv'),
        'level': 1,
        'dates': datetime.date(2020, 11, 1),
        'selections': None,
        'limit': 6
    },    
    'ОНТИ-СТУД-2020/21(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2020,
        'teams': join(DATADIR, 'talent-onti-teams-stud-2021-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2021, 3, 1),
        'selections': 'ОНТИ-СТУД-2020/21',
        'limit': 6
    },
    'ОНТИ-2021/22(2)': {
        'active': True,
        'type': 'onti',
        'season': 2021,
        'teams': join(DATADIR, 'talent-onti-teams-2122-hash.csv'),
        'level': 1,
        'dates': datetime.date(2021, 11, 15),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-2021/22(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2021,
        'teams': join(DATADIR, 'talent-onti-teams-2122-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2021, 11, 15),
        'selections': 'ОНТИ-2021/22(2)',
        'limit': 6
    },
    'ОНТИ-СТУД-2021/22': {
        'active': True,
        'type': 'onti',
        'season': 2021,
        'teams': join(DATADIR, 'talent-onti-teams-stud-2122-hash.csv'),
        'level': 1,
        'dates': datetime.date(2021, 10, 1),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-СТУД-2021/22(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2021,
        'teams': join(DATADIR, 'talent-onti-teams-stud-2122-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2022, 3, 1),
        'selections': 'ОНТИ-СТУД-2021/22',
        'limit': 6
    },
    'ОНТИ-2022/23(2)': {
        'active': True,
        'type': 'onti',
        'season': 2022,
        'teams': join(DATADIR, 'talent-onti-teams-2223-hash.csv'),
        'level': 1,
        'dates': datetime.date(2022, 11, 15),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-2022/23(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2022,
        'teams': join(DATADIR, 'talent-onti-teams-2223-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2023, 3, 1),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-СТУД-2022/23': {
        'active': True,
        'type': 'onti',
        'season': 2022,
        'teams': join(DATADIR, 'talent-onti-teams-stud-2223-hash.csv'),
        'level': 1,
        'dates': datetime.date(2022, 10, 1),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-СТУД-2022/23(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2022,
        'teams': join(DATADIR, 'talent-onti-teams-stud-2223-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2023, 3, 1),
        'selections': 'ОНТИ-СТУД-2022/23',
        'limit': 6
    },
    'ОНТИ-ДЖУН-2022/23(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2022,
        'teams': join(DATADIR, 'talent-onti-teams-jun-2223-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2022, 12, 1),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-2023/24(2)': {
        'active': True,
        'type': 'onti',
        'season': 2023,
        'teams': join(DATADIR, 'talent-onti-teams-2324-hash.csv'),
        'level': 1,
        'dates': datetime.date(2023, 11, 15),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-СТУД-2023/24': {
        'active': True,
        'type': 'onti',
        'season': 2023,
        'teams': join(DATADIR, 'talent-onti-teams-stud-2324-hash.csv'),
        'level': 1,
        'dates': datetime.date(2023, 10, 1),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-ДЖУН-2023/24(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2023,
        'teams': join(DATADIR, 'talent-onti-teams-jun-2324-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2023, 12, 1),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-СТУД-2023/24(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2023,
        'teams': join(DATADIR, 'talent-onti-teams-stud-2324-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2024, 3, 1),
        'selections': 'ОНТИ-СТУД-2023/24',
        'limit': 6
    },
    'ОНТИ-2023/24(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2023,
        'teams': join(DATADIR, 'talent-onti-teams-2324-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2024, 3, 1),
        'selections': 'ОНТИ-2023/24(2)',
        'limit': 6
    },
    'ОНТИ-2024/25(2)': {
        'active': True,
        'type': 'onti',
        'season': 2024,
        'teams': join(DATADIR, 'talent-onti-teams-2425-hash.csv'),
        'level': 1,
        'dates': datetime.date(2024, 11, 1),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-СТУД-2024/25': {
        'active': True,
        'type': 'onti',
        'season': 2024,
        'teams': join(DATADIR, 'talent-onti-teams-stud-2425-hash.csv'),
        'level': 1,
        'dates': datetime.date(2024, 10, 1),
        'selections': None,
        'limit': 6
    },
    'ОНТИ-ДЖУН-2024/25(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2024,
        'teams': join(DATADIR, 'talent-onti-teams-jun-2425-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2024, 12, 20),
        'selections': None,
        'limit': 6
    },
}

def CONVERT_ORIGIN_NAME(origin):
    if origin.find('ОНТИ') == 0:
        return 'ОНТИ'
    elif origin.find('Rukami') == 0:
        return 'Rukami'
    else:
        return 'ПБ'

# ------------------------------------------------------------------------------
# Debugging and assertions
# ------------------------------------------------------------------------------

def debug(*s):
    if DEBUG:
        print(*s)

# ------------------------------------------------------------------------------
# CSV utilities
# ------------------------------------------------------------------------------
def read_participants(fname, prefix):
    participants = []
    reader = csv.reader(open(fname, encoding="utf-8"), delimiter=':')
    for row in reader:
        if len(row) < 3 or len(row) > 4:
            debug('file {} bad line {}'.format(fname, str(row)))
            continue
        if len(row[2].strip()) > 0:
            if len(row) == 4 and len(row[3]) > 0:
                teamid = int(row[3])
            else:
                teamid = None
            participants.append((row[0], prefix, row[1], row[2], teamid))
    return participants

def read_dates(fname):
    d = {}
    reader = csv.reader(open(fname, encoding="utf-8"), delimiter=':')
    for row in reader:
        if len(row) == 2:
            datestr = row[1].split('.')
            year = int(datestr[2])
            month = int(datestr[1])
            day = int(datestr[0])
            d[row[0]] = datetime.date(year, month, day)
    return d

def read_colors(fname):
    colors = {}
    reader = csv.reader(open(fname, encoding="utf-8"), delimiter=':')
    for row in reader:
        if len(row) == 2:
            origin, color = row
            colors[origin] = color
    return colors

def read_regions(fname):
    users = {}
    reader = csv.reader(open(fname, encoding="utf-8"), delimiter=':')
    for row in reader:
        if len(row) == 2:
            user, code = row
            users[user] = int(code)
    return users

def read_githubs(fname):
    users = set([])
    reader = csv.reader(open(fname, encoding="utf-8"), delimiter=':')
    for row in reader:
        if len(row) == 1 and len(row[0]) > 0:
            users.add(hash(row[0]))
    return users

def read_autoteams(fname):
    autoteams = set([])
    reader = csv.reader(open(fname, encoding="utf-8"), delimiter=':')
    for row in reader:
        if len(row) == 1 and len(row[0]) > 0:
            autoteams.add(int(row[0]))
    return autoteams

def read_topics(fname):
    topics = {}
    topics_all = set()
    reader = csv.reader(open(fname, encoding="utf-8"), delimiter=':')
    for row in reader:
        if len(row) == 0:
            continue
        target = row[0]
        topics_all.add(target)
        for r in row:
            if r not in topics:
                topics[r] = set([])
            topics[r].add(target)
    return (topics_all, topics)

def read_event_topics(fname, topics, events):
    all_topics = {}
    for o in events:
        all_topics[o] = {}
    reader = csv.reader(open(fname, encoding="utf-8"), delimiter=':')
    for row in reader:
        if len(row) == 2:
            origin, event = row
            if event not in topics:
                debug('event {} is not in topics'.format(event))
                continue
            all_topics[origin][event] = topics[event]
        elif len(row) > 2:
            origin, event = row[0:2]
            s = set([])
            for r in row[2:]:
                assert len(r) > 0, row
                assert r in topics, r
                s.update(topics[r])
            all_topics[origin][event] = s
        else:
            debug('bad event topic row {}'.format(row))
            exit(1)
    for rukami in ('Rukami(отбор)','Rukami(финал)'):    
        for e in events[rukami]:
            assert e in topics, e
            all_topics[rukami][e] = topics[e]
    return all_topics

def convert_sex(n, m, s):
    if len(s.strip()) != 0:
        if s != 'm' and s != 'w':
            debug('unsupported sex {}'.format(s))
            return None
        return s
    if len(m) > 0:
        if s.rfind('вич') == len(s) - len('вич'):
            return 'm'
        if s.rfind('вна') == len(s) - len('вна'):
            return 'w'
    return None

name_sex_cache = {}
def read_sex(fname):
    sex = {}
    reader = csv.reader(open(fname, encoding="utf-8"), delimiter=':')
    notfound = {}
    for row in reader:
        if len(row) == 4:
            h, n, m, s = row
            s = convert_sex(n, m, s)
            if s:
                if len(n) > 0:
                    if n not in name_sex_cache:
                        name_sex_cache[n] = {}
                        name_sex_cache[n]['m'] = 0
                        name_sex_cache[n]['w'] = 0
                    name_sex_cache[n][s] += 1
                sex[hash(h)] = s
            else:
                notfound[hash(h)] = n
    for h, n in notfound.items():
        if len(n) > 0 and n in name_sex_cache:
            s1 = name_sex_cache[n]['m']
            s2 = name_sex_cache[n]['w']
            if s1 != s2:
                sex[h] = 'm' if s1 > s2 else 'w'
    return sex

def save_csv(fname, data):
    debug('saving csv {}...'.format(fname))
    with open(fname, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=':',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)

# ------------------------------------------------------------------------------
# Data initializers
# ------------------------------------------------------------------------------

def init_teams():
    for origin in TeamOrigins.values():
        if not origin['active']:
            continue
        if isinstance(origin['dates'], str):
            origin['dates'] = read_dates(origin['dates'])

def read_teams(regions, githubs, sex, colors):
    participants = []
    for origin,data in TeamOrigins.items():
        if not data['active']:
            continue
        data['color'] = colors[origin]
        participants += read_participants(data['teams'],
                                          origin)
    debug('participants:', len(participants))
    if USE_GITHUB:
        debug('githubs:', len(githubs))
    
    all_events = {}

    teaminfo = {}
    teams = {}
    emails = {}
    has_regions = 0
    has_github = 0
    reg_filter = 0
    have_sex = 0
    female = 0
    event_teams = {}

    for p in participants:
        email, origin, event, team, team_talent_id = p

        origininfo = TeamOrigins[origin]
        if origin.find('Rukami') == 0 and len(event) == 0:
            event = RUKAMI_REST_TOPIC

        assert len(event) > 0, p
        
        # check date costistency
        if origin not in all_events:
            all_events[origin] = set([])
            assert (isinstance(origininfo['dates'], datetime.date) or
                    event in origininfo['dates']), 'no date available for event {}:{}'.format(origin, event)
        all_events[origin].add(event)
        if (origin + event) not in event_teams:
            event_teams[origin + event] = 0
        
        emailhash = hash(email)
        if emailhash in sex: 
            emailsex = sex[emailhash]
        else:
            emailsex = '?'
        fem = int(emailsex == 'w')
        known_sex = int(emailsex != '?')
        teamhash = hash(origin + event + team)
        if teamhash not in teaminfo:
            teaminfo[teamhash] = ([origin, event, team] +
                                  [team if len(team) < TEAM_NAME_LIMIT else team[0:TEAM_NAME_LIMIT] + '...'] +
                                  [team_talent_id, 0, 0, set([]), 0])
            event_teams[origin + event] += 1
        if teamhash not in teams:
            teams[teamhash] = set([])
        if emailhash not in teams[teamhash]:
            teams[teamhash].add(emailhash)
            teaminfo[teamhash][TI_FEMALE] += fem
            teaminfo[teamhash][TI_SEX] += known_sex

        if emailhash not in emails:
            emails[emailhash] = email
            female += fem
            have_sex += known_sex
            if email in regions:
                has_regions += 1
                reg = regions[email]
                if FILTER_REGIONS and reg in FILTER_REGIONS:
                    reg_filter += 1
                teaminfo[teamhash][TI_REGIONS].add(reg)
                teaminfo[teamhash][TI_WITH_REG] += 1
            if USE_GITHUB:
                if emailhash in githubs:
                    has_github += 1

    if USE_TOPICS:
        topics_all, topics = read_topics(TOPICS_FILE)
        event_topics = read_event_topics(EVENT_TOPICS_FILE, topics, all_events)
    else:
        topics_all = event_topics = None
        
    debug('events:')
    sum_events = 0
    for o,events in all_events.items():
        if FILTER_ORIGIN and o not in FILTER_ORIGIN:
            continue 
        debug('\t{}: {}'.format(o, len(events)))
        for e in events:
            oe = o + e
            debug('\t\t{}: {} teams'.format(e, event_teams[oe] if oe in event_teams else oe))
        sum_events += len(events)
#        for e in events:
#            debug('\t\t{}: [{}]'.format(e, '|'.join(event_topics[o][e])))
    debug('total events:', sum_events)
    debug('students:', len(emails))
    debug('students with sex:', have_sex)
    debug('female students:', female)
    debug('students with regions:', has_regions)
    if USE_GITHUB:
        debug('students with github:', has_github)
    if FILTER_REGIONS:
        debug('students with filter {}: {}'.format(FILTER_REGIONS, reg_filter))
    debug('teams:', len(teams))
    
    teams_in_talentdb = 0
    for t in teams.keys():
        talent_team = teaminfo[t][TI_TALENT_TEAM]
        if talent_team:
            teams_in_talentdb += 1
    debug('teams in talent db:', teams_in_talentdb)

    # drop bad teams

    to_delete = []
    goptar_teams = set([])
    for t,e in teams.items():
        size = len(e)
        origininfo = TeamOrigins[teaminfo[t][TI_ORIGIN]]
        if size == 1 or origininfo['limit'] and size > origininfo['limit']:
            to_delete.append(t)
        else:
            if FILTER_REGIONS:
                found = False
                for emailhash in e:
                    email = emails[emailhash]
                    if email in regions and regions[email] in FILTER_REGIONS:
                        found = True
                if not found:
                    to_delete.append(t)
            if FILTER_PARTICIPANT:
                found = False
                for emailhash in e:
                    email = emails[emailhash]
                    if email == FILTER_PARTICIPANT:
                        found = True
                if not found:
                    to_delete.append(t)                
    for t in to_delete:
        del teams[t]

    debug('teams after cleaning:', len(teams))

    teams_in_talentdb = 0
    teams_onti = 0
    teams_pb = 0
    teams_rest = 0
    for t in teams.keys():
        ti = teaminfo[t]
        talent_team = ti[TI_TALENT_TEAM]
        if talent_team:
            teams_in_talentdb += 1
        origin = ti[TI_ORIGIN]
        if origin.find('ОНТИ') == 0:
            teams_onti += 1
        elif origin.find('ПБ') == 0:
            teams_pb += 1
        else:
            teams_rest += 1
            
    debug('teams in talent db after cleaning:', teams_in_talentdb)

    regions_same = 0
    regions_diff = 0
    regions_part = 0
    regions_none = 0
    for t in teams.keys():
        ti = teaminfo[t]
        regs = len(ti[TI_REGIONS])
        all_regs = ti[TI_WITH_REG]
        team_size = len(teams[t])
        if regs == 0:
            regions_none += 1
            ti[TI_REGIONS] = 0
        elif regs == 1:
            if all_regs >= team_size / 2:
                regions_same += 1
                ti[TI_REGIONS] = 2
            else:
                regions_part += 1
                ti[TI_REGIONS] = 1
        else:
            if all_regs >= team_size / 2:
                regions_diff += 1
                ti[TI_REGIONS] = 3
            else:
                regions_part += 1
                ti[TI_REGIONS] = 1

    if USE_TOPICS:
        teams_by_topics = {}
        for t in teams:
            origin, event = teaminfo[t][0:2]
            tops = event_topics[origin][event]
            for top in tops:
                if top not in teams_by_topics:
                    teams_by_topics[top] = {}
                o = CONVERT_ORIGIN_NAME(origin)    
                if o not in teams_by_topics[top]:
                    teams_by_topics[top][o] = 0
                teams_by_topics[top][o] += 1

        debug('team topics:')
        for top in sorted(teams_by_topics.keys()):
            tt = teams_by_topics[top]
            project_parts = []
            if 'ПБ' in tt:
                project_parts.append('ПБ ' + str(tt['ПБ']))
            if 'Rukami' in tt:
                project_parts.append('Rukami ' + str(tt['Rukami']))
            debug('{}:{}:{}'.format(top,
                                    tt['ОНТИ'] if 'ОНТИ' in tt else '',
                                    ','.join(project_parts)))
    teamsizes = {}
    teamsizes_onti = {}
    teamsizes_pb = {}
    teamsizes_rest = {}
    for t,e in teams.items():
        origin, event = teaminfo[t][0:2]
        num = len(e)
        if num in teamsizes:
            teamsizes[num] += 1
        else:
            teamsizes[num] = 1
        if origin.find('ОНТИ') == 0:
            if num in teamsizes_onti:
                teamsizes_onti[num] += 1
            else:
                teamsizes_onti[num] = 1
        elif origin.find('ПБ') == 0:
            if num in teamsizes_pb:
                teamsizes_pb[num] += 1
            else:
                teamsizes_pb[num] = 1
        else:
            if num in teamsizes_rest:
                teamsizes_rest[num] += 1
            else:
                teamsizes_rest[num] = 1

    debug()
    if len(teams) > 0:
        debug('teams with the same region:', regions_same, int(100.0 * float(regions_same) / float(len(teams))), '%')
        debug('teams with diff regions:', regions_diff, int(100.0 * float(regions_diff) / float(len(teams))), '%')
        debug('teams with bad region info:', regions_part, int(100.0 * float(regions_part) / float(len(teams))),'%')
        debug('teams with w/o region:', regions_none, int(100.0 * float(regions_none) / float(len(teams))), '%')
    debug()
    debug('team types:')
    debug('onti', teams_onti)
    debug('pb', teams_pb)
    debug('rest', teams_rest)
                
    debug()
    debug('team sizes:')
    for num in sorted(teamsizes.keys(), reverse=True):
        debug('{}: {}'.format(num, teamsizes[num]))
    debug()
    debug('onti team sizes:')
    for num in sorted(teamsizes_onti.keys(), reverse=True):
        debug('{}: {}'.format(num, teamsizes_onti[num]))
    debug()
    debug('pb team sizes:')
    for num in sorted(teamsizes_pb.keys(), reverse=True):
        debug('{}: {}'.format(num, teamsizes_pb[num]))
    debug()
    debug('rest team sizes:')
    for num in sorted(teamsizes_rest.keys(), reverse=True):
        debug('{}: {}'.format(num, teamsizes_rest[num]))

    if USE_GITHUB:
        debug()
        debug('github teams:')
        gh_once = 0
        gh_all = 0
        for t,e in teams.items():
            check_once = False
            check_all = True
            for email in e:
                if email in githubs:
                    check_once = True
                else:
                    check_all = False
            if check_once:
                gh_once += 1
            if check_all:
                gh_all += 1
        debug('github present teams:', gh_once)
        debug('github whole teams:', gh_all)

    return teams, teaminfo, emails, event_topics

# ------------------------------------------------------------------------------
# Graph construction
# ------------------------------------------------------------------------------

def early_team(t1, t2, teaminfo):
    ti1 = teaminfo[t1]
    ti2 = teaminfo[t2]
    t1origin, t1event = ti1[0:2]
    t2origin, t2event = ti2[0:2]
    t1origininfo = TeamOrigins[t1origin]
    t2origininfo = TeamOrigins[t2origin]
    t1date = t1origininfo['dates'] if isinstance(t1origininfo['dates'], datetime.date) else t1origininfo['dates'][t1event] 
    t2date = t2origininfo['dates'] if isinstance(t2origininfo['dates'], datetime.date) else t2origininfo['dates'][t2event]
    if t1date <= t2date:
        return t1
    else:
        return t2

sex_color_cache = {}
def get_sex_color(teaminfo):
    fem = teaminfo[TI_FEMALE]
    sex = teaminfo[TI_SEX]
    if sex == 0:
        return 'grey'
    key = fem + sex * 100
    if key in sex_color_cache:
        return sex_color_cache[key]
    fem_prop = float(fem) / sex
    #fem_prop = random.random()
    if fem_prop <= 0.5:
        color = "#{:02x}{:02x}{:02x}".format(int(255.0 * 2.0 * fem_prop), 0, 255)
    else:
        color = "#{:02x}{:02x}{:02x}".format(255, 0, int(255.0 * 2.0 * (1.0 - fem_prop)))
    sex_color_cache[key] = color
    return color

# reg_color_cache = {}
def get_reg_color(teaminfo):
    num = teaminfo[TI_REGIONS]
    if num == 0:
        return 'grey'
    elif num == 1:
        return '#7a16ff'
    elif num >= 2:
        return '#3badff'
    else:
        assert False
        # if num in reg_color_cache:
        #     return reg_color_cache[num]
        # if num > 6:
        #     num = 6
        # green = 255.0 * (1.0 - float(num - 1) / 5.0)
        # blue = 255.0 * float(num - 1) / 5.0
        # color = "#{:02x}{:02x}{:02x}".format(0, int(green), int(blue))
        # reg_color_cache[num] = color

def build_graph(teams, teaminfo, emails, regions, event_topics, autoteams):
    team_graph_edges = {}
    matched_emails = {}
    g = None
    teamindexes = {}

    if BUILD_GRAPH:
        g = igraph.Graph(directed=True)

    debug('calculating graph...')
    # rich O(N^2) algorithm
    for t1,t1emails in teams.items():

        ti1 = teaminfo[t1]
        t1origin = ti1[TI_ORIGIN]
        t1event = ti1[TI_EVENT]
        t1name = ti1[TI_TEAM_LABEL]
        t1origininfo = TeamOrigins[t1origin]
        if SKIP_SELECTION:
            t1origintype = t1origininfo['type']
            t1originselection = t1origininfo['selections']
            t1originyear = t1origininfo['season']
        if BUILD_GRAPH:
            t1level = t1origininfo['level']
            if COLOR_SCHEME == 'events':
                t1color = t1origininfo['color']
            elif COLOR_SCHEME == 'sex':
                t1color = get_sex_color(ti1)
            elif COLOR_SCHEME == 'reg':
                t1color = get_reg_color(ti1)
            else:
                assert False, "bad color scheme {}".format(COLOR_SCHEME)
            t1date = t1origininfo['dates'] if isinstance(t1origininfo['dates'], datetime.date) else t1origininfo['dates'][t1event] 

        for t2,t2emails in teams.items():
            
            if t1 == t2:
                continue
            
            ti2 = teaminfo[t2]
            t2origin = ti2[TI_ORIGIN]
            t2event = ti2[TI_EVENT]
            t2origininfo = TeamOrigins[t2origin]
            if BUILD_GRAPH:
                t2name = ti2[3]
                t2level = t2origininfo['level']
                if COLOR_SCHEME == 'events':
                    t2color = t2origininfo['color']
                elif COLOR_SCHEME == 'sex':
                    t2color = get_sex_color(ti2)
                elif COLOR_SCHEME == 'reg':
                    t2color = get_reg_color(ti2)
                else:
                    assert False, "bad color scheme {}".format(COLOR_SCHEME)
                t2date = t2origininfo['dates'] if isinstance(t2origininfo['dates'], datetime.date) else t2origininfo['dates'][t2event]

            if t1origin == t2origin and t1event == t2event:
                # skip team interconnections in the common event
                continue
            if FILTER_ORIGIN and t1origin not in FILTER_ORIGIN and t2origin not in FILTER_ORIGIN:
                # if origin filter is set skip the rest
                continue

            common_emails = t1emails & t2emails
            common_len = len(common_emails)
            if common_len >= TEAM_SIZE:
                key = sorted((t1, t2))
                keyhash = hash(str(key))
                emailshash = hash(','.join(map(str, sorted(common_emails))))
                if keyhash not in team_graph_edges:
                    team_graph_edges[keyhash] = key
                if emailshash not in matched_emails:
                    matched_emails[emailshash] = (common_emails, set([keyhash]))
                else:
                    matched_emails[emailshash][1].add(keyhash)
            
            if SKIP_SELECTION:
                t2origintype = t2origininfo['type']
                t2originyear = t2origininfo['season']

                # skip connections between selection stages and final stages
                if t1origintype == 'onti' and t2origintype == 'onti' and t1originyear == t2originyear:
                    continue
                
                if t1origin == t2origin and t1origintype != 'onti' and t1originselection:
                    check_array = sorted((t1event, t2event))
                    if check_array[0] in t1originselection and check_array[1] == t1originselection[check_array[0]]:
                        continue

            if BUILD_GRAPH and (FULL_GRAPH and common_len > 0 or
                                not FULL_GRAPH and common_len >= TEAM_SIZE):
                if t1 not in teamindexes:
                    v = g.add_vertex()
                    teamindexes[t1] = t1idx = v.index
                    t1origin = teaminfo[t1][TI_ORIGIN]
                    if PLOT_LABELS:
                        v['label'] = t1name
                        v['label_color'] = LABELS_COLOR
                    v['color'] = t1color
                    v['size'] = len(t1emails)
                    v['team'] = t1
                else:
                    t1idx = teamindexes[t1]
                if t2 not in teamindexes:
                    v = g.add_vertex()
                    teamindexes[t2] = t2idx = v.index
                    t2origin = teaminfo[t2][TI_ORIGIN]
                    if PLOT_LABELS:
                        v['label'] = t2name
                        v['label_color'] = LABELS_COLOR
                    v['color'] = t2color
                    v['size'] = len(t2emails)
                    v['team'] = t2
                else:
                    t2idx = teamindexes[t2]
                if t1date < t2date:
                    e = g.add_edge(t1idx, t2idx)
                else:
                    e = g.add_edge(t2idx, t1idx)
                e['weight'] = len(common_emails)
                e['color'] = EDGES_COLOR

    if BUILD_GRAPH:
        debug()
        debug('graph size: v {} e {}'.format(g.vcount(), g.ecount()))            
        debug('teams in graph', len(teamindexes))

        if CALCULATE_CLUSTERS:
            debug('calculating clusters...')
            c = g.clusters(igraph.WEAK)
            debug('clusters:', len(c))
            giant = c.giant()
            debug('the giant cluster: v {} e {}'.format(giant.vcount(), giant.ecount()))

            giant_students = set([])
            for t in giant.vs['team']:
                assert t in teams
                for e in teams[t]:
                    if not e in giant_students:
                        giant_students.add(e)
        
            debug('the giant cluster students:', len(giant_students))

    # counters
    matches = {}
    matches_onti = {}
    matches_pb = {}
    matches_onti_plus_pb = {}
    matches_pb_plus_onti = {}
    paths = {}
    paths_onti = {}

    debug()
    debug('building output...')
    teamids = set([])
    csv_data = []

    teams_by_topics_int = {}
    teams_by_topics_union = {}

    topics_int_start = {}
    topics_union_start = {}

    mixed_paths = 0
    finals_2021_num = 0
    onti_only = 0
    pb_only = 0
    
    double_onti = []
    onti_plus_pb = []
    pb_plus_onti = []
    events_34 = []
    events_5plus = []
    events_3_in_4 = []
    formal_final = []
    matches2 = []
    matches3 = []
    matches4 = []
    matches5plus = []

    for eh, keyhashes in matched_emails.items():
        m_emails = tuple(keyhashes[0])
        num = len(m_emails)
        if num in matches:
            matches[num] += 1
        else:
            matches[num] = 1
        teams_to_print = set([])
        start_team = None
        for keyhash in tuple(keyhashes[1]):
            teamkey = team_graph_edges[keyhash]
            t1, t2 = teamkey
            if start_team is None:
                start_team = early_team(t1, t2, teaminfo)
            else:
                if t1 not in teams_to_print:
                    start_team = early_team(t1, start_team, teaminfo)
                if t2 not in teams_to_print:
                    start_team = early_team(t2, start_team, teaminfo)
            teams_to_print.add(t1)
            teams_to_print.add(t2)

        if FILTER_PARTICIPANT:
            for eml in m_emails:
                if emails[eml] == FILTER_PARTICIPANT:
                    path = []
                    for t in teams_to_print:
                        ti = teaminfo[t]
                        path.append(ti[TI_ORIGIN]+'-'+ti[TI_EVENT])
                    debug("participant's team paths:",' '.join(path))
    
        num2 = len(teams_to_print)

        # multiple events
        # ONTI finals
        # formal teams in finals
        origins = set([])
        onti_seasons = set([])
        onti_autoteams = set([])
        onti_finals = set([])
        onti_full_seasons = set([])
        final_re = re.compile('ОНТИ.*\(Ф\)')
        final_2021 = False
        for t in teams_to_print:
            ti = teaminfo[t]
            origin = ti[TI_ORIGIN]
            if origin.find('ОНТИ') == 0:
                origins.add('ОНТИ')
                season = TeamOrigins[origin]['season']
                if final_re.match(origin):
                    onti_finals.add(season)
                    if season == 2021:
                        final_2021 = True
                if season in onti_seasons:
                    onti_full_seasons.add(season)
                else:
                    onti_seasons.add(season)
                    if ti[TI_TALENT_TEAM] and ti[TI_TALENT_TEAM] in autoteams:
                        onti_autoteams.add(season)
            else:
                origins.add(origin)
        target_num = num2 - len(onti_full_seasons)
        if final_2021:
            finals_2021_num += 1
        if 'ОНТИ' in origins:
            if len(origins) == 1:
                if target_num >= 3:
                    if num in matches_onti:
                        matches_onti[num] += 1
                    else:
                        matches_onti[num] = 1
                onti_only += 1
            if len(origins) >= 2:
                mixed_paths += 1
        if 'ПБ' in origins and len(origins) == 1:
            pb_only += 1
            if target_num >= 3:
                if num in matches_pb:
                    matches_pb[num] += 1
                else:
                    matches_pb[num] = 1
        if len(onti_finals) >= 2:
            double_onti.append((m_emails, teams_to_print))
        if len(onti_autoteams & onti_finals) > 0:
            formal_final.append((m_emails, teams_to_print))

        if target_num >= 2:
            if num == 2:
                matches2.append((m_emails, teams_to_print))
            elif num == 3:
                matches3.append((m_emails, teams_to_print))
            elif num == 4:
                matches4.append((m_emails, teams_to_print))
            elif num >= 5:
                matches5plus.append((m_emails, teams_to_print))

            if 3 <= target_num <= 4:
                events_34.append((m_emails, teams_to_print))
            elif target_num >= 5:
                events_5plus.append((m_emails, teams_to_print))

        if target_num >= 4 and num >= 3:
            diff_regs = set([])
            for eml in m_emails:
                eml2 = emails[eml]
                if eml2 in regions:
                    reg = regions[eml2]
                    diff_regs.add(reg)
            if len(diff_regs) >= 2:
                events_3_in_4.append((m_emails, teams_to_print))

        # NTI+PB
        start_ti = teaminfo[start_team]
        start_origin = start_ti[TI_ORIGIN]
        onti_first = start_origin.find('ОНТИ') == 0
        was_onti = onti_first
        was_pb = False
        for t in teams_to_print:
            ti = teaminfo[t]
            origin = ti[TI_ORIGIN]
            if not was_onti and origin.find('ОНТИ') == 0:
                was_onti = True
            if not was_pb and origin == 'ПБ':
                was_pb = True
        if was_onti and was_pb:
            if onti_first:
                onti_plus_pb.append((m_emails, teams_to_print))
                if target_num >= 3:
                    if num in matches_onti_plus_pb:
                        matches_onti_plus_pb[num] += 1
                    else:
                        matches_onti_plus_pb[num] = 1
            else:
                pb_plus_onti.append((m_emails, teams_to_print))
                if target_num >= 3:
                    if num in matches_pb_plus_onti:
                        matches_pb_plus_onti[num] += 1
                    else:
                        matches_pb_plus_onti[num] = 1

        if num2 in paths:
            paths[num2] += 1
        else:
            paths[num2] = 1
        if target_num in paths_onti:
            paths_onti[target_num] += 1
        else:
            paths_onti[target_num] = 1
            
        start_origin, start_event = teaminfo[start_team][0:2]

        if USE_TOPICS:
            start_origin_top = event_topics[start_origin][start_event]

            topics_int = set([])
            topics_union = set([])
            first = True
            for teamkey in tuple(teams_to_print):
                origin, event = teaminfo[teamkey][0:2]
                et = event_topics[origin][event]
                date = TeamOrigins[origin]['dates']
                if not isinstance(date, datetime.date):
                    date = date[event]
                if first:
                    topics_int = topics_union = et
                    first = False
                else:
                    topics_int = topics_int & et
                    topics_union = topics_union | et
                
            o1 = CONVERT_ORIGIN_NAME(start_origin)
            for top in topics_int:
                if top not in teams_by_topics_int:
                    teams_by_topics_int[top] = 0
                    teams_by_topics_int[top] += 1
                if top not in topics_int_start:
                    topics_int_start[top] = {}
                if o1 not in topics_int_start[top]:
                    topics_int_start[top][o1] = 0
                    topics_int_start[top][o1] += 1
            for top in topics_union:
                if top not in teams_by_topics_union:
                    teams_by_topics_union[top] = 0
                    teams_by_topics_union[top] += 1
                if top not in topics_union_start:
                    topics_union_start[top] = {}
                if o1 not in topics_union_start[top]:
                    topics_union_start[top][o1] = 0
                    topics_union_start[top][o1] += 1

        if SAVE_CSV:
            # output matches
            data = []
            email_list = '|'.join(map(lambda eml: emails[eml], m_emails))
            team_id = hex(abs(hash(email_list)))[2:]
            assert team_id not in teamids
            teamids.add(team_id)
            data.append(team_id)
            data.append(len(m_emails))
            data.append(email_list)
            origins = []
            events = []
            teamnames = []
            for teamkey in tuple(teams_to_print):
                origin, event, teamname = teaminfo[teamkey][0:3]
                origins.append(origin)
                events.append(event)
                teamnames.append(teamname)
                data.append(len(origins))
                data.append('|'.join(origins))
                data.append('|'.join(events))
                data.append('|'.join(teamnames))
                csv_data.append(data)
        else:
            csv_data.append(1)

    debug()
    debug('matches teams:', len(csv_data))
    debug('matches team size:')
    for num in sorted(matches.keys(), reverse=True):
        debug('{}: {}'.format(num, matches[num]))
    debug('matches 3+ events team size (ONTI only):')
    for num in sorted(matches_onti.keys(), reverse=True):
        debug('{}: {}'.format(num, matches_onti[num]))
    debug('matches 3+ events team size (PB only):')
    for num in sorted(matches_pb.keys(), reverse=True):
        debug('{}: {}'.format(num, matches_pb[num]))
    debug('matches 3+ events team size (ONTI->PB):')
    for num in sorted(matches_onti_plus_pb.keys(), reverse=True):
        debug('{}: {}'.format(num, matches_onti_plus_pb[num]))
    debug('matches 3+ events team size (PB->ONTI):')
    for num in sorted(matches_pb_plus_onti.keys(), reverse=True):
        debug('{}: {}'.format(num, matches_pb_plus_onti[num]))
    debug('events 3 in 4 + reg 2+:', len(events_3_in_4))
    debug('team sequences:')
    plus3 = 0
    for num in sorted(paths.keys(), reverse=True):
        if num > 2:
            plus3 += paths[num]
        debug('{}: {} ({})'.format(num, paths[num], paths_onti[num] if num in paths_onti else 0))
    debug('3+: {}'.format(plus3))
    debug()
    debug('ONTI+x: {}'.format(mixed_paths))
    debug('ONTI-f-2021: {}'.format(finals_2021_num))

    debug('only ONTI: {}'.format(onti_only))
    debug('only PB: {}'.format(pb_only))
    debug('double ONTI finals: {}'.format(len(double_onti)))
    debug('ONTI+PB: {}'.format(len(onti_plus_pb)))
    debug('PB+ONTI: {}'.format(len(pb_plus_onti)))
    debug('3-4 events: {}'.format(len(events_34)))
    debug('5+ events: {}'.format(len(events_5plus)))
    debug('ONTI final with formal teams: {}'.format(len(formal_final)))
    debug('matches 2+ events of 2 teams: {}'.format(len(matches2)))
    debug('matches 2+ events of 3 teams: {}'.format(len(matches3)))
    debug('matches 2+ events of 4 teams: {}'.format(len(matches4)))
    debug('matches 2+ events of 5+ teams: {}'.format(len(matches5plus)))

    sets_to_export = {
        1: events_3_in_4
        # 1: double_onti,
        # 2: onti_plus_pb,
        # 3: pb_plus_onti,
        # 4: events_34,
        # 5: events_5plus,
        # 6: formal_final,
        # 7: matches2,
        # 8: matches3,
        # 9: matches4,
        # 10: matches5plus,        
    }
    nontalent_teams_to_export = []
    nontalent_num = 1
    data_to_export = []
    for s, tms in sets_to_export.items():
        match_num = 0
        for match_emails, teamgroups in tms:
            data = []
            data.append(s)
            data.append(match_num)
            data.append(len(match_emails))
            match_num += 1
            for t in teamgroups:
                ti = teaminfo[t]
                if ti[TI_TALENT_TEAM]:
                    data.append(ti[TI_TALENT_TEAM])
                else:
                    data.append('N{}'.format(nontalent_num))
                    emls = []
                    for e in teams[t]:
                        emls.append(emails[e])
                    new_team = [nontalent_num] + ti[0:3] + [len(emls)] + emls
                    nontalent_teams_to_export.append(new_team)
                    nontalent_num += 1
            data_to_export.append(data)

    if USE_TOPICS:
        debug('matches team topics:')
        for top in sorted(teams_by_topics_union.keys()):
            parts1 = []
            parts2 = []
            for o in ('ОНТИ', 'ПБ', 'Rukami'):
                if top in topics_int_start and o in topics_int_start[top]:
                    parts1.append(o + ' ' + str(topics_int_start[top][o]))
                if top in topics_union_start and o in topics_union_start[top]:
                    parts2.append(o + ' ' + str(topics_union_start[top][o]))
                debug('{}:{} ({}):{} ({})'.format(top,
                                                  teams_by_topics_union[top],
                                                  ','.join(parts2),
                                                  teams_by_topics_int[top] if top in teams_by_topics_int else '',
                                                  ','.join(parts1)))
    data = {}            
    if SAVE_CSV:
        data['csv'] = csv_data
    data['results'] = data_to_export
    data['teams'] = nontalent_teams_to_export
    return g, data

def plot_graph(g, filenames):
    visual_style = {}
    # Set bbox and margin
    visual_style["bbox"] = (PICTURE_SIZE, PICTURE_SIZE)
    visual_style["margin"] = 15
    visual_style["edge_curved"] = False
    visual_style["edge_width"] = [1 + 4 * (w - 1) for w in g.es['weight']]
    visual_style["vertex_size"] = [20 + 5 * (s - 2) for s in g.vs['size']]
    debug('building fruchterman reingold layout...')
    visual_style["layout"] = g.layout_fruchterman_reingold(grid="nogrid")

    for filename in filenames:
        debug('plotting {}...'.format(filename))
        igraph.plot(g, filename, **visual_style)

if __name__ == '__main__':

    init_teams()
    debug()
    debug('1. reading teams data...')
    r = read_regions(REGIONS_FILE)
    s = read_sex(SEX_FILE)
    c = read_colors(COLORS_FILE)
    if USE_GITHUB:
        g = read_githubs(GITHUBS_FILE)
    else:
        g = set([])
    a = read_autoteams(AUTOTEAMS_FILE)
    debug()
    
    if ALL_REGIONS:
        debug('2. building reg team graphs...')
        for i in range(99):
            reg = i + 1
            FILTER_REGIONS = [reg]
            t, ti, e, et = read_teams(r, g, s, c)
            num_t = len(t)
            debug('--------------------------------------------------------------------------------')
            debug('reg {}: teams {}'.format(reg, num_t))
            if num_t == 0:
                continue
            if num_t <= 10:
                PICTURE_SIZE = 500
            elif num_t <= 50:
                PICTURE_SIZE = 1000
            else:
                PICTURE_SIZE = 2000
            graph, _ = build_graph(t, ti, e, r, et, a)
            if graph.ecount() == 0:
                continue
            if BUILD_GRAPH and PLOT_GRAPH:
                targets = []
                if SAVE_SVG:
                    targets.append(RESULT_REGS_SVG.format(reg))
                if SAVE_PNG:
                    targets.append(RESULT_REGS_PNG.format(reg))
                if len(targets) > 0:
                    plot_graph(graph, targets)
    else:
        t, ti, e, et = read_teams(r, g, s, c)
        debug('2. building team graph...')
        graph, data = build_graph(t, ti, e, r, et, a)
        debug()
        debug('3. saving results...')
        if SAVE_CSV:
            save_csv(RESULT_CSV, data['csv'])
            save_csv(RESULT_CSV, data['results'])
            save_csv(RESULT_TEAMS_CSV, data['teams'])
        if BUILD_GRAPH and PLOT_GRAPH:
            targets = []
            if SAVE_SVG:
                targets.append(RESULT_SVG)
            if SAVE_PNG:
                targets.append(RESULT_PNG)
            if len(targets) > 0:
                plot_graph(graph, targets)
