import socket

import click
from edgedroid import data as e_data
from edgedroid.execution_times import (
    EmpiricalExecutionTimeModel,
    ExecutionTimeModel,
    TheoreticalExecutionTimeModel,
    preprocess_data,
)
from edgedroid.frames import FrameModel
from edgedroid.model import EdgeDroidModel
from loguru import logger

from common import EdgeDroidFrame


@click.command()
@click.argument("host", type=str)
@click.argument("port", type=int)
@click.option("-n", "--neuroticism", type=click.FloatRange(0.0, 1.0), default=0.5)
@click.option("-t", "--trace", type=str, default="square00")
@click.option("-f", "--fade-distance", type=int, default=8)
@click.option(
    "-m",
    "--model",
    type=click.Choice(["empirical", "theoretical"], case_sensitive=False),
    default="theoretical",
)
@click.option("--frame-timeout-seconds", type=float, default=5.0)
def run_client(
    host: str,
    port: int,
    neuroticism: float,
    trace: str,
    fade_distance: int,
    model: str,
    frame_timeout_seconds: float,
):
    # TODO: make asynchronous?
    logger.info(
        f"Initializing EdgeDroid model with neuroticism {neuroticism:0.2f} and fade "
        f"distance {fade_distance:d} steps."
    )
    logger.info(f"Model type: {model}")
    logger.info(f"Trace: {trace}")

    # should be able to use a single thread for everything

    # first thing first, prepare data
    data = preprocess_data(*e_data.load_default_exec_time_data())
    frameset = e_data.load_default_trace(trace)

    # prepare models
    if model == "theoretical":
        timing_model: ExecutionTimeModel = TheoreticalExecutionTimeModel(
            data=data, neuroticism=neuroticism, transition_fade_distance=fade_distance
        )
    else:
        timing_model: ExecutionTimeModel = EmpiricalExecutionTimeModel(
            data=data, neuroticism=neuroticism, transition_fade_distance=fade_distance
        )

    frame_model = FrameModel(e_data.load_default_frame_probabilities())

    edgedroid_model = EdgeDroidModel(
        frame_trace=frameset, frame_model=frame_model, timing_model=timing_model
    )

    # "connect" to remote
    # this is of course just for convenience, to skip adding an address to every
    # send() call, as there are no "connections" in udp.
    logger.info(f"Connecting to remote server at {host}:{port}/udp")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect((host, port))

        for model_frame in edgedroid_model.play():
            # package and send the frame
            logger.debug(
                f"Sending frame {model_frame.seq} (frame tag: {model_frame.frame_tag})."
            )
            payload = EdgeDroidFrame(model_frame.seq, model_frame.frame_data).pack()
            sock.sendall(payload)
