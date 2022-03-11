from django.contrib import admin
from .models import Player, VolleyballTeam, Competition, Match, MatchEvent

admin.site.register(Player)
admin.site.register(VolleyballTeam)
admin.site.register(Competition)
admin.site.register(Match)
admin.site.register(MatchEvent)
