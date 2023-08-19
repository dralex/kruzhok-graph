#!/usr/bin/python3

import csv

DATA_DIR='olddata'
NEW_TEAMS='talent-export.csv'
EMAIL_DOUBLES='emailpairs.csv'
AUTO_TEAMS='talent-autoteams.csv'
IMPORT_DELIMITER=':'

PB_ORIGIN = u'Практики будущего'
ONTI_ORIGIN = u'Национальная технологическая олимпиада (Олимпиада КД НТИ)'
ONTI_ORIGIN_OLD = u'Олимпиада КД НТИ'
SEA_ORIGIN = u'Инженерные конкурсы и соревнования по морской робототехнике'
TALENT_ORIGIN = u'Талант НТО (Талант 20.35)'
TALENT_ORIGIN_OLD = u'Талант 20.35'
FUTSCI_ORIGIN = u'Ученые будущего'
KRUZHOKPRO_ORIGIN = u'KRUZHOK.PRO'
OPENSOURCE_ORIGIN = u'Open Source'
AK_ORIGIN = u'Ассоциация кружков'
VOSTOK_ORIGIN = u'Восток'
PLANET_ORIGIN = u'Дежурный по планете'
ORZ_ORIGIN = u'Открываем Россию заново'

EXPORT_NAMES = {
    PB_ORIGIN: 'talent-pb',
    ONTI_ORIGIN: 'talent-onti',
    SEA_ORIGIN: 'talent-sea',
    TALENT_ORIGIN: 'talent-2035-proj',
    FUTSCI_ORIGIN: 'talent-futsci',
    KRUZHOKPRO_ORIGIN: 'talent-kruzhokpro',
    OPENSOURCE_ORIGIN: 'talent-opensource',
    VOSTOK_ORIGIN: 'talent-vostok',
    PLANET_ORIGIN: 'talent-planet',
    ORZ_ORIGIN: 'talent-orz'
}

DEBUG = True

email_doubles = {}
export_data = {}
export_events = {}
export_autoteams = set([])

if DEBUG:
    rows = 0
    teams = {}
    participants = {}
    origins = {}
    team_bugs = 0

reader = csv.reader(open('{}/{}'.format(DATA_DIR, EMAIL_DOUBLES)), delimiter=IMPORT_DELIMITER)
for row in reader:
    if len(row) != 2:
        continue
    eml_orig = row[0]
    eml_subst = row[1]
    email_doubles[eml_subst] = eml_orig

reader = csv.reader(open('{}/{}'.format(DATA_DIR, NEW_TEAMS)), delimiter=IMPORT_DELIMITER)
for row in reader:
    if len(row) != 10:
        continue
    if row[0] == 'ID':
        continue
    if DEBUG:
        rows += 1

    teamid = int(row[0])
    teamname = row[1]
    byassignment = int(row[2])
    if byassignment:
        export_autoteams.add(teamid)
    eventname = row[3]
    if len(eventname) == 0:
        continue
    eventdate = row[4].split(',')[0]
    eventorigin = row[8]
    firstemail = row[6]
    secondemail = row[7]
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
        if (eventname.find(u'Практики будущего') >= 0 or
            eventname.find(u'Конференция научно-исследовательских проектов Всероссийского атласа почвенных микроорганизмов') == 0):
            eventorigin = PB_ORIGIN
        elif eventname == u'Настоящее будущее. Русская электроника':
            eventorigin = VOSTOK_ORIGIN

    if eventorigin == ONTI_ORIGIN_OLD:
        eventorigin = ONTI_ORIGIN
    if eventorigin == TALENT_ORIGIN_OLD:
        eventorigin = TALENT_ORIGIN
    if eventorigin == u'Лёрнити':
        eventorigin = PB_ORIGIN
    if eventorigin == AK_ORIGIN and eventname == u'Всероссийский конкурс open source проектов школьников и студентов, направление “Создатели”':
        eventorigin = OPENSOURCE_ORIGIN
    if eventorigin == u'Конкурс open source проектов':
        eventorigin = OPENSOURCE_ORIGIN

    if eventorigin == ONTI_ORIGIN:
        season_year = int(eventname[eventname.find('20')+2:eventname.find('20')+4])
        season = '{}{}'.format(season_year, season_year + 1)
        if eventname.find(u'Финал') == 0:
            if eventname.find(u'Студтрек') >= 0:
                export_name = EXPORT_NAMES[eventorigin] + '-teams-stud-' + season + '-f'
            elif eventname.find('Junior') >= 0:
                export_name = EXPORT_NAMES[eventorigin] + '-teams-jun-' + season + '-f'
            else:
                export_name = EXPORT_NAMES[eventorigin] + '-teams-' + season + '-f'                
        elif eventname.find(u'Этап 2') == 0:
            export_name = EXPORT_NAMES[eventorigin] + '-teams-' + season
        elif eventname.find(u'Сбор обратной связи по проведению Урока НТО.') == 0:
            continue
        elif eventname.find(u'Анкета финалиста Олимпиады КД НТИ 2020/2021') == 0:
            continue
        elif eventname.find(u'Отборочный этап.') == 0 or eventname.find(u'Прыжок в финал. Отборочный этап.') == 0:
            export_name = EXPORT_NAMES[eventorigin] + '-teams-stud-' + season
        else:
            assert False, 'Bad event ONTI event name "{}"'.format(eventname)
    elif eventorigin == AK_ORIGIN and eventname == u'Всероссийский конкурс open source проектов школьников и студентов, направление “Контрибьюторы”':
        continue
    elif eventorigin == '':
        continue
    elif eventorigin in EXPORT_NAMES:
        export_name = EXPORT_NAMES[eventorigin] + '-teams'
        export_event = EXPORT_NAMES[eventorigin] + '-dates'
        if export_event not in export_events:
            export_events[export_event] = {}
        if eventname == u'Региональный хакатон по технологиям искусственного интеллекта «IZH.IT»':
            eventdate = '17.08.2021'
        assert len(eventdate) > 0, "Bad event date {} {} {}".format(eventorigin, eventname, teamid)
        export_events[export_event][eventname] = eventdate

    else:
        assert False, 'Bad origin "{}" for "{}"'.format(eventorigin, eventname)

    if export_name not in export_data:
        export_data[export_name] = []
    export_data[export_name].append((email,eventname,teamname,teamid))

    if DEBUG:
        if eventorigin not in origins:
            origins[eventorigin] = {}
        if eventname not in origins[eventorigin]:
            origins[eventorigin][eventname] = eventdate
        if teamid not in teams:
            teams[teamid] = (teamname, eventorigin, eventname)
        if email not in participants:
            participants[email] = set([])
        if teamid in participants[email]:
            #print('id {} email {}'.format(teamid, email))
            team_bugs += 1
        participants[email].add(teamid)

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
    
output = open('{}/{}'.format(DATA_DIR, AUTO_TEAMS), 'w', newline = '')
writer = csv.writer(output, delimiter=':',
                    quotechar='"', quoting=csv.QUOTE_MINIMAL)        
for teamid in export_autoteams:
    writer.writerow([teamid,])
output.close()

if DEBUG:
    print('Talent rows: {}'.format(rows))
    print('Talent teams:')
    print('teams: {}'.format(len(teams)))
    print('auto teams: {}'.format(len(export_autoteams)))
    print('team matches: {}'.format(team_bugs))
    print('participants: {}'.format(len(participants)))

    # print('events:')
    # for o,evs in origins.items():
    #     print('\t{}:'.format(o))
    #     for e in evs:
    #         print('\t\t{}'.format(e))
