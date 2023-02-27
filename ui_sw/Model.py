"""

Model.py

"""
from pepper import Houpub


class PepM:

    def __init__(self):
        self.host = "http://192.168.3.116/api"
        self.email = None
        self.pw = None
        self.sel_software = None
        self.project_list = None

    def login_model(self, email, pw, sel_software):

        self.email = email
        self.pw = pw
        pepper = Houpub()
        pepper.login(self.host, email, pw)
        pepper.software = sel_software
        print(f"login id : {email} , seleted software : {sel_software}")

    def main_model(self):
        pepper = Houpub()
        get_myproject = pepper.get_my_projects()
        print(f"get user project : {get_myproject}")

