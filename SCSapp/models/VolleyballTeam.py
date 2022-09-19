from django.db import models
from django.contrib.auth.models import User

class VolleyballTeam(models.Model):
    name = models.CharField(max_length=64, verbose_name="Название")
    registratedTime = models.DateTimeField(auto_now_add=True, verbose_name="Время регистрации")
    discription = models.TextField(blank=True, verbose_name="Описание")
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE, verbose_name="Соревнования")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

    def __str__(self):#
        return self.name

    def getRegisteredTime(self):
        return self.registratedTime.strftime("%H:%M   %Y:%m:%d")

    def getProtocolFormat(self):
        if not(len(self.user.last_name) == 0 and len(self.user.first_name) == 0):
            return {"name":self.name,"registeredTime":self.getRegisteredTime(),
                    "user":(self.user.last_name + " " + self.user.first_name[:1] + ".")}
        else:
            return  {"name": self.name, "registeredTime": self.getRegisteredTime(), "user":' '}
