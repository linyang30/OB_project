import logging

class LaunchView:

    default_focus_img = '../action_imgs/default_focus.png'

    def __init__(self, comm):
        self.comm = comm

    def launch_verify(self):
        logging.info('launch_verify')
        if self.comm.img_element_exists(self.default_focus_img, True):
            return True
        else:
            return False
