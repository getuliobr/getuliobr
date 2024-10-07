from svgparser import SVGParser
from queries import get_user_commits, get_user_languages_percentage, get_user_prs_count, process_commit
import json
  
svg = SVGParser('base.svg')

with open('info.json', 'r+') as jsonFile:
  data = json.load(jsonFile)


commits = get_user_commits('getuliobr', after=data['latestCommitDate'])

if len(commits):
  data['latestCommitDate'], _, _ = process_commit(commits[0])

for commit in commits:
  _, addi, dele = process_commit(commit)
  
  # Uncomment to ignore node_modules and templates
  data['additions'] += addi # if addi < 10000 else 0
  data['deletions'] += dele # if dele < 10000 else 0
  data['commits'] += 1

svg.update('additions', f'+{data["additions"]}')
svg.update('deletions', f'-{data["deletions"]}')
svg.update('commits', f'{data["commits"]}')
svg.update('prs', get_user_prs_count('getuliobr'))

languages = get_user_languages_percentage('getuliobr')
for i in range(5):
  name, percentage = languages[i]
  hashSize = int(percentage * 20//100)
  dashSize = 20 - hashSize
  
  rightPart = f'({int(percentage)}%) [{"#" * hashSize}{"-" * dashSize}]'
  
  # 40 string size - percentage part - 1 space
  maxNameSize = 40 - len(rightPart) - 1
  # format name
  name = name[:maxNameSize]
  #fill with the name and remaining fill with spaces to align
  leftPart = f'{name}{" " * (maxNameSize - len(name))}'
  
  svg.update(f'top{i+1}', f'{leftPart} {rightPart}')
  

svg.write('out.svg')

with open('info.json', 'w') as jsonFile:
  json.dump(data, jsonFile)