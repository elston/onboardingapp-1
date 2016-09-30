from __future__ import unicode_literals

from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey('team.TeamUser',
                              related_name='organization_owner')
    team = models.ManyToManyField(
        'team.Team', related_name='organization_team', blank=True)

    def __unicode__(self):
        return self.name
