from svgparser import SVGParser
from queries import get_user_commits, get_user_prs_count, process_commit
import json
  
svg = SVGParser('base.svg')

with open('info.json', 'r+') as jsonFile:
  data = json.load(jsonFile)


latestCommitDate = data['latestCommitDate']

commits = get_user_commits('getuliobr', after=latestCommitDate)
data['latestCommitDate'] = None

for commit in commits:
  date, addi, dele = process_commit(commit)
  
  if not data['latestCommitDate']:
    data['latestCommitDate'] = date
  
  data['additions'] += addi
  data['deletions'] += dele
  data['commits'] += 1

data['latestCommitDate'] = latestCommitDate

svg.update('additions', f'+{data["additions"]}')
svg.update('deletions', f'-{data["deletions"]}')
svg.update('commits', f'{data["commits"]}')
svg.update('prs', get_user_prs_count('getuliobr'))

svg.write('out.svg')

with open('info.json', 'w') as jsonFile:
  json.dump(data, jsonFile)