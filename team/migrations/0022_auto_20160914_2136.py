# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-14 21:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0021_account_org_limit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(choices=[(b'Asana', b'Asana'), (b'Bitbucket', b'Bitbucket'), (b'Box', b'Box'), (b'Dropbox', b'Dropbox'), (b'Github', b'Github'), (b'HipChat', b'HipChat'), (b'Jira', b'Jira'), (b'Quay', b'Quay'), (b'Slack', b'Slack'), (b'Toggl', b'Toggl'), (b'Trello', b'Trello'), (b'Zendesk', b'Zendesk')], max_length=50),
        ),
    ]