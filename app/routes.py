from app import app
from quart import Quart, render_template
import asyncio
import datetime
import nest_asyncio
import pyatv
import sys

nest_asyncio.apply()
LOOP = asyncio.get_event_loop()

async def discover(loop):
    """ Discover Apple TVs on local network """
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

                finally:
                    await connect_device.close()

        atvs.append(atv)

    return atvs

@app.route('/')
def dashboard():
    atvs = LOOP.run_until_complete(discover(LOOP))
    atvs = sorted(atvs, key = lambda i: i['name'])

    context = {'atvs': atvs}
    return render_template('dashboard.html', title='Dashboard', context=context)
