import bcrypt

def get_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

if get_hash("admin") == "$2b$12$u6zXtEDN1YcdNEaQO6oaCeBVKExDWlt8yebHOBK82f0ODR7d.7rBO":
    print(True)