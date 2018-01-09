
import calendar

from django.conf import settings
from django.db import models
from django.utils.timezone import datetime, timedelta
from django.utils.translation import ugettext as _

from django.apps import apps

# from qatrack.qa.models import Frequency


# ServiceArea = apps.get_app_config('service_log').get_model('ServiceArea')
# UnitServiceArea = apps.get_app_config('service_log').get_model('UnitServiceArea')

PHOTON = 'photon'
ELECTRON = 'electron'


class Vendor(models.Model):
    """ Vendor of Unit

    Stores information (just name for now) of unit vendor.
    """

    name = models.CharField(max_length=64, unique=True, help_text=_('Name of this vendor'))
    notes = models.TextField(max_length=255, blank=True, null=True, help_text=_('Additional notes about this vendor'))

    def __str__(self):
        """Display more descriptive name"""
        return self.name


class UnitClass(models.Model):
    """ Class of unit

    Unit class, ie. linac, CT, MR, etc.
    """

    name = models.CharField(max_length=64, unique=True, help_text=_('Name of this unit class'))

    def __str__(self):
        """Display more descriptive name"""
        return '<UnitClass(%s)>' % self.name


class Site(models.Model):
    """ Site unit resides

    Allows for multiple site filtering (different campuses, buildings, hospitals, etc)
    """
    name = models.CharField(max_length=64, unique=True, help_text=_('Name of this site'))

    def __str__(self):
        return self.name


class UnitType(models.Model):
    """Radiation Device Type

    Stores a device type for grouping individual :model:`unit`s together.
    For example, your Elekta Linacs might form one group, and your Tomo's
    another.

    TODO: improve model types
    """
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.PROTECT)
    unit_class = models.ForeignKey(UnitClass, null=True, blank=True, on_delete=models.PROTECT)

    name = models.CharField(max_length=50, help_text=_('Name for this unit type'))
    model = models.CharField(max_length=50, null=True, blank=True, help_text=_('Optional model name for this group'))

    class Meta:
        unique_together = [('name', 'model')]

    def __str__(self):
        """Display more descriptive name"""
        return '%s%s' % (self.name, ' - %s' % self.model if self.model else '')


class Modality(models.Model):
    """Treatment modalities

    defines available treatment modalities for a given :model:`unit1`

    """

    name = models.CharField(
        _('Name'),
        max_length=255,
        help_text=_('Descriptive name for this modality'),
        unique=True
    )

    class Meta:
        verbose_name_plural = _('Modalities')

    def __str__(self):
        return self.name


def weekday_count(start_date, end_date, uate_list):
    week = {}
    for i in range((end_date - start_date).days):
        day = start_date + timedelta(days=i + 1)
        if str(day) not in uate_list:
            day_name = calendar.day_name[day.weekday()].lower()
            week[day_name] = week[day_name] + 1 if day_name in week else 1
    return week


class Unit(models.Model):
    """Radiation devices
    Stores a single radiation device (e.g. Linac, Tomo unit, Cyberkinfe etc.)
    """
    type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    site = models.ForeignKey(Site, null=True, blank=True, on_delete=models.PROTECT)

    number = models.PositiveIntegerField(null=False, unique=True, help_text=_('A unique number for this unit'))
    name = models.CharField(max_length=256, help_text=_('The display name for this unit'))
    serial_number = models.CharField(max_length=256, null=True, blank=True, help_text=_('Optional serial number'))
    location = models.CharField(max_length=256, null=True, blank=True, help_text=_('Optional location information'))
    install_date = models.DateField(null=True, blank=True, help_text=_('Optional install date'))
    date_acceptance = models.DateField(help_text=_('Changing acceptance date will delete unit available times that occur before it'))
    active = models.BooleanField(default=True, help_text=_('Set to false if unit is no longer in use'))
    restricted = models.BooleanField(default=False, help_text=_('Set to false to restrict unit from operation'))

    modalities = models.ManyToManyField(Modality)

    # objects = UnitManager()

    class Meta:
        ordering = [settings.ORDER_UNITS_BY]

    def __str__(self):
        return self.name

    def get_potential_time(self, date_from, date_to):

        if date_from is None or date_from > self.date_acceptance:
            date_from = self.date_acceptance

        self_uat_set = self.unitavailabletime_set.filter(
            date_changed__range=[date_from, date_to]
        ).order_by('date_changed')
        self_uate_set = self.unitavailabletimeedit_set.filter(
            date__range=[date_from, date_to]
        ).order_by('date')

        if self.unitavailabletime_set.filter(date_changed__lt=date_from).exists():
            self_uat_set = self_uat_set | self.unitavailabletime_set.filter(date_changed__lt=date_from).order_by('-date_changed')[:1]

        potential_time = 0

        uate_list = {str(uate.date): uate.hours for uate in self_uate_set}

        val_list = self_uat_set.values('date_changed', 'hours_sunday', 'hours_monday', 'hours_tuesday', 'hours_wednesday', 'hours_thursday', 'hours_friday', 'hours_saturday')
        uat_len = len(val_list)
        for i in range(uat_len):
            next_date = val_list[i + 1]['date_changed'] if i < uat_len - 1 else date_to

            if val_list[i]['date_changed'] < date_from:
                days_nums = weekday_count(date_from, next_date, uate_list)
            else:
                days_nums = weekday_count(val_list[i]['date_changed'], next_date, uate_list)

            for day in days_nums:
                potential_time += days_nums[day] * val_list[i]['hours_' + day].total_seconds()

        for uate in uate_list:
            potential_time += uate_list[uate].total_seconds()

        return potential_time / 3600


class UnitAvailableTimeEdit(models.Model):
    """
    A one off change to unit available time (holiday's, extended hours for a single day, etc)
    """
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    name = models.CharField(max_length=64, help_text=_('A quick name or reason for the change'), blank=True, null=True)
    date = models.DateField(help_text=_('Date of available time change'))
    hours = models.DurationField(help_text=_('New duration of availability'))

    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'
        unique_together = [('unit', 'date')]

    def __str__(self):
        return '%s (%s)' % (self.name, self.date.strftime('%b %d, %Y'))


class UnitAvailableTime(models.Model):

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    date_changed = models.DateField(blank=True, help_text=_('Date the units available time changed or will change'))
    hours_monday = models.DurationField(help_text=_('Duration of available time on Mondays'))
    hours_tuesday = models.DurationField(help_text=_('Duration of available time on Tuesdays'))
    hours_wednesday = models.DurationField(help_text=_('Duration of available time on Wednesdays'))
    hours_thursday = models.DurationField(help_text=_('Duration of available time on Thursdays'))
    hours_friday = models.DurationField(help_text=_('Duration of available time on Fridays'))
    hours_saturday = models.DurationField(help_text=_('Duration of available time on Saturdays'))
    hours_sunday = models.DurationField(help_text=_('Duration of available time on Sundays'))

    class Meta:
        ordering = ['-date_changed']
        default_permissions = ('change',)
        get_latest_by = 'date_changed'
        unique_together = [('unit', 'date_changed')]

    def __str__(self):
        return 'Available time for %s' % self.unit.name
