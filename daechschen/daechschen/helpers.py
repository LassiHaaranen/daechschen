import json, urllib2

from django.contrib.auth.models import User


#TODO: move to settings
server_url = "http://localhost:8080"

def load_json(uri):
  """
  Returns json data from uri as a Python object
  @param uri: uri to retrieve json data
  """  
  return json.load(urllib2.urlopen(uri))

def get_userprofile(user_id):
  """
  Returns userprofile from bserve based on user_id
  @param user_id: user_id in A+
  """
  #user_info = load_json(server_url + '/api/v1/userprofile/' + str(user_id) + '/?format=json') 
  user_profile, created = UserProfile.objects.get_or_create(id=user_id)
  return user_profile

def get_user_course_instance_summary(user_id,course_instance_id):
  course_summary = load_json(server_url + 
                              "/api/v1/course_result/"+str(course_instance_id) + "/user/" +
                              str(user_id) + "/?format=json"    )
  return course_summary
