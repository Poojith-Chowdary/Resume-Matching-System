class HRUser:
    def __init__(self, email, password=None, oauth_provider=None):
        self.email = email
        self.password = password
        self.oauth_provider = oauth_provider
