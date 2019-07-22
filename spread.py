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

#get time of last connection
def get_last_connect_row(member: str):
    sheet = client.open('The Idiots Discord Activity')
    log = sheet.worksheet('log')
    lastrow = log.row_count
    connect = ['connected', 'returned']
    print(member)
    while True:
        if lastrow <= 1:
            return 0
        name = log.cell(lastrow, 3).value
        status = log.cell(lastrow, 4).value
        print(lastrow, name, status)
        if member == name:
            if status in connect:
                return lastrow
            return 0
        lastrow -= 1


def get_length(member: str):
    lastrow = get_last_connect_row(member)
    if lastrow is 0:
        return 0
    current = time.time()
    length = current - float(log.cell(lastrow, 1).value)
    return int(length / 60)


def log_update(member, before, after):
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

