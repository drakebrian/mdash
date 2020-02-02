from app import app
from quart import Quart, render_template
import asyncio
import datetime
import nest_asyncio
import os.path
import pyatv
import sys
import yaml

nest_asyncio.apply()
LOOP = asyncio.get_event_loop()
CONFIG_FILE = 'app/config.yaml'

def load_config(config=CONFIG_FILE, section=None):
    if os.path.exists(config):
        with open(config, 'r') as stream:
            try:
                config = yaml.safe_load(stream)

                if section and config:
                    for k, v in config.items():
                        if k == section:
                            return v
                return config
            except yaml.YAMLError as ex:
                print(ex)

    return None

async def discover(loop, artwork=False, hosts=None):
    """ Discover Apple TVs on local network """
    if hosts:
        discovered = await pyatv.scan(loop, hosts=hosts, timeout=5)
    else:
        discovered = await pyatv.scan(loop, timeout=5)
    atvs = []

    for device in discovered:
        atv = {}
        atv['playing'] = False

        atv['name'] = device.name
        atv['address'] = device.address
        atv['identifier'] = device.identifier
        atv['services'] = device.services

        for service in device.services:
            if service.protocol.name == 'MRP':
                try:
                    connect_device = await pyatv.connect(device, loop)
                    now_playing = await connect_device.metadata.playing()
                    # 'album', 'artist', 'device_state', 'genre', 'hash', 'media_type', 'position', 'repeat', 'shuffle', 'title', 'total_time'
                    if 'idle' not in str(now_playing.device_state).lower():
                        atv['now_playing'] = now_playing.title
                        atv['playing'] = True

                        if 'paused' in str(now_playing.device_state).lower():
                            atv['playing'] = 'Paused'

                        if now_playing.total_time:
                            atv['playing_percent'] = (now_playing.position / now_playing.total_time) * 100

                            atv['current_position'] = str(now_playing.position / 60).split('.')[0] + ':' + str(now_playing.position % 60).zfill(2)
                            atv['time_remaining'] = str((now_playing.total_time - now_playing.position) / 60).split('.')[0] + ':' + str((now_playing.total_time - now_playing.position) % 60).zfill(2)
                        elif now_playing.position and not now_playing.total_time:
                            atv['playing_percent'] = 200

                        ## TO DO Artwork
                        if artwork:
                            artwork = await connect_device.metadata.artwork()
                            print(artwork)

                finally:
                    await connect_device.close()

        atvs.append(atv)

    return atvs

@app.route('/')
def dashboard():
    hosts_preload = load_config(config=CONFIG_FILE, section='apple_tvs')
    atvs = LOOP.run_until_complete(discover(LOOP, hosts=hosts_preload))
    atvs = sorted(atvs, key = lambda i: i['name'])

    context = {'atvs': atvs}
    return render_template('dashboard.html', title='Mdashboard', context=context)
