from collections import defaultdict
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
    total = response['total_count']
    commits.extend(response['items'])
    page += 1
  
  return commits

def get_user_prs_count(login):
  response = requests.get(f'https://api.github.com/search/issues?q=is:pr+author:{login}', headers=headers).json()
  return response['total_count']

def process_commit(commit):
  response = requests.get(commit['url'], headers=headers).json()
  stats = response['stats']
  commiter = commit['commit']['author']
  return commiter['date'], stats['additions'], stats['deletions']

def graphql(query, variables):
  return requests.post(
      'https://api.github.com/graphql',
      json = {'query': query, 'variables': variables},
      headers={
          'Authorization': f'bearer {os.environ["TOKEN"]}'
      }
  ).json()

def get_user_languages_percentage(login):
  # https://raw.githubusercontent.com/anuraghazra/github-readme-stats/refs/heads/master/src/fetchers/top-languages-fetcher.js
  """
  MIT License

  Copyright (c) 2020 Anurag Hazra

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
  """
  LANGUAGES_QUERY = """
  query userInfo($login: String!) {
    user(login: $login) {
      # fetch only owner repos & not forks
      repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
        nodes {
          name
          languages(first: 100, orderBy: {field: SIZE, direction: DESC}) {
            edges {
              size
              node {
                color
                name
              }
            }
          }
        }
      }
    }
  }
  """
  repositories = graphql(LANGUAGES_QUERY, {'login': login})['data']['user']['repositories']['nodes']
  languages = defaultdict(int)
  total = 0
  for repo in repositories:
    for language in repo['languages']['edges']:
      name = language['node']['name']
      size = language['size']
      languages[name] += size
      total += size
  
  for language in languages:
    languages[language] *= 100/total 
  
  return sorted(languages.items(), key=lambda x: x[1])[::-1]