import unittest
from HTMLTestRunner import HTMLTestRunner
from common.common_func import Common
import multiprocessing
import yaml
from common.base_unit import BaseUnit
from test_case.test_launch import TestLaunch
import logging
import time
import re
import subprocess


def exec_command(command_str):
    logging.info('exec_command: ' + command_str)
    p = subprocess.Popen(command_str, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.read().decode('utf-8')
    return out

def reset_adb():
    logging.info('reset_adb')
    time.sleep(1)
    command_kill_server = 'adb kill-server'
    command_start_server = 'adb start-server'
    exec_command(command_kill_server)
    time.sleep(1)
    out = exec_command(command_start_server)
    result = re.findall(r'daemon started successfully', out)
    if result[0] == 'daemon started successfully':
        logging.info('reset adb success')
        time.sleep(1)
    else:
        reset_adb()

def run(device_name, phone_ip, phone_port):
    comm = Common(device_name, phone_ip, phone_port)
    result = comm.is_install()
    if result == 2:
        comm.uninstall_app()
        comm.install_app()
    elif result == 0:
        comm.install_app()

    test_report_dir = '../test_report/'
    test_report_name = comm.get_device_info() + '_' + comm.get_current_time() + '_test_report.html'

    suite = unittest.TestSuite()
    suite.addTest(BaseUnit.parametrize(TestLaunch, comm))

    with open(test_report_dir + test_report_name, 'wb') as f:
        runner = HTMLTestRunner(f)
        runner.run(suite)

if __name__ == '__main__':

    reset_adb()
    with open('../config/config.yaml', 'r') as file:
        data = yaml.load(file)
    run_process = []
    for phone in data['devices']:
        p = multiprocessing.Process(target=run, args=(phone['device_name'], phone['phone_ip'], phone['phone_port']))
        run_process.append(p)

    for p in run_process:
        p.start()
    for p in run_process:
        p.join()

