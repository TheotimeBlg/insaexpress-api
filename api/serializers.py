from django.contrib.auth.models import User
from rest_framework import serializers

from api.fields import PublicLongitudeField, PublicLatitudeField, PublicDistanceField
from api.models import Team, Participant, Position, Achievement, TeamAchievement


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('latitude', 'longitude', 'team_id', 'created_at')


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ('id', 'name', 'points')


class TeamAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    achievement_id = serializers.IntegerField(write_only=True)
    team_id = serializers.IntegerField()

    class Meta:
        model = TeamAchievement
        fields = ('created_at', 'achievement', 'achievement_id', 'team_id', 'picture')


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ('id', 'name', 'phone')


class PublicTeamSerializer(serializers.ModelSerializer):
    team_achievements = TeamAchievementSerializer(many=True)
    latitude = PublicLatitudeField()
    longitude = PublicLongitudeField()
    distance = PublicDistanceField()

    class Meta:
        model = Team
        fields = ('id', 'name', 'latitude', 'longitude', 'distance',
                  'score', 'disqualified', 'team_achievements', 'picture')


class TeamSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True)
    team_achievements = TeamAchievementSerializer(many=True)

    class Meta:
        model = Team
        fields = ('id', 'name', 'latitude', 'longitude', 'distance',
                  'score', 'disqualified', 'team_achievements',
                  'participants', 'picture', 'last_seen')



