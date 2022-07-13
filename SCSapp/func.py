from datetime import datetime
import pytz
import smtplib
from email.message import EmailMessage

def convertDTPickerStrToDateTime(DTPStr):
    newCompDataTime = datetime(
        int(DTPStr[0:4]),
        int(DTPStr[5:7]),
        int(DTPStr[8:10]),
        int(DTPStr[11:13]),
        int(DTPStr[14:16])
    )
    return newCompDataTime

#       Вызывается при переходе на главную и страницу любого соревнования
def checkCompetitionStart(competitions):
    for comp in competitions:
        if comp.lastTimeForApplications < pytz.UTC.localize(datetime.now()):
            comp.makeStandings()


def sentMail(message, strRecipients):
    sender = "scsapp@yandex.ru"
    password = 'Prostoparol1234'
    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)

    msg = EmailMessage()
    msg['Subject'] = f'Соревнования скоро!'
    msg['From'] = sender
    msg['To'] = strRecipients
    msg.set_content(message)

    try:
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return "Messages was sent succesfully"
    except Exception as _e:
        return f"{_e}"