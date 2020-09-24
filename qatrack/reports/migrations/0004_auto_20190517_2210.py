# Generated by Django 2.1.7 on 2019-05-18 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_copy_report_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savedreport',
            name='include_signature',
            field=models.BooleanField(default=True, help_text='Signature field at end of PDFs?', verbose_name='Signature'),
        ),
        migrations.AlterField(
            model_name='savedreport',
            name='report_type',
            field=models.CharField(choices=[('General', [('test_data', 'Test Instance Values'), ('utc', 'Test List Instances'), ('qc-summary-by-date', 'QC Summary')]), ('Scheduling', [('due_and_overdue', 'Due and Overdue QC'), ('next_due', 'Next Due Dates for QC')])], max_length=128),
        ),
        migrations.AlterField(
            model_name='savedreport',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]