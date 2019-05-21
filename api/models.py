from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.utils.translation import ugettext_lazy as _

from geopy.distance import vincenty




class Team(models.Model):
    name = models.CharField(max_length=150, verbose_name=_('nom d\'équipe'))
    picture = models.FileField(default="https://vignette.wikia.nocookie.net/lucifer/images/9/97/No_Photo.png/revision/latest?cb=20171213001812&path-prefix=fr", verbose_name=_('logo'))
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    distance = models.IntegerField(default=0, verbose_name=_('distance parcourue'), help_text=_('en mètres'))
    score = models.IntegerField(blank=True, default=0)
    disqualified = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    def compute_score(self):
        score = self.team_achievements.aggregate(Sum('achievement__points'))
        return score['achievement__points__sum'] or 0

    @property
    def last_seen(self):
        try:
            balise = self.balises.filter(valid=True).last()
        except Balise.DoesNotExist:
            return None
        try:
            position = balise.positions.order_by('dh').last()
        except Position.DoesNotExist:
            return None
        return position.created_at

    def __str__(self):
        return self.name


class Participant(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('nom'))
    phone = models.CharField(max_length=20, verbose_name=_('téléphone'))
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='participants')

    def __str__(self):
        return "{} ({})".format(self.name, self.team.name)


class Balise(models.Model):
    serial = models.CharField(max_length=50, verbose_name=_('numéro de série'))
    valid = models.BooleanField(default=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='balises')
    
    def __str__(self):
        return self.serial + ' - ' + self.team.name


class Position(models.Model):
    balise = models.ForeignKey(Balise, on_delete=models.CASCADE, null=True, related_name='positions')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    name = models.CharField(max_length=250, verbose_name=_('nom constaté'), blank=True, default='')
    dh = models.IntegerField(blank=True, default=0)
    speed = models.IntegerField(blank=True, default=0)
    created_at = models.DateTimeField(blank=True, auto_now_add=True)

    def __str__(self):
        return "Position {} à {}".format(self.balise.team.name, self.created_at)


@receiver(post_save, sender=Position)
def update_team_position(instance, **kwargs):
    last_position = instance.balise.positions.order_by('dh').last()
    team = last_position.balise.team

    start = (team.latitude, team.longitude)
    stop = (last_position.latitude, last_position.longitude)
    distance = int(vincenty(start, stop).meters)

    team.distance += distance
    team.latitude = last_position.latitude
    team.longitude = last_position.longitude
    team.save()


class Achievement(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('nom'))
    points = models.IntegerField(verbose_name=_('points'))
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(blank=True, auto_now_add=True)
    teams = models.ManyToManyField(Team, through='TeamAchievement')

    def __str__(self):
        return "{} ({} points)".format(self.name, self.points)


class TeamAchievement(models.Model):
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='team_achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.PROTECT, related_name='team_achievements')
    #created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(blank=True, auto_now_add=True)
    photo = models.FileField(blank=False, null=True)
    validation = models.BooleanField(default=False)



    def __str__(self):
        return "{} a réussi le succès \"{}\" ({} points)".format(self.team.name, self.achievement.name, self.achievement.points)

class File(models.Model):
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='file')
    achievement = models.ForeignKey(Achievement, on_delete=models.PROTECT, related_name='file')
    file = models.FileField(blank=False, null=True)

    def __str__(self):
        return self.file.name

@receiver(post_save, sender=Achievement)
def update_score_on_achievement_edit(instance, **kwargs):
    for team in instance.teams.all():
        team.score = team.compute_score()
        team.save()


@receiver(post_save, sender=TeamAchievement)
def update_score_on_teams(instance, **kwargs):
    team = instance.team
    team.score = team.compute_score()
    team.save()


@receiver(post_delete, sender=TeamAchievement)
def delete_score_on_teams(instance, **kwargs):
    team = instance.team
    team.score = team.compute_score()
    team.save()

