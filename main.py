import os
from hashing import sha256
from db import get_last_contribution, upsert_contribution, get_all_contributions
from queries import get_user_info, get_affiliated_repos, get_user_commits
from svgparser import SVGParser

MY_ID = None

if __name__ == '__main__':
  svg = SVGParser('base.svg')
  
  MY_ID, prs, commits = get_user_info()
  repos = get_affiliated_repos()
    
  for repo, hashedCommitId in repos:
    # We use hashed names to prevent leaking stuff
    hashedRepo = sha256(repo)
    
    last_commit_id, repoAdditions, repoDeletions, repoCommits = get_last_contribution(hashedRepo)

    # if nothing new, just go to next repo
    if hashedCommitId == last_commit_id:
      continue

    # THE FIRST COMMIT FROM NOW BECOMES THE LAST IN THE NEXT UPDATE,
    # THATS WHY WE SAVE IT AS last_commit_id
    for commit in get_user_commits(repo):
      commit = commit['node']
            
      user = commit['author']['user']
      if not user or user['id'] != MY_ID:
        continue
      
      repoCommits += 1
      # uncomment to ignore accidental node_modules commits and templates
      repoAdditions += commit['additions'] # if commit['additions'] < 10000 else 0
      repoDeletions += commit['deletions'] # if commit['deletions'] < 10000 else 0
    
    upsert_contribution(hashedRepo, hashedCommitId, repoAdditions, repoDeletions, repoCommits)
    print(f'{hashedRepo[:16]}: +{repoAdditions} -{repoDeletions} on {repoCommits} commits')


  additions = 0
  deletions = 0

  for repoAdd, repoDel, repoCommit in get_all_contributions():
    additions += repoAdd
    deletions += repoDel
  
  svg.update('additions', f'+{additions}')
  svg.update('deletions', f'-{deletions}')
  svg.update('commits', f'{commits}')
  svg.update('prs', prs)
  
  svg.write('out.svg')