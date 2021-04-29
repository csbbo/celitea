import asyncio
import socketio

sio = socketio.AsyncClient()


@sio.event
async def connect():
    print('connection established')


@sio.event
async def receive_and_emit_demo(data):
    # receive
    print(data)

    # emit
    await sio.emit('demo', {'response': 'my response'})


@sio.event
async def room1(data):
    print(data)


@sio.event
async def disconnect():
    print('disconnected from server')


async def main():
    await sio.connect('http://localhost:7070')
    await sio.wait()


if __name__ == '__main__':
    asyncio.run(main())
