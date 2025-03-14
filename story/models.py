from django.db import models

from member.models import *
# Create your models here.


class Genre(models.Model):
    name = models.TextField(max_length=250, null=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Story(models.Model):
    GENRE_CHOICES = [
        (1, 'Fiction'),
        (2, 'Science Fiction'),
        (3, 'Historical Fiction'),
        (4, 'Mystery'),
        (5, 'Fantasy'),
        (6, 'Romance'),
    ]

    STATUS_CHOICES = [
        (1, 'pending'),
        (2, 'published'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    started_date = models.DateField(default='2000-01-01', null=True, blank=True)
    title = models.TextField(max_length=250, null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    main_character = models.TextField(max_length=250, null=True, blank=True)
    time_setting = models.TextField(max_length=250, null=True, blank=True)
    suggested_keyword = models.TextField(max_length=250, null=True, blank=True)
    exposition_summary = models.TextField(max_length=10000, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    def __str__(self):
        return "_".join([self.user.username, str(self.started_date), self.title])


class Stage(models.Model):
    PART_CHOICES = [
        (1, 'exposition'),
        (2, 'rising action'),
        (3, 'climax'),
        (4, 'falling action'),
        (5, 'resolution'),
    ]
    STATUS_CHOICES = [
        (1, 'pending'),
        (2, 'rejected'),
        (3, 'accepted'),
    ]
    story = models.ForeignKey(Story, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, blank=False)
    submitted_date = models.DateField(default='2000-01-01', null=True, blank=True)
    part = models.IntegerField(choices=PART_CHOICES)
    status = models.IntegerField(choices=STATUS_CHOICES)
    text = models.TextField(max_length=100000, null=True, blank=True)

    def __str__(self):
        return "_".join([self.user.username, self.story.title, str(self.part), str(self.status)])
