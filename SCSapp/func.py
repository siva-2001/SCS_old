from datetime import datetime
import pytz
from .models import Competition

def convertDTPickerStrToDateTime(str):
    newCompDataTime = datetime(
        int(str[0:4]),
        int(str[5:7]),
        int(str[8:10]),
        int(str[11:13]),
        int(str[14:16])
    )
    return newCompDataTime

def checkCompetitionStart():
    competitions = Competition.objects.all().filter(status= Competition.ANNOUNSED)
    for comp in competitions:
        if comp.lastTimeForApplications < pytz.UTC.localize(datetime.now()):
            comp.makeStandings()

            #doMailing()


def doMailing():
    A = 0                                                                    #   ЗАГЛУШКА