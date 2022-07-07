from datetime import datetime
import pytz
from .models import Competition

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
def checkCompetitionStart():
    competitions = Competition.objects.all().filter(status= Competition.ANNOUNSED)
    for comp in competitions:
        if comp.lastTimeForApplications < pytz.UTC.localize(datetime.now()):
            comp.makeStandings()
