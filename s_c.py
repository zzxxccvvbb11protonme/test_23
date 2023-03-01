#!/usr/bin/env python3
# coding: utf-8

import logging
import os
import socket
import time

import psutil
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INTERVAL = 3

app = Flask(__name__)

intervals = (
    # ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),  # 60 * 60 * 24
    ('hours', 3600),  # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


def get_uptime():
    return int(time.time() - psutil.boot_time())


def get_memory():
    virtual_memory = psutil.virtual_memory()
    return virtual_memory.total / 1024.0, virtual_memory.used / 1024.0


def get_swap():
    swap_memory = psutil.swap_memory()
    return swap_memory.total / 1024.0, swap_memory.used / 1024.0


def get_hdd():
    valid_fs = ["ext4", "ext3", "ext2", "reiserfs", "jfs", "btrfs", "fuseblk", "zfs", "simfs", "ntfs", "fat32", "exfat",
                "xfs"]
    disks = dict()
    size = 0
    used = 0
    for disk in psutil.disk_partitions():
        if not disk.device in disks and disk.fstype.lower() in valid_fs:
            disks[disk.device] = disk.mountpoint
    for disk in disks.values():
        usage = psutil.disk_usage(disk)
        size += usage.total
        used += usage.used
    return int(size / 1024.0 / 1024.0), int(used / 1024.0 / 1024.0)


def get_cpu():
    return psutil.cpu_percent(interval=INTERVAL)


def liuliang():
    net_in = 0
    net_out = 0
    net = psutil.net_io_counters(pernic=True)
    for k, v in net.items():
        if 'lo' in k or 'tun' in k \
                or 'docker' in k or 'veth' in k \
                or 'br-' in k or 'vmbr' in k \
                or 'vnet' in k or 'kube' in k:
            continue
        else:
            net_in += v[1]
            net_out += v[0]
    return net_in, net_out


def tupd():
    try:
        t = int(os.popen('ss -t|wc -l').read()[:-1]) - 1
        u = int(os.popen('ss -u|wc -l').read()[:-1]) - 1
        p = int(os.popen('ps -ef|wc -l').read()[:-1]) - 2
        d = int(os.popen('ps -eLf|wc -l').read()[:-1]) - 2

        return t, u, p, d
    except Exception as e:
        return 0, 0, 0, 0


def get_network(ip_version):
    host = ''
    if ip_version == 4:
        host = "ipv4.google.com"
    elif ip_version == 6:
        host = "ipv6.google.com"

    try:
        socket.create_connection((host, 80), 2).close()
        return True
    except Exception as e:
        return False


def net_speed():
    avgrx = 0
    avgtx = 0
    for name, stats in psutil.net_io_counters(pernic=True).items():
        if "lo" in name or "tun" in name \
                or "docker" in name or "veth" in name \
                or "br-" in name or "vmbr" in name \
                or "vnet" in name or "kube" in name:
            continue
        avgrx += stats.bytes_recv
        avgtx += stats.bytes_sent

    time.sleep(INTERVAL)

    avgrx2 = 0
    avgtx2 = 0
    for name, stats in psutil.net_io_counters(pernic=True).items():
        if "lo" in name or "tun" in name \
                or "docker" in name or "veth" in name \
                or "br-" in name or "vmbr" in name \
                or "vnet" in name or "kube" in name:
            continue
        avgrx2 += stats.bytes_recv
        avgtx2 += stats.bytes_sent

    netrx = int((avgrx2 - avgrx) / INTERVAL)
    nettx = int((avgtx2 - avgtx) / INTERVAL)

    return netrx, nettx


@app.route('/get_node_status')
def get_node_status():
    net_in, net_out = liuliang()
    uptime = get_uptime()
    load_1, load_5, load_15 = os.getloadavg()
    memory_total, memory_used = get_memory()
    swap_total, swap_used = get_swap()
    hdd_total, hdd_used = get_hdd()

    cpu = get_cpu()
    netrx, nettx = net_speed()

    array = {}
    array['online4'] = get_network(4)
    array['online6'] = get_network(6)

    array['uptime'] = display_time(uptime)
    array['load_1'] = load_1
    array['load_5'] = load_5
    array['load_15'] = load_15
    array['memory_total'] = str(round(memory_total / 1024 / 1024, 2)) + ' G'

    if memory_used >= 1024 * 1024:
        array['memory_used'] = str(round(memory_used / 1024 / 1024, 2)) + ' G'
    else:
        array['memory_used'] = str(round(memory_used / 1024, 2)) + ' M'

    if swap_total >= 1024 * 1024:
        array['swap_total'] = str(round(swap_total / 1024 / 1024, 2)) + ' G'
    else:
        array['swap_total'] = str(round(swap_total / 1024, 2)) + ' M'

    if swap_used >= 1024 * 1024:
        array['swap_used'] = str(round(swap_used / 1024 / 1024, 2)) + ' G'
    elif 1024 <= swap_used < 1024 * 1024:
        array['swap_used'] = str(round(swap_used / 1024, 2)) + ' M'
    else:
        array['swap_used'] = str(round(swap_used, 2)) + ' K'

    array['hdd_total'] = str(round(hdd_total / 1024, 2)) + ' G'
    array['hdd_used'] = str(round(hdd_used / 1024, 2)) + ' G'
    array['cpu'] = cpu

    array['network_rx'] = str(round(netrx / 1024 / 1024, 2)) + ' MB/S'

    array['network_tx'] = str(round(nettx / 1024 / 1024, 2)) + ' MB/S'

    if net_in >= 1024 * 1024 * 1024:
        array['network_in'] = str(round(net_in / 1024 / 1024 / 1024, 2)) + ' G'
    elif 1024 * 1024 <= net_in < 1024 * 1024 * 1024:
        array['network_in'] = str(round(net_in / 1024 / 1024, 2)) + ' M'
    else:
        array['network_in'] = str(round(net_in / 1024, 2)) + ' K'

    if net_out >= 1024 * 1024 * 1024:
        array['network_out'] = str(round(net_out / 1024 / 1024 / 1024, 2)) + ' G'
    elif 1024 * 1024 <= net_out < 1024 * 1024 * 1024:
        array['network_out'] = str(round(net_out / 1024 / 1024, 2)) + ' M'
    else:
        array['network_out'] = str(round(net_out / 1024, 2)) + ' K'

    array['tcp'], array['udp'], array['process'], array['thread'] = tupd()

    return jsonify(array)


@app.route("/ping")
def ping():
    return {'ping': 'pong'}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4171, debug=True)

    
    
