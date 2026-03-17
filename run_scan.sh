#!/bin/bash
# 每4小时运行一次

cd /root/.bounty-hunter
/usr/bin/python3 auto_scanner.py >> auto_scan.log 2>&1
