import requests, os

headers = {
  'Accept': 'application/vnd.github+json',
  'Authorization': f'Bearer {os.environ["TOKEN"]}',
  'X-GitHub-Api-Version': '2022-11-28',
}

def get_user_commits(login, after='2000-01-01T00:00:00Z'):
  commits = []
  total = 1
  page = 1
  while len(commits) < total:
    response = requests.get(f'https://api.github.com/search/commits?q=author:{login}+author-date:>{after}&page={page}&per_page=100&sort=author-date', headers=headers).json()
    print(response)
    total = response['total_count']
    commits.extend(response['items'])
    page += 1
  
  return commits

def get_user_prs_count(login):
  response = requests.get(f'https://api.github.com/search/issues?q=is:pr+author:{login}', headers=headers).json()
  print(os.environ["TOKEN"][:4], response)
  return response['total_count']
  

def process_commit(commit):
  response = requests.get(commit['url'], headers=headers).json()
  stats = response['stats']
  commiter = commit['commit']['author']
  return commiter['date'], stats['additions'], stats['deletions']
    
if __name__ == '__main__':
  commits = get_user_commits('getuliobr')
  print(process_commit(commits[1]))
  print(get_user_prs_count('getuliobr'))