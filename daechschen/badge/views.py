from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from badge.models import *
from helpers import *

import random

def user_course_summary_view(request): 
  user_id = request.GET.get('user_profile_id')
  user, created = BadgeUser.objects.get_or_create(id=user_id, defaults={'username': user_id})
  if created and random.randint(0,1) == 1:
    user.experimental_group = 1
    user.save()
  course_id = request.GET.get('course_instance_id')  

  if None in [course_id,user_id]:
    return HttpResponseBadRequest()

  course_summary =  get_user_course_instance_summary(user_id,course_id)  
  
  badges = Badge.objects.filter(course_instance=course_id) 
  user_badges = AwardedBadge.objects.filter(user=user).filter(badge__course_instance=course_id).order_by('-awarded')
  available_badges = []
  awarded_badges = []

  for badge in badges.all():
    if not AwardedBadge.objects.filter(badge=badge, user=user):
      if badge.as_child().check_for_user(course_summary):
        a = AwardedBadge(badge=badge, user=user)
        a.save()
        awarded_badges.append(a)  
      else:
        available_badges.append(badge)

  base_url = request.build_absolute_uri('/')[:-1] 

  return render_to_response('user_summary.html', { 
                                                  "all_badges": badges,    
                                                  "badges": available_badges,
                                                  "user_badges": user_badges,
                                                  "awarded_badges": awarded_badges,
                                                  "base_url": base_url,
                                                  "show_badges": user.show_badges,
                                                  "user_id":  user_id,
                                                  "user_hash": user.user_hash
                                                }) 

def user_course_view(request): 
  user_id = request.GET.get('user_profile_id')
  course_id = request.GET.get('course_instance_id')  
  
  if None in [course_id,user_id]:
    return HttpResponseBadRequest()
  
  course_summary =  get_user_course_instance_summary(user_id,course_id)  
  badges = Badge.objects.filter(course_instance=course_id)
  awarded_badges = []
  user, created = BadgeUser.objects.get_or_create(id=user_id, defaults={'username': user_id})

  if created and random.randint(0,1) == 1:
    user.experimental_group = 1
    user.save()

  for badge in badges.all():
    if not AwardedBadge.objects.filter(badge=badge, user=user):
      if badge.as_child().check_for_user(course_summary):
        a = AwardedBadge(badge=badge, user=user)
        a.save()
        awarded_badges.append(a)

  user_badges = AwardedBadge.objects.filter(user=user).order_by('-awarded')
  base_url = request.build_absolute_uri('/')[:-1] 

  return render_to_response('user.html', { "awarded_badges": awarded_badges,
                                                  "user_badges": user_badges,
                                                  "base_url": base_url,
                                                  "show_badges": user.show_badges
                                                }) 

@require_POST
@csrf_exempt
def toggle_badges(request):
  user_id = request.POST.get('user_id')
  user_hash = request.POST.get('user_hash')
  print request.POST
  if user_id == None:
    return HttpResponseBadRequest()

  #User should be created at this point
  user = BadgeUser.objects.get(id=user_id)
  if(user.user_hash == user_hash):
    user.show_badges = not user.show_badges    
    user.save()
    history = ToggleHistory.objects.create(user=user, new_value=user.show_badges)
    history.save()

  return HttpResponse(content=user.show_badges)
    