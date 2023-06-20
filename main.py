#!/usr/bin/env python3

import sys
import pprint
import serial
import time
import os
from flippydot import *
from datetime import datetime, timedelta
from pytz import timezone


import numpy as np
import requests
import typer
from typing import Optional
from typing_extensions import Annotated


SERIAL_PORT = "/dev/cu.usbserial-AK05BHWP"
GITHUB_API_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_USERNAME = 'golanlevin'

if GITHUB_API_TOKEN is None:
    raise ValueError("Please Set the GITHUB_TOKEN environment variable.")


def github_junk(username: object = 'cheeriocheng', from_time: object = "2022-01-01T00:00:00Z",
                to_time: object = "2023-01-01T00:00:00Z") -> object:
    headers = {"Authorization": "Bearer " + GITHUB_API_TOKEN}
    query = f"""
query {{ 
  user(login: "{username}") {{
    email
    createdAt
    contributionsCollection(from: "{from_time}", to: "{to_time}") {{
      contributionCalendar {{
        totalContributions
        weeks {{
          contributionDays {{
            weekday
            date 
            contributionCount 
            color
          }}
        }}
        months {{
          name
            year
            firstDay 
          totalWeeks 

        }}
      }}
    }}
  }}

}}
    """
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def github_other_junk(username="cheeriocheng"):
    parsed = dict()

    local_tz = timezone('America/Los_Angeles')
    now = local_tz.localize(datetime.now()).astimezone(timezone('UTC'))
    end = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    beginning = (now - timedelta(weeks=53)).strftime("%Y-%m-%dT%H:%M:%SZ")#max allowed trace back is one year
    print(f"FROM {beginning} TO {end} for {username}")
    response = github_junk(username=username, from_time=beginning, to_time=end)

    contributionCalendar = response["data"]["user"]["contributionsCollection"]["contributionCalendar"]

    weeks = contributionCalendar["weeks"]
    for week in weeks:
        contributionDays = week["contributionDays"]
        for day in contributionDays:
            weekkday = day["weekday"]
            date = datetime.fromisoformat(day["date"])
            contributionCount = int(day["contributionCount"])

            parsed[date] = contributionCount
            # if contributionCount > 0:
            #     pprint.pprint(day)

    return parsed


def clear_stage(panel, ser):
    frame_delay = 0.4
    # Set whole panel to white
    frame = np.ones((panel.get_total_height(), panel.get_total_width()), dtype=np.uint8)
    serial_data = panel.apply_frame(frame)
    ser.write(serial_data)
    time.sleep(frame_delay)

    # Set whole panel to black
    frame = np.zeros((panel.get_total_height(), panel.get_total_width()), dtype=np.uint8)
    serial_data = panel.apply_frame(frame)
    ser.write(serial_data)
    time.sleep(frame_delay)


def main(name: Annotated[Optional[str], typer.Argument()] = None):
    global GITHUB_USERNAME
    if name is not None:
        GITHUB_USERNAME = name

    result = github_other_junk(GITHUB_USERNAME)
    # print(result)
    # sys.exit(0)

    # Setup our serial port connection
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=57600,
        timeout=1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    # Configure our FlipDot panel
    panel = flippydot.Panel([
        [1, 2]
    ], 28, 7, module_rotation=0, screen_preview=False)
    # print('total_height: ' + str(panel.get_total_height()))
    # print('total_width: ' + str(panel.get_total_width()))

    frame = np.zeros((panel.get_total_height(), panel.get_total_width()), dtype=np.uint8)
    idx = 0
    print(f"Frame shape {frame.shape}")
    column = panel.get_total_width()
    clear_stage(panel, ser)

    for date, contributions in sorted(result.items()):
        x = int(idx / 7)  # TODO fix the lastest week
        y = int((idx + 1) % 7)  # change from monday as day 0 to sunday as day 0
        if x >= column:
            break
        frame[y, x] = contributions
        idx += 1

    serial_data = panel.apply_frame(frame)
    ser.write(serial_data)

    # while True:
    time.sleep(2)


if __name__ == "__main__":
    typer.run(main)
