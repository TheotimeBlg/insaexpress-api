from django.contrib import admin
from . import models


@admin.register(models.Team,
                models.Participant,
                models.Balise,
                models.Achievement,
                models.Position,
                models.TeamAchievement,
                models.File)
		
class BasicAdmin(admin.ModelAdmin):
    pass
