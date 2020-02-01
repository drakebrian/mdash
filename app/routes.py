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
        #try:
            #connect_device = await pyatv.connect(device, loop)
        atv = {}
        atv['name'] = device.name
        atv['address'] = device.address
        atv['playing'] = 'Nothing Playing' #await connect_device.metadata.playing()

        atvs.append(atv)
        #finally:
        #    connect_device.close()

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
