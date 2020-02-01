from app import app
from quart import Quart, render_template
import asyncio
import pyatv
import sys
import nest_asyncio

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
                    if 'playing' in str(now_playing.device_state).lower():
                        atv['now_playing'] = now_playing.title
                        atv['playing'] = True

                        if now_playing.total_time:
                            atv['playing_percent'] = (now_playing.position / now_playing.total_time) * 100
                        elif now_playing.position and not now_playing.total_time:
                            atv['playing_percent'] = 200

                finally:
                    await connect_device.close()

        atvs.append(atv)

    return atvs

async def print_what_is_playing(loop):
    """Find a device and print what is playing."""
    print('Discovering devices on network...')
    atvs = await pyatv.scan(loop, timeout=5)

    if not atvs:
        print('No device found', file=sys.stderr)
        return 

    print('Connecting to {0}'.format(atvs[0].address))
    atv = await pyatv.connect(atvs[0], loop)

    try:
        playing = await atv.metadata.playing()
        print('Currently playing:')
        print(playing)
    finally:
        # Do not forget to close
        await atv.close()


@app.route('/')
def dashboard():
    atvs = LOOP.run_until_complete(discover(LOOP))

    context = {'atvs': atvs}
    return render_template('dashboard.html', title='Dashboard', context=context)
