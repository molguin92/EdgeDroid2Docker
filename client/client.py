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
def run_client(
    host: str, port: int, neuroticism: float, trace: str, fade_distance: int, model: str
):
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
