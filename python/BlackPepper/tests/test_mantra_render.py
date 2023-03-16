from unittest import TestCase
from BlackPepper.mantra_render import set_mantra_for_render


class TestAuto_log(TestCase):
    def test_set_mantra_for_render(self):
        self.man = set_mantra_for_render()
