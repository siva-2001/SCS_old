from django.urls import reverse
from django.db import models
import random
from django.contrib.auth.models import User
import pytz
from datetime import datetime
from SCSapp.func import sentMail
from SCSapp.protocolCreator import PDF
from django.core.files import File
import os
from SCSapp.models.VolleyballTeam import VolleyballTeam

class Competition(models.Model):
    ANNOUNSED = 'Announsed'
    CURRENT = 'Current'
    PAST = 'Past'
    competitionStatusChoises = [
        (ANNOUNSED, 'Announsed'),
        (CURRENT, 'Current'),
        (PAST, 'Past'),
    ]
    status = models.CharField(
        max_length=12,
        choices=competitionStatusChoises
    )


    name = models.CharField(max_length=100, verbose_name="Заголовок")
    discription = models.TextField(blank=True, verbose_name="Описание")
    lastTimeForApplications = models.DateTimeField(verbose_name="Заявки на участие принимаются до")
    competitionEndDateTime = models.DateTimeField(blank=True, null=True, verbose_name="Соревнование завершилось")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Организатор")
    organizerName = models.CharField(max_length=32, null=True, verbose_name="Наименование организации проводящей турнир")
    theNumberOfTeamsRequiredToStartTheCompetition = models.IntegerField(default=4, verbose_name="Необходимое количество команд")
    protocol = models.FileField(upload_to='protocols', null=True, blank=True, verbose_name="Протокол")


    class Meta:
        permissions = [
            ('control_competition','the user must be the judge')
        ]
        verbose_name = 'Соревнование'
        verbose_name_plural = 'Соревнования'


    def __str__(self):
        return f" Title: {self.name}"

    def get_absolute_url(self):
        return reverse('competition', args=[str(self.id)])


    def getLastTimeForApplicationStr(self):
        return self.lastTimeForApplications.strftime("%H:%M   %Y:%m:%d")

    def getEndDateTimeStr(self):
        return self.competitionEndDateTime.strftime("%H:%M   %Y:%m:%d")

    def makeStandings(self):
        teams = VolleyballTeam.objects.all().filter(competition=self)
        if len(teams) < self.theNumberOfTeamsRequiredToStartTheCompetition:
            return False

        self.status = Competition.CURRENT
        self.save()
        standingElemets = []

        while(len(standingElemets) < len(teams)):
            num = random.randint(0, len(teams)-1)
            if not teams[num] in standingElemets:
                standingElemets.append(teams[num])

        tours = 0
        while(pow(tours, 2) <= len(teams)):
            for ind, elem in enumerate(standingElemets):
                if ind < len(standingElemets)-1:
                    if type(elem) == VolleyballTeam and type(standingElemets[ind+1]) == VolleyballTeam:
                        match = Match(
                            name= f"{elem.name} vs {standingElemets[ind+1].name}",
                            firstTeam = elem,
                            secondTeam = standingElemets[ind+1],
                            competition=self,
                        )
                        match.save()
                        standingElemets.remove(elem)
                        standingElemets.remove(standingElemets[ind])
                        standingElemets.insert(ind, match)
                    elif type(elem) == VolleyballTeam and type(standingElemets[ind+1]) == Match:
                        match = Match(
                            name=f"{elem.name} vs _______",
                            firstTeam = elem,
                            competition = self
                        )
                        match.save()
                        standingElemets[ind + 1].nextMatch = match
                        standingElemets[ind + 1].save()
                        standingElemets.remove(elem)
                        standingElemets.remove(standingElemets[ind])
                        standingElemets.insert(ind, match)
                    elif type(elem) == Match and type(standingElemets[ind+1]) == Match:
                        match = Match(
                            name=f"_______ vs ________",
                            competition = self,
                        )
                        match.save()
                        elem.nextMatch = match
                        elem.save()
                        standingElemets[ind+1].nextMatch = match
                        standingElemets[ind+1].save()
                        standingElemets.remove(elem)
                        standingElemets.remove(standingElemets[ind])
                        standingElemets.insert(ind, match)
            standingElemets.reverse()
            tours += 1
        return True

    def updateStanding(self, matchID):
        match = Match.objects.all().get(id=matchID)
        nextMatch = match.nextMatch
        if(nextMatch):
            if nextMatch.firstTeam:
                if match.firstTeamScore > match.secondTeamScore:
                    nextMatch.secondTeam = match.firstTeam
                else:
                    nextMatch.secondTeam = match.secondTeam
                nextMatch.name = f"{nextMatch.firstTeam} vs {nextMatch.secondTeam}"
            else:
                if match.firstTeamScore > match.secondTeamScore:
                    nextMatch.firstTeam = match.firstTeam
                else:
                    nextMatch.firstTeam = match.secondTeam
                nextMatch.name = f"{nextMatch.firstTeam} vs _____________"
            nextMatch.save()
        else:
            self.status = Competition.PAST
            self.competitionEndDateTime = pytz.UTC.localize(datetime.now())
            self.save()
            self.GenerateProtocol()
        self.DoMailingAboutStart()

    def GenerateProtocol(self):
        pdf = PDF()
        teams = VolleyballTeam.objects.all().filter(competition=self)
        matches = Match.objects.all().filter(competition=self)
        teamsPF, matchesPF = [], []
        for team in teams:
            teamsPF.append(team.getProtocolFormat())
        for match in matches:
            matchesPF.append( match.getProtocolFormat())
        pdf.CompetitionProtocol(self.name, teamsPF, matchesPF,
                                self.organizer.first_name + "  " + self.organizer.last_name, str(self.getEndDateTimeStr()))
        with open("tempFile.pdf", 'rb') as protocol:
            self.protocol.save(self.name+".pdf", File(protocol), save=False)
        os.remove("tempFile.pdf")
        self.save()


    def DoMailingAboutStart(self):
        users = User.objects.all()
        strRecipients = ''
        for user in users:
            if user.email:
                strRecipients = strRecipients + user.email + ', '
        strRecipients = strRecipients[:-2]
        message = f"Соревнования {self.name} стартовали!"
        sentMail(message=message, strRecipients=strRecipients)
