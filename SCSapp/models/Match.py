from django.db import models
from SCSapp.models.VolleyballTeam import VolleyballTeam
from SCSapp.models.Competition import Competition



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

    def getProtocolFormat(self):
        if self.firstTeamScore > self.secondTeamScore:
            winScore = self.firstTeamScore
            losScore = self.secondTeamScore
            winner = self.firstTeam.name
            loser = self.secondTeam.name
        else:
            winScore = self.secondTeamScore
            losScore = self.firstTeamScore
            winner = self.secondTeam.name
            loser = self.firstTeam.name
        return {"time":self.getDateTime(),"place":self.place,"winner":winner,
                "winScore":str(winScore), "loser":loser, "losScore":str(losScore)}