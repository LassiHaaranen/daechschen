
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.auth.models import AbstractUser
from django.conf import settings 

class BadgeUser(AbstractUser):
  # TODO: show/hide badges in the side bar view based on this
  show_badges = models.BooleanField(default=True)

class KnowsChild(models.Model):
  """
  See: http://blog.headspin.com/?p=474
  """
  # Make a place to store the class name of the child
  _my_subclass = models.CharField(max_length=200)

  class Meta:
    abstract = True

  def as_child(self):
    return getattr(self, self._my_subclass)

  def save(self, *args, **kwargs):
    # Save what kind of badge we are
    self._my_subclass = self.__class__.__name__.lower()
    super(KnowsChild, self).save(*args, **kwargs)

class Badge(KnowsChild):
  name            = models.CharField("Name of the badge",max_length=50)
  description     = models.CharField("Description of the badge", max_length=127)
  graphics_file   = models.FileField(upload_to="badge")
  course_instance = models.IntegerField("Instance resource")
  hidden          = models.BooleanField("Hides the badge initially", default=False)

  def filename(self):
    return os.path.basename(self.graphics_file.name)

  def get_url(self):
    return  "/badge/" + str(self.id) + "/"

  def __unicode__(self):
    return self.name + " (" +self._my_subclass + ")"

class PerfectScoresOnCourseBadge(Badge):
  """
  Badge for requiring a certain amount of perfect submissions for exercises
  (i.e. maximum points for the exercise) and that there are maximum
  of attempts_allowed submissions for each exercise.

  If attempts_allowed is set to 1, it means that the student must submit a 
  fully correct submission on the first try.
  """
  perfect_scores_required = models.IntegerField("How many perfect scores are required")
  attempts_allowed        = models.IntegerField("How many submissions per exercise are allowed")
  counted_modules         = models.CommaSeparatedIntegerField(max_length=64)

  def check_for_user(self, course_summary, user_id=None):    
    perfect_score_count = 0
    counted_modules = eval(self.counted_modules)

    for rnd in course_summary["summary"]:
      for ex in rnd["exercise_summaries"]:
        if (ex["completed_percentage"] == 100 and 
        ex["submission_count"] <= self.attempts_allowed and
        rnd["exercise_round_id"] in counted_modules):
          perfect_score_count += 1    

    if perfect_score_count >= self.perfect_scores_required:
      return True
    return False

class EarlySubmissionBadge(Badge):
  """
  A course module (i.e. round) based badge to be awarded if percentage_required
  of the rounds maximum points are submitted before the round closes, determined
  by early_time (in seconds).
  """
  early_time                    = models.IntegerField("Time required to be early in seconds")
  course_module                 = models.IntegerField("Course module")
  percentage_required           = models.IntegerField("Percentage required")

  def check_for_user(self, course_summary, user_id=None):
    for rnd in course_summary["summary"]:
      if rnd["exercise_round_id"] == self.course_module:
        closing_time = parser.parse(rnd["closing_time"])
        difference = closing_time - datetime.now()
        difference_in_seconds = difference.days * 86500 + difference.seconds
        if (difference_in_seconds >= self.early_time 
        and rnd["completed_percentage"] >= self.percentage_required):        
          return True
        else:
          return False
    return False

class MinimumGradeOnRoundBadge(Badge):
  """
  A course module (i.e. round) based badge to be awarded if score_required 
  amount of points is achieved.
  """
  round_id           = models.IntegerField("Id of the round")
  score_percentage   = models.IntegerField("Minimum percentage to get from the round to achieve the badge")
  
  def check_for_user(self, course_summary, user_id=None):
    for rnd in course_summary["summary"]:
      if rnd['exercise_round_id'] == self.round_id:       
        if rnd["completed_percentage"] >= self.score_percentage:
          return True
        return False
    return False


class MetaBadge(Badge):
  """
  Meta badges are awarded when user has achieved all of the badges set in
  required_badges.
  """
  required_badges   = models.ManyToManyField(Badge, related_name="badge_required")

  def check_for_user(self,course_summary, user_id=None):
    user = BadgeUser.objects.get(id=course_summary["user"])
    user_badges = AwardedBadge.objects.filter(user=user)
    for badge in self.required_badges.all():
      badge_found = False
      for user_badge in user_badges:
        if badge == user_badge.badge:
          badge_found = True
      if badge_found == False:
        return False
    return True

class AwardedBadge(models.Model):
  """
  Model for storing what badges users have achieved and when.
  """
  badge     = models.ForeignKey(Badge, related_name="badge")
  user      = models.ForeignKey(BadgeUser, related_name="user")
  awarded   = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return self.badge.name + " -> " + str(self.user.id)


