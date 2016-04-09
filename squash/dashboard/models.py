from django.db import models


class Dataset(models.Model):
    datasetId = models.AutoField(primary_key=True)
    name = models.TextField()
    camera = models.TextField()
    description = models.TextField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Visit(models.Model):
    visitId = models.AutoField(primary_key=True)
    datasetId = models.ForeignKey(Dataset)
    visit = models.IntegerField()
    mjd = models.IntegerField()
    nExposures = models.IntegerField()
    exposureType = models.TextField()
    exposureStart = models.DateTimeField()
    exposureTime = models.IntegerField()
    filter = models.CharField(max_length=1)
    telRa = models.FloatField()
    telDecl = models.FloatField()
    zenithDistance = models.FloatField()
    airMass = models.FloatField()
    hourAngle = models.FloatField()

    def __str__(self):
        return self.visit


class Ccd(models.Model):
    ccdId = models.AutoField(primary_key=True)
    visitId = models.ForeignKey(Visit)
    ccd = models.TextField()
    llra = models.FloatField()
    lldecl = models.FloatField()
    urra = models.FloatField()
    urdecl = models.FloatField()
    medianSkyBkg = models.FloatField()
    madSkyBkg = models.FloatField()
    medianFwhm = models.FloatField()
    madFwhm = models.FloatField()
    medianR50 = models.FloatField()
    madR50 = models.FloatField()
    medianMajorAxis = models.FloatField()
    madMajorAxis = models.FloatField()
    medianMinorAxis = models.FloatField()
    madMinorAxis = models.FloatField()
    medianTheta = models.FloatField()
    madTheta = models.FloatField()
    medianScatterRa = models.FloatField()
    madScatterRa = models.FloatField()
    medianScatterDecl = models.FloatField()
    madScatterDecl = models.FloatField()
    medianScatterPsfFlux = models.FloatField()
    madScatterPsfFlux = models.FloatField()
    nSources = models.IntegerField()
    nCosmicRays = models.IntegerField()
    log = models.TextField()

    def __str__(self):
        return self.ccd
