import json
import urllib2
import time

owner = 'eightamrock'
repo = 'launchbox'
token = '' #insert use auth token here
headers = {'Authorization': "token "+token}

def message(text):
  print text

def is_prod(data):
  return data['base']['ref'] == 'release'

def is_mergable(data):
  return data['mergeable'] is True and data['state'] == 'open'

def get_deploy_pr():
  can_deploy = False
  pr = 0

  while not can_deploy:
    pr = raw_input("Enter launch code: ")
    try:
      url = "https://api.github.com/repos/%s/%s/pulls/%s" % (owner, repo, pr)
      req = urllib2.Request(url, None, headers)
      content = urllib2.urlopen(req).read()
      results = json.loads(content)
      can_deploy = is_mergable(results) # and is_prod(results)
    except:
      can_deploy = False
    if not can_deploy:
      message("Unable to launch.")
      time.sleep(3)

  message("Ready to deploy %s commit(s)." % results['commits'])
  return pr

def merge_pr(num):
  url = "https://api.github.com/repos/%s/%s/pulls/%s/merge" % (owner, repo, num)
  print url

num = get_deploy_pr()
raw_input("Press enter to continue...")
merge_pr(num)
