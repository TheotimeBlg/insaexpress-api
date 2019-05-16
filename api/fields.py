import random

from rest_framework import serializers


class PublicCoordinateField(serializers.FloatField):
    resolution = 0.5
    precision = 1
    """
    Add noise to the coordinate to protect privacy.
    """
    def to_representation(self, obj):
        return self.round(obj)

    def round(self, f):
        value = round(round(f / self.resolution) * self.resolution, self.precision)
        return value


class PublicLatitudeField(PublicCoordinateField):
    resolution = 0.020
    precision = 3


class PublicLongitudeField(PublicCoordinateField):
    resolution = 0.030
    precision = 3


class PublicDistanceField(PublicCoordinateField):
    resolution = 2000
    precision = 0
