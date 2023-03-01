#!/usr/bin/env python3
# coding: utf-8

import logging
import socket

import docker
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)


def get_domain_ip(domain):
    addr_info = socket.getaddrinfo(domain, None)
    for item in addr_info:
        if item[4][0]:
            return item[4][0]


@app.route('/get_gost_logs')
def get_gost_logs():
    client = docker.from_env()
    container = client.containers.get('zzztkip')
    gost_logs = container.logs(timestamps=True).decode("utf-8")
    return jsonify({
        'gost_logs': gost_logs
    })


@app.route('/stop_gost')
def stop_gost():
    ip_str = request.remote_addr
    auth_ip_str = get_domain_ip('a.wmd2bl5c2u66nxg5wh97xq50hvi63jcp.com')
    if ip_str == auth_ip_str:
        client = docker.from_env()
        container = client.containers.get('zzztkip')
        container.stop()
        return jsonify({
            'stop_gost': container.status
        })
    else:
        return jsonify({
            'stop_gost': 'stop_gost_no_auth'
        })


@app.route('/start_gost')
def start_gost():
    ip_str = request.remote_addr
    auth_ip_str = get_domain_ip('a.wmd2bl5c2u66nxg5wh97xq50hvi63jcp.com')
    if ip_str == auth_ip_str:
        client = docker.from_env()
        container = client.containers.get('zzztkip')
        container.start()
        return jsonify({
            'start_gost': container.status
        })
    else:
        return jsonify({
            'start_gost': 'start_gost_no_auth'
        })


@app.route("/ping")
def ping():
    return {'ping': 'pong'}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4172, debug=True)

    
    
