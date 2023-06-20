#!/usr/bin/env python3

import typer
from typing import Optional
from typing_extensions import Annotated

import sys
import cv2
from flippydot import *
import numpy as np
import time, serial


def main(name: Annotated[Optional[str], typer.Argument()] = None):
    print(f" {name}")

    # Setup our serial port connection
    ser = serial.Serial(
        # ls /dev/cu*
        port='/dev/cu.usbserial-AK05BHWP',
        baudrate=57600,
        timeout=1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    # Configure our FlipDot panel
    panel = flippydot.Panel([
        [1,2]
        # [3],
        # [4],
    ], 28, 7, module_rotation=0, screen_preview= True )

    frame_delay = 1.0


    # # Turn entire screen from black to white 10 times
    # for i in range(1):
    #     # Set whole panel to white
    #     frame = np.ones((panel.get_total_height(), panel.get_total_width()), dtype=np.uint8)
    #     serial_data = panel.apply_frame(frame)
    #     ser.write(serial_data)
    #     print(frame.shape)
    #     time.sleep(frame_delay)
    #
    #     # Set whole panel to black
    #     frame = np.zeros((panel.get_total_height(), panel.get_total_width()), dtype=np.uint8)
    #     serial_data = panel.apply_frame(frame)
    #     ser.write(serial_data)
    #     time.sleep(frame_delay)

     # Move a vertical line down the panel
    for i in range(panel.get_total_height()):
        frame = np.zeros((panel.get_total_height(), panel.get_total_width()), dtype=np.uint8)
        frame[i,:] = 1
        serial_data = panel.apply_frame(frame)
        ser.write(serial_data)
        time.sleep(frame_delay)

if __name__ == "__main__":
    typer.run(main)
