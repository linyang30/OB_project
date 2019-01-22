import yaml
import logging
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import subprocess
import re
import os
import time
from airtest.core.api import connect_device, install, uninstall, exists, Template, keyevent, touch


class Common:

    def __init__(self, device_name, phone_ip, phone_port):
        logging.info('Common init')
        self.device_name = device_name
        self.phone_ip = phone_ip
        self.phone_port = phone_port
        self.base_dir = self.get_base_dir()
        self.data = self.get_config_data()
        self.app_name = self.get_app_name()
        self.apk_path = self.get_apk_path()
        self.package, self.version_code, self.version_name = self.get_apk_info()
        self.connect_phone()
        self.init_phone()
        self.poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        self.resolution = self.get_device_screen_display()
        self.threshold = 0.7

    def get_config_data(self):
        logging.info('get_config_data')
        with open('../config/config.yaml', 'r') as file:
            data = yaml.load(file)
        return data

    def get_poco(self):
        logging.info('get_poco')
        poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        return poco

    def get_current_time(self):
        logging.info('get_current_time')
        now = time.strftime('%Y-%m-%d-%H-%M-%S')
        return now

    def exec_command(self, command_str):
        logging.info('exec_command: ' + command_str)
        p = subprocess.Popen(command_str, shell=True, stdout=subprocess.PIPE)
        out = p.stdout.read().decode('utf-8')
        return out

    def get_device_info(self):
        command = 'adb -s ' + self.device_name + ' shell cat /system/build.prop'
        out = self.exec_command(command)
        manufacturer = re.findall(r'ro.product.manufacturer=(\w+)', out)[0]
        command_name = 'adb -s ' + self.device_name + ' shell getprop ro.product.model'
        out_name = self.exec_command(command_name)
        name = out_name.strip()
        return manufacturer + '_' + name

    def get_device_screen_display(self):
        command = 'adb -s ' + self.device_name + ' shell wm size'
        out = self.exec_command(command)
        result = re.findall(r'Physical :size\s+(\d+)x(\d+)', out)[0]
        return [int(x) for x in result]

    def init_phone(self):
        logging.info('init_phone')
        device = 'Android://' + self.data['adb_host_ip'] + ':' + str(self.data['adb_host_port']) + '/' + self.device_name + '?ori_method=' + str(self.data['connect_func'])
        logging.info(device)
        connect_device(device)

    def get_base_dir(self):
        logging.info('get_base_dir')
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return base_dir

    def get_app_name(self):
        logging.info('get_app_name')
        app_dir = os.path.join(self.base_dir, 'app')
        return os.listdir(app_dir)[0]

    def get_apk_path(self):
        logging.info('get_apk_path')
        apk_path = os.path.join(self.base_dir, 'app', self.app_name)
        return apk_path

    def get_apk_info(self):
        logging.info('get_apk_info')
        apk_path = self.apk_path
        command = 'aapt dumpsys badging ' + apk_path
        out = self.exec_command(command)
        package = re.findall(r'package\: name=\'([\w\.]+)\'', out)[0]
        version_code = re.findall(r'versionCode=\'(\d+)\'', out)[0]
        version_name = re.findall(r'versionName=\'([\d\.]+)\'', out)[0]
        apk_info = {}
        apk_info['package'] = package
        apk_info['version_code'] = version_code
        apk_info['version_name'] = version_name
        return package, version_code, version_name


    def is_install(self):
        '''应用正确安装返回1， 应用已安装，但版本不一致返回2， 应用未安装返回0'''
        logging.info('is_install')

        command = 'adb -s ' + self.device_name + ' shell dumpsys package ' + self.package
        out = self.exec_command(command)
        if out.strip():
            current_version_code = re.findall(r'versionCode=(\d+)', out)[0]
            current_version_name = re.findall(r'versionName=([\d+\.]+)', out)[0]
            if current_version_code == self.version_code and current_version_name == self.version_name:
                return 1
            else:
                return 2
        else:
            return 0

    def install_app(self):
        logging.info('install_app')
        install(self.apk_path)


    def uninstall_app(self):
        logging.info('uninstall_app')
        uninstall(self.package)

    def img_element_exists(self, img_file, is_rgb):
        return exists(Template(filename=img_file, threshold=self.threshold, resolution=self.resolution, rgb=is_rgb))

    def exit_app(self):
        logging.info('exit_app')
        confir_exit_btn = 'com.orbbec.gdgamecenter:id/confir_exit_btn'
        keyevent("BACK")
        time.sleep(5)
        self.poco(confir_exit_btn).click()
        # if self.img_element_exists('../action_imgs/exit_btn.png', False):
        #     logging.info('find it')
        #     self.click_img('../action_imgs/exit_btn.png', False)
        time.sleep(5)

    def skip_upgrade(self):
        logging.info('skip_upgrade')
        cancel_button = 'com.android.packageinstaller:id/cancel_button'
        if self.poco(cancel_button).exists():
            self.poco(cancel_button).click()
        time.sleep(5)

    def skip_notice(self):
        logging.info('skip_notice')
        notice_btn = 'com.orbbec.gdgamecenter:id/btn'
        if self.poco(notice_btn).exists():
            self.poco(notice_btn).click()
        time.sleep(5)

    def connect_phone(self):
        logging.info('connect_phone')
        time.sleep(1)
        command = 'adb connect ' + self.phone_ip + ':' + str(self.phone_port)
        out = self.exec_command(command)
        pattern = re.compile('already connected to ' + str(self.phone_ip) + ':' + str(self.phone_port))
        result_list = pattern.findall(out)
        result = result_list[0] if len(result_list) > 0 else 'None'
        if result == 'already connected to ' + str(self.phone_ip) + ':' + str(self.phone_port):
            logging.info('connect phone success')
            time.sleep(1)
        else:
            self.connect_phone()

    def reset_adb(self):
        logging.info('reset_adb')
        time.sleep(1)
        command_kill_server = 'adb kill-server'
        command_start_server = 'adb start-server'
        self.exec_command(command_kill_server)
        time.sleep(1)
        out = self.exec_command(command_start_server)
        result = re.findall(r'daemon started successfully', out)
        if result[0] == 'daemon started successfully':
            logging.info('reset adb success')
            time.sleep(1)
        else:
            self.reset_adb()

    def disconnect_phone(self):
        logging.info('disconnect_phone')
        time.sleep(1)
        command = 'adb disconnect'
        out = self.exec_command(command)
        result = re.findall(r'disconnected everything', out)
        if result[0] == 'disconnected everything':
            logging.info('disconnect phone success')
            time.sleep(1)
        else:
            self.disconnect_phone()

    def click_img(self, img_file, is_rgb):
        logging.info('click_element')
        touch(Template(filename=img_file, threshold=self.threshold, resolution=self.resolution, rgb=is_rgb))

if __name__ == '__main__':
    comm = Common('192.168.137.158:30016', '192.168.137.158', 30016)
    print(comm.get_device_info())








