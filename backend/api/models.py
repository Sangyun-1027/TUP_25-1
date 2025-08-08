from django.db import models
from django.contrib.auth.models import AbstractUser


class User(models.Model):
    id = models.AutoField(primary_key=True)  # 기본 키
    name = models.CharField(max_length=100)
    skills = models.JSONField(default=list)  # ex: ["Python", "React"]
    keywords = models.JSONField(default=list)  # ex: ["빠른 실행", "소통"]
    mainRole = models.CharField(max_length=50)  # ex: "프론트엔드"
    subRole = models.CharField(max_length=50, blank=True)  # ex: "디자인"
    rating = models.FloatField(default=0.0)  # ex: 4.7
    participation = models.IntegerField(default=0)  # 공모전 참여 횟수 등
    is_leader = models.BooleanField(default=False)
    has_reward = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    tech = models.JSONField(default=list)  # 기술스택 ex: ["Django", "AWS"]
    looking_for = models.JSONField(default=list)  # ex: ["디자이너", "기획자"]
    max_members = models.IntegerField()
    members = models.ManyToManyField(User, related_name='joined_teams', blank=True)
    status = models.CharField(max_length=20, default='open')  # ex: open / closed

    def __str__(self):
        return self.name


class Application(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Invitation(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
