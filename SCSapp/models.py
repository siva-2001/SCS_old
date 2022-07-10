from django.urls import reverse
from django.db import models
import random
from django.contrib.auth.models import User
import pytz
from datetime import datetime
from .func import sentMail


class VolleyballTeam(models.Model):
    name = models.CharField(max_length=64, verbose_name="Название")
    registratedTime = models.DateTimeField(auto_now_add=True, verbose_name="Время регистрации")
    discription = models.TextField(blank=True, verbose_name="Описание")
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE, verbose_name="Соревнования")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

    def __str__(self):
        return self.name

#    def get_ablolut_url(self):
#        return reverse()

class Player(models.Model):
    class Meta:
        ordering = ['surename', 'name']
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

    name = models.CharField(max_length=32, verbose_name='Имя')
    surename = models.CharField(max_length=32, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=32, blank=True, null=True, verbose_name='Отчество')
    age = models.IntegerField(verbose_name='Возраст')
    team = models.ManyToManyField(VolleyballTeam, blank=True)

    def __str__(self):
        return f'{self.name}  {self.surename}'



class MatchEvent(models.Model):
    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
    GOAL = 'Goal'
    PLAYER_REPLACEMENT = 'Player replacement'
    PART = 'Part'
    INTERVAL = 'Interval'
    END = 'Game over'
    NONE = 0
    FIRST = 1
    SECOND = 2

    teamChoise = [
        (FIRST, 'first'),
        (SECOND, 'second'),
    ]
    eventTypeChoises = [
        (GOAL, 'Goal'),
        (PLAYER_REPLACEMENT, 'Player replacement'),
        (PART, 'Part'),
        (INTERVAL, 'Interval'),
        (END, 'Game over'),
    ]

    eventType = models.CharField(
        max_length=20,
        choices=eventTypeChoises
    )


    Team = models.IntegerField(choices=teamChoise, verbose_name="Команда", null=True, blank=True)
    EventTime = models.TimeField(auto_now_add=True, verbose_name="Время события")
    match = models.ForeignKey('Match', on_delete=models.CASCADE, verbose_name="Матч")

    def __str__(self):
        return f"{self.eventType}, team {self.Team} in {self.EventTime}"

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
    protocol = models.FileField(upload_to='competition_protocols', null=True, blank=True, verbose_name="Протокол")


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
        return self.lastTimeForApplications.strftime("%Y:%m:%d   %H:%M")

    def getEndDateTimeStr(self):
        return self.competitionEndDateTime.strftime("%Y:%m:%d   %H:%M")

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
        match.status_isCompleted = True
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
        match.save()

    def doMailingAboutCurrent(self):
        users = User.objects.all()
        strRecipients = ''
        for user in users:
            if user.email:
                strRecipients = strRecipients + user.email + ', '
        strRecipients = strRecipients[:-2]
        message = f"Соревнования {self.name} стартовали!"
        sentMail(message=message, strRecipients=strRecipients)




class Match(models.Model):
    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'
    name = models.CharField(max_length=64)
    nextMatch = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None, blank=True)
    firstTeam = models.ForeignKey(VolleyballTeam, blank=True,
        null=True, on_delete=models.SET_NULL, related_name="first_team", default=None)
    secondTeam = models.ForeignKey(VolleyballTeam, blank=True,
        null=True, on_delete=models.SET_NULL, related_name="second_team", default=None)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    matchDateTime = models.DateTimeField(null=True, default=None)
    firstTeamScore = models.IntegerField(default=0)
    secondTeamScore = models.IntegerField(default=0)
    place = models.CharField(max_length=128, blank=True, null=True)
    status_isCompleted = models.BooleanField(default=False)
    protocol = models.FileField(upload_to='match_protocols', null=True, blank=True)
        # Значение по умолчанию - названия команд

    def getDateTime(self):
        if self.matchDateTime:
            return self.matchDateTime.strftime("%Y:%m:%d %H:%M")
        else: return "Дата неизвестна"

    def __str__(self):
        return f"Матч '{self.name}'"