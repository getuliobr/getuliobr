from hashlib import sha256 as _sha256

def sha256(data: str):
  return _sha256(data.encode('utf-8')).hexdigest()