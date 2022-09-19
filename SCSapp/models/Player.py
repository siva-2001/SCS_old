from django.db import models
from SCSapp.models.VolleyballTeam import VolleyballTeam

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

