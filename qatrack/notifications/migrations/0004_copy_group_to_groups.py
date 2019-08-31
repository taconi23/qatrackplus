# Generated by Django 2.1.7 on 2019-04-11 02:51

from django.db import migrations


def copy_group_to_groups(apps, schema):

    NotificationSubscription = apps.get_model("notifications", "NotificationSubscription")
    for ns in NotificationSubscription.objects.all():
        ns.groups.add(ns.group)


def copy_first_group_to_group(apps, schema):

    NotificationSubscription = apps.get_model("notifications", "NotificationSubscription")
    for ns in NotificationSubscription.objects.all():
        ns.group = ns.groups.first()
        ns.save()


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_auto_20190410_2251'),
    ]

    operations = [
        migrations.RunPython(copy_group_to_groups, copy_first_group_to_group)
    ]