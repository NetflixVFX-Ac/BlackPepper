"""

Model.py

"""
from pepper import Houpub


class PepM:

    def __init__(self):
        self.host = "http://192.168.3.116/api"
        self.email = "pepper@hook.com"
        self.pw = "pepperpepper"
        self.sel_software = "hip"

    def login_data(self, email, pw, sel_software):

        self.email = email
        self.pw = pw
        self.sel_software = sel_software
        pep = Houpub()
        pep.login(self.host, email, pw)
        pep.software = sel_software
        print(f"login id : {email} , seleted software : {sel_software}")

    def get_project(self):
        pep = Houpub()
        pep.get_my_projects()

    def get_temp(self, project_name):
        pep = Houpub()
        pep.project = project_name
        # print(pep.project)
        asset_list = pep.get_all_assets()
        # print(asset_list)
        return asset_list





# def main():
#     c = PepM()
#     # c.email = "pepper@hook.com"
#     # c.pw = "pepperpepper"
#     c.email = "pipeline@rapa.org"
#     c.pw = "netflixacademy"
#     c.sel_software = "hip"
#     c.login_data(c.email, c.pw, c.sel_software)
#     project_name = c.get_project()
#     c.get_temp(project_name[0])
#     # pass
#
#
# if __name__ == "__main__":
#     main()