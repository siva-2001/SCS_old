from django.db import models

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

