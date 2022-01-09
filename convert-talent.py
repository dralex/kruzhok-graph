#!/usr/bin/python3

import csv

DATA_DIR='olddata'
NEW_TEAMS='talent-export.csv'
EMAIL_DOUBLES='emailpairs.csv'

PB_ORIGIN = u'Практики будущего'
ONTI_ORIGIN = u'Национальная технологическая олимпиада (Олимпиада КД НТИ)'
SEA_ORIGIN = u'Инженерные конкурсы и соревнования по морской робототехнике'
TALENT_ORIGIN = u'Талант 20.35'
FUTSCI_ORIGIN = u'Ученые будущего'
KRUZHOKPRO_ORIGIN = u'KRUZHOK.PRO'

EXPORT_NAMES = {
    PB_ORIGIN: 'talent-pb',
    ONTI_ORIGIN: 'talent-onti',
    SEA_ORIGIN: 'talent-sea',
    TALENT_ORIGIN: 'talent-2035-proj',
    FUTSCI_ORIGIN: 'talent-futsci',
    KRUZHOKPRO_ORIGIN: 'talent-kruzhokpro',
}

email_doubles = {}
export_data = {}
export_events = {}
# teams = {}
# participants = {}
# origins = {}
# team_bugs = 0

reader = csv.reader(open('{}/{}'.format(DATA_DIR, EMAIL_DOUBLES)), delimiter=':')
for row in reader:
    if len(row) != 2:
        continue
    eml_orig = row[0]
    eml_subst = row[1]
    email_doubles[eml_subst] = eml_orig

reader = csv.reader(open('{}/{}'.format(DATA_DIR, NEW_TEAMS)), delimiter=':')
for row in reader:
    if len(row) != 8:
        continue
    teamid = int(row[0])
    teamname = row[1]
    eventname = row[2]
    if len(eventname) == 0:
        continue
    eventdate = row[3].split(',')[0]
    eventorigin = row[7]
    firstemail = row[5]
    secondemail = row[6]
    if len(firstemail) > 0:
        email = firstemail
    elif len(secondemail) > 0:
        if secondemail in email_doubles:
            email = email_doubles[secondemail]
        else:
            email = secondemail
    else:
        continue
    if email.find('@') < 0:
        continue
    if len(eventorigin) == 0:
        eventorigin = PB_ORIGIN

    if eventorigin == ONTI_ORIGIN:
        if eventname.find(u'Этап 2') == 0:
            eventname = eventname.split('. ')[1]
            export_name = EXPORT_NAMES[eventorigin] + '-teams-2122'
        elif eventname.find(u'Сбор обратной связи по проведению Урока НТО.') == 0:
            continue
        elif eventname.find(u'Отборочный этап.') == 0:
            export_name = EXPORT_NAMES[eventorigin] + '-teams-stud-2122'
            eventname = eventname.split('. ')[1]
        else:
            assert False, 'Bad event ONTI event name {}'.format(eventname)
    else:
        export_name = EXPORT_NAMES[eventorigin] + '-teams'
        export_event = EXPORT_NAMES[eventorigin] + '-dates'
        if export_event not in export_events:
            export_events[export_event] = {}
        if eventname == u'Региональный хакатон по технологиям искусственного интеллекта «IZH.IT»':
            eventdate = '17.08.2021'
        assert len(eventdate) > 0, teamid
        export_events[export_event][eventname] = eventdate

    if export_name not in export_data:
        export_data[export_name] = []
    export_data[export_name].append((email,eventname,teamname))
    
    # if eventorigin not in origins:
    #     origins[eventorigin] = {}
    # if eventname not in origins[eventorigin]:
    #     origins[eventorigin][eventname] = eventdate
    # if teamid not in teams:
    #     teams[teamid] = (teamname, eventorigin, eventname)
    # if email not in participants:
    #     participants[email] = set([])
    # if teamid in participants[email]:
    #     #print('id {} email {}'.format(teamid, email))
    #     team_bugs += 1
    # participants[email].add(teamid)

for fname,data in export_data.items():
    output = open('{}/{}.csv'.format(DATA_DIR, fname), 'w', newline = '')
    writer = csv.writer(output, delimiter=':',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)        
    for row in data:
        writer.writerow(row)
    output.close()

for fname,dates in export_events.items():
    output = open('{}/{}.csv'.format(DATA_DIR, fname), 'w', newline = '')
    writer = csv.writer(output, delimiter=':',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)        
    for event,date in dates.items():
        writer.writerow([event,date])
    output.close()

# print('Talent teams:')
# print('teams: {}'.format(len(teams)))
# print('team bugs: {}'.format(team_bugs))
# print('participants: {}'.format(len(participants)))

# print('events:')
# for o,evs in origins.items():
#     print('\t{}:'.format(o))
#     for e in evs:
#         print('\t\t{}'.format(e))

