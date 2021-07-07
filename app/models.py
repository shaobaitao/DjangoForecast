from django.db import models


# Create your models here.

class users(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    phoneNumber = models.CharField(max_length=32)
    trainDataID = models.IntegerField(null=True)


class userPermission(models.Model):
    permission = models.IntegerField()
    userID = models.ForeignKey(users, null=True, on_delete=models.SET_NULL)


class userData(models.Model):
    userID = models.ForeignKey(users, null=True, on_delete=models.SET_NULL)
    Age = models.IntegerField()
    BusinessTravel = models.CharField(max_length=32)
    Department = models.CharField(max_length=32)
    DistanceFromHome = models.FloatField()
    Education = models.IntegerField()
    EducationField = models.CharField(max_length=32)
    EmployeeNumber = models.IntegerField()
    EnvironmentSatisfaction = models.IntegerField()
    Gender = models.CharField(max_length=32)
    JobInvolvement = models.IntegerField()
    JobLevel = models.IntegerField()
    JobRole = models.CharField(max_length=32)
    JobSatisfaction = models.IntegerField()
    MaritalStatus = models.CharField(max_length=32)
    MonthlyIncome = models.IntegerField()
    NumCompaniesWorked = models.IntegerField()
    Over18 = models.CharField(max_length=8)
    OverTime = models.CharField(max_length=8)
    PercentSalaryHike = models.IntegerField()
    PerformanceRating = models.IntegerField()
    RelationshipSatisfaction = models.IntegerField()
    StandardHours = models.IntegerField()
    StockOptionLevel = models.IntegerField()
    TotalWorkingYears = models.IntegerField()
    TrainingTimesLastYear = models.IntegerField()
    WorkLifeBalance = models.IntegerField()
    YearsAtCompany = models.IntegerField()
    YearsInCurrentRole = models.IntegerField()
    YearsSinceLastPromotion = models.IntegerField()
    YearsWithCurrManager = models.IntegerField()
