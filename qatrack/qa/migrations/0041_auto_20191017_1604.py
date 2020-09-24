# Generated by Django 2.1.11 on 2019-10-17 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0040_add_default_autoreviewruleset'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='auto_review',
        ),
        migrations.AlterField(
            model_name='autoreviewrule',
            name='pass_fail',
            field=models.CharField(choices=[('not_done', 'Not Done'), ('ok', 'OK'), ('tolerance', 'Tolerance'), ('action', 'Action'), ('no_tol', 'No Tol Set')], help_text='Pass fail state of test instances to apply this rule to.', max_length=15),
        ),
    ]