class AuthService:
    def __init__(self, users_db):
        self.users_db = users_db

    def verify(self, username, password):
        return self.users_db.verify_login(username, password)

    def get_users(self):
        return self.users_db.get_all_users()
