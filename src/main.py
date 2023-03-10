#!/usr/bin/env python3

"""
Inspired by pystemd example - start_transient_unit.py
https://github.com/facebookincubator/pystemd/blob/fb124d2f1196af0dcb69fa8fc9bb9ca8cbf6bf4c/examples/start_transient_unit.py
"""

import random
import shlex
import time
import argparse

from pystemd.dbuslib import DBus
from pystemd.systemd1 import Manager, Unit


def start_transient_unit(cmd="/bin/sleep 5"):
    a_cmd = [c.encode() for c in shlex.split(cmd)]
    random_unit_name = f"myservice.{random.randint(0, 100)}.{time.time()}.service"
    unit = {
        b"Description": b"Example of transient unit",
        b"ExecStart": [(a_cmd[0], a_cmd, False)],
        b"RemainAfterExit": True,
    }

    # if we need interactive prompts for passwords, we can create our own DBus object.
    # if we dont need interactive, we would just do `with Manager() as manager:`.
    with DBus(interactive=True) as bus, Manager(bus=bus) as manager:
        manager.Manager.StartTransientUnit(random_unit_name, b"fail", unit)

        with Unit(random_unit_name, bus=bus) as unit:
            while True:
                print(
                    "service `{cmd}` (name={random_unit_name}) has MainPID "
                    "{unit.Service.MainPID}".format(**locals())
                )
                if unit.Service.MainPID == 0:
                    print(
                        "service finished with "
                        "{unit.Service.ExecMainStatus}/{unit.Service.Result} "
                        "will stop it and then... bye".format(**locals())
                    )
                    unit.Unit.Stop(b"replace")
                    break
                print("service still running, sleeping by 5 seconds")
                time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create dummy process and assign it to systemd scope. \
                     Process runs `/bin/sleep <n>`"
    )

    parser.add_argument(
        "--sleep",
        type=int,
        default=0,
        nargs=1,
        help="number of seconds for /bin/sleep",
    )

    ARGS = parser.parse_args()
    SLEEP_CMD = f"/bin/sleep {ARGS.sleep[0]}"

    start_transient_unit(SLEEP_CMD)
