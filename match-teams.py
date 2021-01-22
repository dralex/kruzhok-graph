#!/usr/bin/python3
# ------------------------------------------------------------------------------
# Kruzhok Movement teams matching tool
#
# Alexey Fedoseev <aleksey@fedoseev.net>, 2020
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
BUILD_GRAPH = True
CALCULATE_CLUSTERS = False
PLOT_GRAPH = False
FULL_GRAPH = True
FILTER_REGIONS = []
SAVE_CSV = True
SKIP_SELECTION = False
RESULT_CSV = 'result.csv'
RESULT_PNG = 'graph.png'
RESULT_SVG = 'graph.svg'
PICTURE_SIZE = 4000
TEAM_NAME_LIMIT = 15
FILTER_ORIGIN = None
DATADIR = 'data'
REGIONS_FILE = join(DATADIR, 'regions.csv')

# ------------------------------------------------------------------------------
# Data structure
# ------------------------------------------------------------------------------

TeamOrigins = {
    'ПБ':{
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'pb-teams-2-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'pb-dates.csv'),
        'color': 'red',
        'selections': {'Полуфинал MultiTechBattle': 'Финал MultiTechBattle',
                       '2 этап Skolkovo Junior Challenge-2020': 'Финал Skolkovo Junior Challenge 2020'},
        'limit': None
    },
    'KRUZHOK.PRO': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'kruzhokpro-teams-hash.csv'),
        'level': 1,
        'dates': join(DATADIR, 'kruzhokpro-dates.csv'),
        'color': 'orange',
        'selections': None,
        'limit': None
    },
    'Архипелаг 20.35': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'archipelago-teams-hash.csv'),
        'level': 1,
        'dates': datetime.date(2020, 11, 12),
        'color': 'red',
        'selections': None,
        'limit': None
    },
    'МПШ': {
        'active': True,
        'type': 'projects',
        'season': None,
        'teams': join(DATADIR, 'pb-mpsh-teams-hash.csv'),
        'level': 1,
        'dates': datetime.date(2019, 8, 12),
        'color': 'red',
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
        'color': 'blue4',
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
        'color': 'blue',
        'selections': 'ОНТИ-2018/19(2)',
        'limit': 6
    },
    'ОНТИ-2019/20(2)': {
        'active': True,
        'type': 'onti',
        'season': 2019,
        'teams': join(DATADIR, 'onti-teams-1920-hash.csv'),
        'level': 2,
        'dates': datetime.date(2019, 11, 15),
        'color': 'green4',
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
        'color': 'green',
        'selections': 'ОНТИ-2019/20(2)',
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
}

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

def save_csv(fname, data):
    debug('saving csv {}...'.format(fname))
    with open(fname, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=';',
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

def read_teams(regions):
    participants = []
    for origin,data in TeamOrigins.items():
        if not data['active']:
            continue
        participants += read_participants(data['teams'],
                                          origin)
    debug('participants:', len(participants))
    
    all_events = {}

    teaminfo = {}
    teams = {}
    emails = {}
    has_regions = 0
    reg_filter = 0

    for p in participants:
        email, origin, event, team = p

        origininfo = TeamOrigins[origin]

        # check date costistency
        if origin not in all_events:
            all_events[origin] = set([])
            assert (isinstance(origininfo['dates'], datetime.date) or
                    event in origininfo['dates']), 'no date available for event {}:{}'.format(origin, event)
        all_events[origin].add(event)
        
        emailhash = hash(email)
        teamhash = hash(origin + event + team)
        teaminfo[teamhash] = list(p[1:]) + [team if len(team) < TEAM_NAME_LIMIT else team[0:TEAM_NAME_LIMIT] + '...']
        
        if teamhash not in teams:
            teams[teamhash] = set([])
        teams[teamhash].add(emailhash)
            
        if emailhash not in emails:
            emails[emailhash] = email
            if email in regions:
                has_regions += 1
                if FILTER_REGIONS and regions[email] in FILTER_REGIONS:
                    reg_filter += 1

    debug('events:')
    for o,events in all_events.items():
        debug('\t{}: {}'.format(o, len(events)))
    debug('students:', len(emails))
    debug('students with regions:', has_regions)
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

    return teams, teaminfo, emails

# ------------------------------------------------------------------------------
# Graph construction
# ------------------------------------------------------------------------------

def build_graph(teams, teaminfo, emails, regions):
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
            if BUILD_GRAPH:
                t2name = ti2[3]
                t2origininfo = TeamOrigins[t2origin]
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
    for eh, keyhashes in matched_emails.items():
        m_emails = tuple(keyhashes[0])
        num = len(m_emails)
        if num in matches:
            matches[num] += 1
        else:
            matches[num] = 1
        teams_to_print = set([])
        for keyhash in tuple(keyhashes[1]):
            teamkey = team_graph_edges[keyhash]
            t1, t2 = teamkey
            teams_to_print.add(t1)
            teams_to_print.add(t2)
        num2 = len(teams_to_print)
        if num2 in paths:
            paths[num2] += 1
        else:
            paths[num2] = 1

        if not SAVE_CSV:
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
    for num in sorted(paths.keys(), reverse=True):
        debug('{}: {}'.format(num, paths[num]))

    return g, csv_data

def plot_graph(g, filename):
    visual_style = {}
    # Set bbox and margin
    visual_style["bbox"] = (PICTURE_SIZE, PICTURE_SIZE)
    visual_style["margin"] = 15
    visual_style["edge_curved"] = False
    visual_style["edge_width"] = [1 + 4 * (w - 1) for w in g.es['weight']]
    visual_style["vertex_size"] = [20 + 5 * (s - 2) for s in g.vs['size']]
    visual_style["layout"] = g.layout_fruchterman_reingold(grid="nogrid")

    debug('plotting {}...'.format(filename))
    igraph.plot(g, filename, **visual_style)

if __name__ == '__main__':

    init_teams()
    r = read_regions(REGIONS_FILE)
    t, ti, e = read_teams(r)
    graph, data = build_graph(t, ti, e, r)
    if SAVE_CSV:
        save_csv(RESULT_CSV, data)
    if BUILD_GRAPH:
        if PLOT_GRAPH:
            plot_graph(graph, RESULT_PNG)
            plot_graph(graph, RESULT_SVG)
