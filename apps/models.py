# models.py

from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    version = models.CharField(max_length=20, default='1.0')
    manager = models.CharField(max_length=100, default='Ahmed')  # Hardcoded manager

    def __str__(self):
        return f"{self.name} (v{self.version})"

class Feature(models.Model):
    PRIORITY_CHOICES = [('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')]
    STATUS_CHOICES = [('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')]

    name = models.CharField(max_length=255)
    description = models.TextField()
    brd = models.TextField('Business Requirements Document')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='features')

    def __str__(self):
        return self.name
 
    
class TestCase(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In Progress'),
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    steps = models.TextField()
    expected_result = models.TextField()
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='test_cases')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New Fields
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW',
    )

    def __str__(self):
        return self.title