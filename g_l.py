#!/usr/bin/env python3
# coding: utf-8

import logging
import socket

import docker
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)



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
    client = docker.from_env()
    container = client.containers.get('zzztkip')
    container.stop()
    return jsonify({
        'stop_gost': container.status
    })


@app.route('/start_gost')
def start_gost():
    client = docker.from_env()
    container = client.containers.get('zzztkip')
    container.start()
    return jsonify({
        'start_gost': container.status
    })


@app.route("/ping")
def ping():
    return {'ping': 'pong'}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4172, debug=True)

    
    
