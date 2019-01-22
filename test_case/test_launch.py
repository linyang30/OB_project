from common.my_unit import MyUnit
from bussiness_view.launch_view import LaunchView
import unittest

class TestLaunch(MyUnit):


    def test_launch(self):
        lv = LaunchView(self.param)
        assert lv.launch_verify()

if __name__ == '__main__':
    unittest.main()