from svgparser import SVGParser
from queries import get_user_commits, get_user_prs_count, process_commit
import json
  
svg = SVGParser('base.svg')

with open('info.json', 'r+') as jsonFile:
  data = json.load(jsonFile)


commits = get_user_commits('getuliobr', after=data['latestCommitDate'])

if len(commits):
  data['latestCommitDate'], _, _ = process_commit(commits[0])

for commit in commits:
  _, addi, dele = process_commit(commit)
   
  data['additions'] += addi
  data['deletions'] += dele
  data['commits'] += 1

svg.update('additions', f'+{data["additions"]}')
svg.update('deletions', f'-{data["deletions"]}')
svg.update('commits', f'{data["commits"]}')
svg.update('prs', get_user_prs_count('getuliobr'))

svg.write('out.svg')

with open('info.json', 'w') as jsonFile:
  json.dump(data, jsonFile)