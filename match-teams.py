#!/usr/bin/python3
# ------------------------------------------------------------------------------
# Kruzhok Movement teams matching tool
#
# Alexey Fedoseev <aleksey@fedoseev.net>, 2020-2022
# ------------------------------------------------------------------------------

import csv
import igraph
import datetime
from os.path import join

# ------------------------------------------------------------------------------
# Global constants and flags
# ------------------------------------------------------------------------------

DEBUG = True
TEAM_SIZE = 2
USE_GITHUB = True
BUILD_GRAPH = True
CALCULATE_CLUSTERS = True
PLOT_GRAPH = False
FULL_GRAPH = True
USE_TOPICS = False
FILTER_REGIONS = []
SAVE_CSV = False
SKIP_SELECTION = False
RESULT_CSV = 'result.csv'
RESULT_PNG = 'graph.png'
RESULT_SVG = 'graph.svg'
PICTURE_SIZE = 4000
TEAM_NAME_LIMIT = 15
FILTER_ORIGIN = None
DATADIR = 'data'
REGIONS_FILE = join(DATADIR, 'regions.csv')
TOPICS_FILE = join(DATADIR, 'topics.csv')
EVENT_TOPICS_FILE = join(DATADIR, 'events-topics.csv')
GITHUBS_FILE = join(DATADIR, 'github-users.csv')
RUKAMI_REST_TOPIC = 'Прочее'

# ------------------------------------------------------------------------------
# Data structure
# ------------------------------------------------------------------------------

TeamOrigins = {
    'ПБ':{
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'talent-pb-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-pb-dates.csv'),
        'color': 'red',
        'selections': None,
        'limit': 10
    },
    'KRUZHOK.PRO': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'talent-kruzhokpro-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-kruzhokpro-dates.csv'),
        'color': 'red4',
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
        'color': 'red3',
        'selections': None,
        'limit': None
    },
    'МОРРОБ': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'talent-sea-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'talent-sea-dates.csv'),
        'color': 'purple',
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
        'color': 'purple',
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
        'color': 'purple',
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
        'color': 'purple',
        'selections': None,
        'limit': None
    },
    'ОНТИ-2018/19(2)': {
        'active': True,
        'type': 'onti',
        'season': 2018,
        'teams': join(DATADIR, 'onti-teams-1819-hash.csv'),
        'level': 2,
        'dates': datetime.date(2018, 11, 15),
        'color': 'blue',
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
        'color': 'blue3',
        'selections': 'ОНТИ-2018/19(2)',
        'limit': 6
    },
    'ОНТИ-СТУД-2018/19(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2018,
        'teams': join(DATADIR, 'onti-stud-teams-1819-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2019, 3, 1),
        'color': 'blue4',
        'selections': None,
        'limit': 6
    },
    'ОНТИ-2019/20(2)': {
        'active': True,
        'type': 'onti',
        'season': 2019,
        'teams': join(DATADIR, 'onti-teams-1920-hash.csv'),
        'level': 2,
        'dates': datetime.date(2019, 11, 15),
        'color': 'green',
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
        'color': 'green3',
        'selections': 'ОНТИ-2019/20(2)',
        'limit': 6
    },
    'ОНТИ-СТУД-2019/20(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2019,
        'teams': join(DATADIR, 'onti-stud-teams-1920-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2020, 3, 1),
        'color': 'green4',
        'selections': None,
        'limit': 6
    },
    'ОНТИ-2020/21': {
        'active': True,
        'type': 'onti',
        'season': 2020,
        'teams': join(DATADIR, 'onti-teams-2021-hash.csv'),
        'level': 2,
        'dates': datetime.date(2020, 11, 15),
        'color': 'yellow',
        'selections': None,
        'limit': 6
    },
    'ОНТИ-2020/21(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2020,
        'teams': join(DATADIR, 'onti-teams-2021-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2021, 3, 1),
        'color': 'gold',
        'selections': 'ОНТИ-2020/21',
        'limit': 6
    },
    'ОНТИ-СТУД-2020/21(Ф)': {
        'active': True,
        'type': 'onti',
        'season': 2020,
        'teams': join(DATADIR, 'onti-stud-teams-2021-f-hash.csv'),
        'level': 1,
        'dates': datetime.date(2021, 3, 1),
        'color': 'orange',
        'selections': None,
        'limit': 6
    },
    'ОНТИ-2021/22': {
        'active': True,
        'type': 'onti',
        'season': 2021,
        'teams': join(DATADIR, 'talent-onti-teams-2122-hash.csv'),
        'level': 2,
        'dates': datetime.date(2021, 11, 15),
        'color': 'white',
        'selections': None,
        'limit': 6
    },
    'ОНТИ-СТУД-2021/22': {
        'active': True,
        'type': 'onti',
        'season': 2021,
        'teams': join(DATADIR, 'talent-onti-teams-stud-2122-hash.csv'),
        'level': 2,
        'dates': datetime.date(2021, 10, 1),
        'color': 'grey',
        'selections': None,
        'limit': 6
    }

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
        if len(row) != 3:
            debug('file {} bad line {}'.format(fname, str(row)))
            continue
        if len(row[2].strip()) > 0:
            participants.append((row[0], prefix, row[1], row[2]))
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

def read_teams(regions, githubs):
    participants = []
    for origin,data in TeamOrigins.items():
        if not data['active']:
            continue
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

    for p in participants:
        email, origin, event, team = p

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
        
        emailhash = hash(email)
        teamhash = hash(origin + event + team)
        teaminfo[teamhash] = [origin, event, team] + [team if len(team) < TEAM_NAME_LIMIT else team[0:TEAM_NAME_LIMIT] + '...']

        if teamhash not in teams:
            teams[teamhash] = set([])
        teams[teamhash].add(emailhash)
            
        if emailhash not in emails:
            emails[emailhash] = email
            if email in regions:
                has_regions += 1
                if FILTER_REGIONS and regions[email] in FILTER_REGIONS:
                    reg_filter += 1
            if USE_GITHUB:
                if emailhash in githubs:
                    has_github += 1
    if USE_TOPICS:
        topics_all, topics = read_topics(TOPICS_FILE)
        event_topics = read_event_topics(EVENT_TOPICS_FILE, topics, all_events)
    else:
        topics_all = event_topics = None
    
    debug('events:')
    for o,events in all_events.items():
        debug('\t{}: {}'.format(o, len(events)))
#        for e in events:
#            debug('\t\t{}: [{}]'.format(e, '|'.join(event_topics[o][e])))
    debug('students:', len(emails))
    debug('students with regions:', has_regions)
    if USE_GITHUB:
        debug('students with github:', has_github)
    if FILTER_REGIONS:
        debug('students with filter {}: {}'.format(FILTER_REGIONS, reg_filter))
    debug('teams:', len(teams))

    # drop bad teams
    
    to_delete = []
    for t,e in teams.items():
        size = len(e)
        origininfo = TeamOrigins[teaminfo[t][0]]
        if size == 1 or origininfo['limit'] and size > origininfo['limit']:
            to_delete.append(t)
        elif FILTER_REGIONS:
            found = False
            for emailhash in e:
                email = emails[emailhash]
                if email in regions and regions[email] in FILTER_REGIONS:
                    found = True
            if not found:
                to_delete.append(t)
    for t in to_delete:
        del teams[t]

    debug('teams after cleaning:', len(teams))

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
    for e in teams.values():
        num = len(e)
        if num in teamsizes:
            teamsizes[num] += 1
        else:
            teamsizes[num] = 1

    debug()
    debug('team sizes:')
    for num in sorted(teamsizes.keys(), reverse=True):
        debug('{}: {}'.format(num, teamsizes[num]))

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

def build_graph(teams, teaminfo, emails, regions, event_topics):
    team_graph_edges = {}
    matched_emails = {}
    teamindexes = {}
    g = igraph.Graph(directed=True)

    debug()
    debug('calculating graph...')
    # rich O(N^2) algorithm
    for t1,t1emails in teams.items():

        ti1 = teaminfo[t1]
        t1origin = ti1[0]
        t1event = ti1[1]
        t1name = ti1[3]
        t1origininfo = TeamOrigins[t1origin]
        if SKIP_SELECTION:
            t1origintype = t1origininfo['type']
            t1originselection = t1origininfo['selections']
            t1originyear = t1origininfo['season']
        if BUILD_GRAPH:
            t1level = t1origininfo['level']
            t1color = t1origininfo['color']
            t1date = t1origininfo['dates'] if isinstance(t1origininfo['dates'], datetime.date) else t1origininfo['dates'][t1event] 

        for t2,t2emails in teams.items():
            
            if t1 == t2:
                continue
            
            ti2 = teaminfo[t2]
            t2origin = ti2[0]
            t2event = ti2[1]
            t2origininfo = TeamOrigins[t2origin]
            if BUILD_GRAPH:
                t2name = ti2[3]
                t2level = t2origininfo['level']
                t2color = t2origininfo['color']
                t2date = t2origininfo['dates'] if isinstance(t2origininfo['dates'], datetime.date) else t2origininfo['dates'][t2event]

            if t1origin == t2origin and t1event == t2event:
                # skip team interconnections in the common event
                continue
            if FILTER_ORIGIN and t1origin != FILTER_ORIGIN and t2origin != FILTER_ORIGIN:
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
                
                if t1origin == t2origin and t1origintype == 'project' and t1originselection:
                    check_array = sorted((t1event, t2event))
                    if check_array[0] in t1originselection and check_array[1] == t1originselection[check_array[0]]:
                        continue

            if BUILD_GRAPH and (FULL_GRAPH and common_len > 0 or
                                not FULL_GRAPH and common_len >= max(t1level, t2level)):
                if t1 not in teamindexes:
                    v = g.add_vertex()
                    teamindexes[t1] = t1idx = v.index
                    t1origin = teaminfo[t1][0]
                    v['label'] = t1name
                    v['color'] = t1color
                    v['size'] = len(t1emails)
                    v['team'] = t1
                else:
                    t1idx = teamindexes[t1]
                if t2 not in teamindexes:
                    v = g.add_vertex()
                    teamindexes[t2] = t2idx = v.index
                    t2origin = teaminfo[t2][0]
                    v['label'] = t2name
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

    if BUILD_GRAPH:
        debug()
        debug('graph size: v {} e {}'.format(g.vcount(), g.ecount()))            

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
    paths = {}
    
    debug()
    debug('building output...')
    teamids = set([])
    csv_data = []

    teams_by_topics_int = {}
    teams_by_topics_union = {}

    topics_int_start = {}
    topics_union_start = {}

    mixed_paths = 0

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

        num2 = len(teams_to_print)
        origins = set([])

        for t in teams_to_print:
            ti = teaminfo[t]
            origin = ti[0]
            if origin.find('ОНТИ') == 0:
                origins.add('ОНТИ')
            else:
                origins.add(origin)

        if 'ОНТИ' in origins and len(origins) >= 2:
            mixed_paths += 1

        if num2 in paths:
            paths[num2] += 1
        else:
            paths[num2] = 1

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

        if not SAVE_CSV:
            csv_data.append(1)
            continue
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

    debug()
    debug('matches teams:', len(csv_data))
    debug('matches team size:')
    for num in sorted(matches.keys(), reverse=True):
        debug('{}: {}'.format(num, matches[num]))
    debug('team sequences:')
    plus3 = 0
    for num in sorted(paths.keys(), reverse=True):
        if num > 2:
            plus3 += paths[num]
        debug('{}: {}'.format(num, paths[num]))
    debug('3+: {}'.format(plus3))
    debug()
    debug('sequences ONTI+x: {}'.format(mixed_paths))

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
    return g, csv_data

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
    if USE_GITHUB:
        g = read_githubs(GITHUBS_FILE)
    else:
        g = set([])
    t, ti, e, et = read_teams(r, g)
    debug()
    debug('2. building team graph...')
    graph, data = build_graph(t, ti, e, r, et)
    debug()
    debug('3. saving results...')
    if SAVE_CSV:
        save_csv(RESULT_CSV, data)
    if BUILD_GRAPH:
        if PLOT_GRAPH:
            plot_graph(graph, [RESULT_PNG, RESULT_SVG])
