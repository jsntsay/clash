from django.db import models

# User class for built-in authentication module
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	political = models.CharField(max_length=200)
	age = models.IntegerField()
	gender = models.CharField(max_length=30)
	def __unicode__(self):
		return self.user.username

class Article(models.Model):
	title = models.CharField(max_length=300)
	source = models.CharField(max_length=300)
	article_link = models.CharField(max_length=300)
	blurb = models.TextField(blank=True)
	def __unicode__(self):
		return self.article_link

class Discussion(models.Model):
	userA = models.ForeignKey(User, related_name="user_a")
	userB = models.ForeignKey(User, related_name="user_b")
	articleA = models.ForeignKey(Article, related_name="article_a", blank=True, null=True)
	articleB = models.ForeignKey(Article, related_name="article_b", blank=True, null=True)
	# randomly assigned animal and color for this discussion
	animal = models.CharField(max_length=200, blank=True)
	animalColor = models.CharField(max_length=200, blank=True)
	# states: "start", "articles", "discuss"
	state = models.CharField(max_length=200, default="start")
	def __unicode__(self):
		return self.userA.username + ":" + self.userB.username

# states for discussion: articles, position, context, situational, free
class DiscussionState(models.Model):
	discuss = models.ForeignKey(Discussion, related_name="discuss")
	state = models.CharField(max_length=200, default="articles")
	finished = models.BooleanField(default="False")
	def __unicode__(self):
		return str(self.discuss) + ":" + self.state
		
# 1st phase: discrete position questions
class Position(models.Model):
	user = models.ForeignKey(User)
	discuss = models.ForeignKey(Discussion)
	answer1 = models.IntegerField(blank=True, null=True)
	answer2 = models.IntegerField(blank=True, null=True)
	answer3 = models.IntegerField(blank=True, null=True)
	answer4 = models.IntegerField(blank=True, null=True)
	def __unicode__(self):
		return str(self.discuss) + ":" + self.user.username + ":" + self.answer
		
# 2nd phase: discrete context questions
class Context (models.Model):
	user = models.ForeignKey(User)
	discuss = models.ForeignKey(Discussion)
	answer1 = models.IntegerField(blank=True, null=True)
	answer2 = models.IntegerField(blank=True, null=True)
	answer3 = models.IntegerField(blank=True, null=True)
	def __unicode__(self):
		return str(self.discuss) + ":" + self.user.username + ":" + self.answer
		
# 3rd phase: fill in the blank situational questions
class Situational(models.Model):
	user = models.ForeignKey(User)
	discuss = models.ForeignKey(Discussion)
	option = models.CharField(max_length=200, blank=True, null=True)
	answer = models.TextField(blank=True, null=True)
	text = models.TextField(blank=True, null=True)
	def __unicode__(self):
		return str(self.discuss) + ":" + self.user.username + ":" + self.text
		
# 4th phase: free text
class FreeComment(models.Model):
	user = models.ForeignKey(User)
	discuss = models.ForeignKey(Discussion)
	text = models.TextField()
	time = models.DateTimeField(auto_now=True)
	def __unicode__(self):
		return str(self.discuss) + ":" + self.user.username + ":" + self.text