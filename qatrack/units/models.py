from django.db import models
from django.utils.translation import ugettext as _


#==========================================================================
class UnitType(models.Model):
    """Radiation Device Type

    Stores a device type for grouping individual :model:`unit`s together.
    For example, your Elekta Linacs might form one group, and your Tomo's
    another.

    """

    name = models.CharField(max_length=50, help_text=_("Name for this unit type"))
    vendor = models.CharField(max_length=50, help_text=_("e.g. Elekta"))
    model = models.CharField(max_length=50, help_text=_("Optional model name for this group (e.g. Beam Modulator)"), null=True, blank=True)


#============================================================================
class Modality(models.Model):
    """Treatment modalities

    defines available treatment modalities for a given :model:`unit1`

    """

    type_choices = (("photon", "Photon"), ("electron", "Electron"),)
    type = models.CharField(_("Treatement modality type"), choices=type_choices, max_length=20)
    energy = models.FloatField(help_text=_("Nominal energy (in MV for photons and MeV for electrons"))
    spectrum = models.CharField(help_text=_("Only required for brachytherapy"), max_length=50, blank=True, null=True)

    #---------------------------------------------------------------------------
    def __unicode__(self):
        if self.type == "photon":
            unit, particle = "MV", "Photon"
        else:
            unit, particle = "MeV", "Electron"
        return "<Modality(%.1f%s,%s)>" % (self.energy, unit, particle)

    class Meta:
        verbose_name_plural = "Modalities"


#============================================================================
class Unit(models.Model):
    """Radiation devices

    Stores a single radiation device (e.g. Linac, Tomo unit, Cyberkinfe etc.)

    """

    number = models.PositiveIntegerField(null=False, unique=True, help_text=_("A unique number for this unit"))
    name = models.CharField(max_length=256, help_text=_("The display name for this unit"))
    type = models.ForeignKey(UnitType)

    modalities = models.ManyToManyField(Modality)

    class Meta:
        ordering = ["number"]

    #----------------------------------------------------------------------
    def __unicode__(self):
        return u"<Unit(%d, %s)>" % (self.number, self.name)