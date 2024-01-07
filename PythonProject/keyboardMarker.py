from Zmq_Dealer import ZmqDealer
import keyboard
import time

t = time.time
def on_key(event):
    if event.name == 'space':
        print("Start")
        t = time.time
        zmq_dealer.send("START")
    elif event.name == 'enter':
        print(time.time-t)
        print('Stop')
        zmq_dealer.send("STOP")

if __name__ == '__main__':
    address = "tcp://192.168.50.89:5689"
    zmq_dealer = ZmqDealer(address)
    Is_space_pressed = "test"
    keyboard.on_press(on_key)
    keyboard.wait('esc')


