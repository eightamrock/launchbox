import urllib2
import time
import pytz
import datetime
import json
from libs import requests
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config.cfg')

owner = config.get('github', 'owner')
repo = config.get('github', 'repository')
token = config.get('github', 'token')
try:
  target_branch = config.get('github', 'target_branch')
except ConfigParser.NoOptionError:
  target_branch = None
headers = {
  'Authorization': "token "+token,
  'User-Agent': 'LaunchBox'
}
time_fmt = '%b %d, %Y %H:%M:%S %Z'

def message(text):
  print text

def is_target(data):
  return target_branch == None or data['base']['ref'] == target_branch

def is_mergable(data):
  return data['mergeable'] is True and data['state'] == 'open'

def get_deploy_pr():
  can_deploy = False
  pr = 0

  while not can_deploy:
    pr = raw_input("Enter launch code: ")
    url = "https://api.github.com/repos/%s/%s/pulls/%s" % (owner, repo, pr)
    req = requests.get(url, headers=headers)
    results = req.json()
    can_deploy = req.status_code == 200 and is_mergable(results) and is_target(results)
    if not can_deploy:
      message("Unable to launch.")
      time.sleep(3)

  message("Ready to deploy %s commit(s)." % results['commits'])
  return pr

def merge_pr(num):
  timestamp = datetime.datetime.now(pytz.timezone("America/New_York"));
  payload = {
    'commit_message': "LaunchBox Release - " + timestamp.strftime(time_fmt)
  }
  url = "https://api.github.com/repos/%s/%s/pulls/%s/merge" % (owner, repo, num)
  res = requests.put(url, data=json.dumps(payload), headers=headers)
  if res.json()['merged']:
    message("Deploying")
  else :
    message("Could not deploy - " + res.json()['message'])

num = get_deploy_pr()
raw_input("Press enter to continue...")
merge_pr(num)


#test 4
