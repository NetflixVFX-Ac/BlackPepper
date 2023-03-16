from unittest import TestCase
from BlackPepper.ui.auto_login import Auto_log


class TestAuto_log(TestCase):

    def setUp(self):
        self.auto = Auto_log()
        self.auto.valid_host = False
        self.auto.valid_user = False
        self.auto.auto_login = False
        self.auto.host = "http://192.168.3.116/api"
        self.auto.user_id = "pipeline@rapa.org"
        self.auto.user_pw = "netflixacademy"
        self.auto.user_ext = "hipnc"
        self.auto.user = "pipeline@rapa.org"
        # self.auto.user_path = '/home/rapa/git/hook/python/BlackPepper/config/user.json'

    def test_home_json_path(self):
        self.auto.home_json_path()
        self.assertNotEqual('/home/rapa/git/hook/python/config', self.auto.dir_path)
        self.assertEqual('/home/rapa/git/hook/python/BlackPepper/.config', self.auto.dir_path)
        self.assertNotEqual('/home/rapa/git/hook/python/config', self.auto.user_path)
        self.assertEqual('/home/rapa/git/hook/python/BlackPepper/config/user.json', self.auto.user_path)

    def test_connect_login(self):
        self.auto.connect_login()
        self.assertTrue(self.auto.valid_host)
        self.assertTrue(self.auto.valid_user)
        self.assertNotEqual(self.auto.user_dict['auto'], [])
        for i in self.auto.user_dict['auto']:
            self.assertTrue(i['valid_host'])
            self.assertTrue(i['valid_user'])
        self.assertTrue(self.auto.connect_login())

    def test_log_out(self):
        self.auto.connect_login()
        self.auto.log_out()
        self.assertIsNone(self.auto.user)
        self.assertEqual(self.auto.host, '')
        self.assertEqual(self.auto.user_id, '')
        self.assertEqual(self.auto.user_pw, '')
        self.assertEqual(self.auto.user_ext, '')
        self.assertFalse(self.auto.valid_host)
        self.assertFalse(self.auto.valid_user)
        self.assertFalse(self.auto.auto_login)

    def test_save_setting(self):
        self.auto.save_setting()
        self.assertNotEqual(self.auto.user_dict['auto'], {})
        for i in self.auto.user_dict['auto']:
            self.assertEqual(i['host'], self.auto.host)
            self.assertEqual(i['user_id'], self.auto.user_id)
            self.assertEqual(i['user_pw'], self.auto.user_pw)
            self.assertEqual(i['user_ext'], self.auto.user_ext)
            self.assertEqual(i['valid_host'], self.auto.valid_host)
            self.assertEqual(i['valid_user'], self.auto.valid_user)
            self.assertEqual(i['auto_login'], self.auto.auto_login)

    def test_reset_setting(self):
        self.auto.reset_setting()
        self.assertEqual(self.auto.host, '')
        self.assertEqual(self.auto.user_id, '')
        self.assertEqual(self.auto.user_pw, '')
        self.assertEqual(self.auto.user_ext, '')
        self.assertFalse(self.auto.valid_host)
        self.assertFalse(self.auto.valid_user)
        self.assertFalse(self.auto.auto_login)
        self.assertNotEqual(self.auto.user_dict['auto'], {})
        for i in self.auto.user_dict['auto']:
            self.assertEqual(i['host'], '')
            self.assertEqual(i['user_id'], '')
            self.assertEqual(i['user_ext'], '')
            self.assertFalse(i['valid_host'])
            self.assertFalse(i['valid_user'])
            self.assertFalse(i['auto_login'])
