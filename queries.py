import requests, os
from hashing import sha256

USER_INFO = '''
query ($login: String!) {
  user(login: $login) {
    id
    pullRequests(first: 1) {
      totalCount
    }
  }
}
'''

REPOS_AFFILIATED = '''
query ($owner_affiliation: [RepositoryAffiliation], $login: String!, $cursor: String) {
  user(login: $login) {
    repositories(first: 100, after: $cursor, ownerAffiliations: $owner_affiliation) {
      edges {
        node {
          ... on Repository {
            nameWithOwner
            defaultBranchRef {
              target {
                ... on Commit {
                  id
                }
              }
            }
          }
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
'''

COMMITS_IN_REPO = '''
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    defaultBranchRef {
      target {
				... on Commit {
          history(first:100, after: $cursor) {
            edges {
              node {
                author {
                  user {
                    id
                  }
                }
                deletions
                additions
                id
                committedDate
              }
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
      }
    }
  }
}
'''

'''

'''

def query(query, variables):
  return requests.post(
      'https://api.github.com/graphql',
      json = {'query': query, 'variables': variables},
      headers={
          'Authorization': f'bearer {os.environ["TOKEN"]}'
      }
  ).json()
  
def get_affiliated_repos(cursor='', login='getuliobr'):
  data = query(REPOS_AFFILIATED, {'login': login, 'cursor': cursor})['data']['user']['repositories']
  repos: list = list(map(lambda x: (
    x['node']['nameWithOwner'],
    sha256(x['node']['defaultBranchRef']['target']['id'])
  ), data['edges']))
  pagination = data['pageInfo']
  
  nextPage = pagination['hasNextPage']
  cursor = pagination['endCursor']
  
  if nextPage:
    repos.extend(get_affiliated_repos(cursor))
  return repos

def get_user_commits(repo, cursor=None):
  owner, name = repo.split('/')
  branch = query(COMMITS_IN_REPO, {'owner': owner, 'name': name, 'cursor': cursor})['data']['repository']['defaultBranchRef']
  if not branch:
    return
  data = branch['target']['history']
  commits: list = data['edges']
  pagination = data['pageInfo']
  
  nextPage = pagination['hasNextPage']
  cursor = pagination['endCursor']
  
  if nextPage:
    commits.extend(get_user_commits(repo, cursor))
  return commits

def get_user_info(login='getuliobr'):
  user = query(USER_INFO, {'login': login})['data']['user']
  id = user['id']
  prs = user['pullRequests']['totalCount']
  # TODO: count commits
  return id, prs, 0

def get_all_commits(login):
  headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {os.environ["TOKEN"]}',
    'X-GitHub-Api-Version': '2022-11-28',
  }

  commits = []
  total = 1
  page = 1
  while len(commits) < total:
    response = requests.get(f'https://api.github.com/search/commits?q=author:{login}&page={page}&per_page=100&sort=author-date', headers=headers).json()
    total = response['total_count']
    commits.extend(response['items'])
    page += 1
  
  return commits

def process_commit(commit):
  response = requests.get(commit['url']).json()
  stats = response['stats']
  commiter = commit['commit']['author']
  return commiter['date'], stats['additions'], stats['deletions']
    
if __name__ == '__main__':
  commits = get_all_commits('getuliobr')
  print(process_commit(commits[1]))