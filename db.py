import sqlite3

connection = sqlite3.connect("contributions.db")

def upsert_contribution(repo, last_commit_id, additions, deletions, commits):
  cursor = connection.cursor()
  UPSERT = """
  INSERT INTO Contributions (
    repo,
    last_commit_id,
    additions,
    deletions,
    commits
  ) VALUES (?, ?, ?, ?, ?)
  ON CONFLICT(repo) DO UPDATE SET
    last_commit_id=excluded.last_commit_id,
    additions=excluded.additions,
    deletions=excluded.deletions,
    commits=excluded.commits
  WHERE repo=excluded.repo;
  """
  cursor.execute(UPSERT, (repo, last_commit_id, additions, deletions, commits))
  connection.commit()
  cursor.close()

def get_last_contribution(repo):
  SELECTION = """
  SELECT 
    last_commit_id,
    additions,
    deletions,
    commits
  FROM Contributions 
  WHERE repo = ?;
  """
  cursor = connection.execute(SELECTION, (repo,))
  result = cursor.fetchone()
  cursor.close()
  return result if result else ('undefined', 0, 0, 0)

def get_all_contributions():
  SELECTION = """
  SELECT 
    additions,
    deletions,
    commits
  FROM Contributions;
  """
  cursor = connection.execute(SELECTION, ())
  result = cursor.fetchall()
  cursor.close()
  return result

if __name__ == '__main__':
  print("Creating database")
  cursor = connection.cursor()
  CREATE_TABLE = """
  CREATE TABLE IF NOT EXISTS Contributions (
    repo TEXT PRIMARY KEY,
    last_commit_id TEXT,
    additions INTEGER,
    deletions INTEGER,
    commits INTEGER
  )
  """
  cursor.execute(CREATE_TABLE)
  connection.commit()
  cursor.close()