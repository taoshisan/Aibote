import os
import signal
import threading
from multiprocessing.context import SpawnProcess
from typing import Callable

import click

from loguru import logger


def multiprocess(workers_num: int, create_process: Callable[[], SpawnProcess]) -> None:
    should_exit = threading.Event()

    logger.info(
        "Started parent process [{}]".format(
            click.style(str(os.getpid()), fg="cyan", bold=True)
        )
    )

    for sig in (
            signal.SIGINT,  # Sent by Ctrl+C.
            signal.SIGTERM  # Sent by `kill <pid>`. Not sent on Windows.
            if os.name != "nt"
            else signal.SIGBREAK,  # Sent by `Ctrl+Break` on Windows.
    ):
        signal.signal(sig, lambda sig, frame: should_exit.set())

    processes: list[SpawnProcess] = []

    def create_child() -> SpawnProcess:
        process = create_process()
        processes.append(process)
        process.start()
        logger.info(
            "Started child process [{}]".format(
                click.style(str(process.pid), fg="cyan", bold=True)
            )
        )
        return process

    for _ in range(workers_num):
        create_child()

    while not should_exit.wait(0.5):
        for idx, process in enumerate(tuple(processes)):
            if process.is_alive():
                continue

            logger.info(
                "Child process [{}] died unexpectedly".format(
                    click.style(str(process.pid), fg="cyan", bold=True)
                )
            )
            del processes[idx]
            create_child()

    for process in processes:
        if process.pid is None:
            continue

        if os.name == "nt":
            # Windows doesn't support SIGTERM.
            os.kill(process.pid, signal.CTRL_BREAK_EVENT)
        else:
            os.kill(process.pid, signal.SIGTERM)

    for process in processes:
        logger.info(
            "Waiting for child process [{}] to terminate".format(
                click.style(str(process.pid), fg="cyan", bold=True)
            )
        )
        process.join()

    logger.info(
        "Stopped parent process [{}]".format(
            click.style(str(os.getpid()), fg="cyan", bold=True)
        )
    )
