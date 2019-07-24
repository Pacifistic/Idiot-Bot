import gspread
import time
import discord
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)

sheet = client.open('The Idiots Discord Activity')
log = sheet.worksheet('log')
data = sheet.worksheet('data')


def isAFK(member: discord.VoiceState):
    if member.deaf:
        return True
    elif member.mute:
        return True
    elif member.self_mute:
        return True
    elif member.self_deaf:
        return True
    elif member.afk:
        return True
    return False


def newEntry(name: str):
    sheet = client.open('The Idiots Discord Activity')
    data = sheet.worksheet('data')

    col = data.col_count
    data.add_cols(1)

    data.update_cell(1, col, name)


def updateTotal(name: str, length: int):
    sheet = client.open('The Idiots Discord Activity')
    totals = sheet.worksheet('total')

    totalsdata = totals.get_all_records()
    count = 2

    for person in totalsdata:
        if person.get('name') == name:
            length = length + int(person.get('length'))
            totals.update_cell(count, 2, length)
            return
        count += 1

    newEntry(name)
    row = [name, length]
    totals.append_row(row)


async def updataData():
    sheet = client.open('The Idiots Discord Activity')
    data = sheet.worksheet('data')
    totals = sheet.worksheet('total')
    row = totals.col_values(2)
    row.pop(0)
    row.insert(0, time.asctime())
    data.append_row(row)


#get time of last connection
def get_last_connect_time(member: str):
    sheet = client.open('The Idiots Discord Activity')
    log = sheet.worksheet('log')
    loglist = log.get_all_records()
    connect = ['connected', 'returned']

    entries = list(filter(lambda entry: entry['name'] == member, loglist))

    while True:
        entry = entries.pop()
        if entry.get('status') in connect:
            return float(entry.get('time'))


def get_length(member: str):
    lasttime = get_last_connect_time(member)
    if lasttime is 0:
        return 0
    current = time.time()
    length = current - lasttime
    updateTotal(member, int(length / 60))
    return int(length / 60)


async def log_update(member, before, after):
    #connected to discord
    if before.channel is None and after.channel is not None:
        print(member.display_name + ' joined ' + after.channel.name)
        row = [time.time(), time.asctime(), member.name, 'connected', after.channel.name]
        log.append_row(row)
        return
    #disconnected from discord
    elif after.channel is None:
        print(member.display_name + ' disconnected')
        row = [time.time(), time.asctime(), member.name, 'disconnected', before.channel.name, get_length(member.name)]
        log.append_row(row)
        return
    #went afk
    elif isAFK(after):
        print(member.display_name + ' is AFK')
        row = [time.time(), time.asctime(), member.name, 'AFK', before.channel.name, get_length(member.name)]
        log.append_row(row)
        return
    #left AFK channel
    elif before.channel.name == 'AFK' and after.channel is not None and after.channel is not before.channel:
        print(member.display_name + ' is back')
        row = [time.time(), time.asctime(), member.name, 'returned', after.channel.name]
        log.append_row(row)
        return
    # changed channel
    elif before.channel is not after.channel:
        print(member.display_name + ' moved to ' + after.channel.name)
        row = [time.time(), time.asctime(), member.name, 'moved', after.channel.name]
        log.append_row(row)
        return
    #stopped being AFK
    else:
        print(member.display_name + ' is back')
        row = [time.time(), time.asctime(), member.name, 'returned', after.channel.name]
        log.append_row(row)
        return


async def reauth():
    global client
    client.login()
