import inspect

import pytest

import gitair.core.session as session_module
from gitair.core.errors import (
    GitairError,
    InvalidGestureSourceConfiguration,
    InvalidGestureSourceInput,
)
from gitair.gestures.event import GestureType
from gitair.gestures.head_turn import HeadPoseSample, HeadTurnGestureSource
from gitair.gestures.mapper import GestureMapper


def test_head_turn_source_emits_head_right_when_yaw_crosses_right_threshold() -> None:
    source = HeadTurnGestureSource(
        turn_threshold_degrees=20.0,
        neutral_threshold_degrees=8.0,
        cooldown_samples=0,
    )

    neutral_event = source.observe_yaw(6.0)
    right_event = source.observe_yaw(21.0, confidence=0.82)

    assert neutral_event is None
    assert right_event is not None
    assert right_event.gesture_type == GestureType.HEAD_RIGHT
    assert right_event.confidence == 0.82


def test_head_turn_source_emits_head_left_when_yaw_crosses_left_threshold() -> None:
    source = HeadTurnGestureSource(
        turn_threshold_degrees=20.0,
        neutral_threshold_degrees=8.0,
        cooldown_samples=0,
    )

    left_event = source.observe_yaw(-22.0)

    assert left_event is not None
    assert left_event.gesture_type == GestureType.HEAD_LEFT


def test_neutral_head_turn_input_emits_no_gesture_event() -> None:
    source = HeadTurnGestureSource(
        turn_threshold_degrees=20.0,
        neutral_threshold_degrees=8.0,
        cooldown_samples=0,
    )

    assert source.observe_yaw(0.0) is None
    assert source.observe_yaw(7.9) is None
    assert source.observe_yaw(-7.9) is None


def test_head_turn_source_requires_neutral_return_before_repeating_event() -> None:
    source = HeadTurnGestureSource(
        turn_threshold_degrees=20.0,
        neutral_threshold_degrees=8.0,
        cooldown_samples=0,
    )

    first_event = source.observe_yaw(24.0)
    repeated_held_turn = source.observe_yaw(26.0)
    neutral_event = source.observe_yaw(0.0)
    second_event = source.observe_yaw(24.0)

    assert first_event is not None
    assert first_event.gesture_type == GestureType.HEAD_RIGHT
    assert repeated_held_turn is None
    assert neutral_event is None
    assert second_event is not None
    assert second_event.gesture_type == GestureType.HEAD_RIGHT


def test_head_turn_source_cooldown_blocks_events_after_neutral_return() -> None:
    source = HeadTurnGestureSource(
        turn_threshold_degrees=20.0,
        neutral_threshold_degrees=8.0,
        cooldown_samples=2,
    )

    first_event = source.observe_yaw(24.0)
    neutral_during_cooldown = source.observe_yaw(0.0)
    turn_during_cooldown = source.observe_yaw(24.0)
    turn_after_cooldown = source.observe_yaw(24.0)

    assert first_event is not None
    assert neutral_during_cooldown is None
    assert turn_during_cooldown is None
    assert turn_after_cooldown is not None
    assert turn_after_cooldown.gesture_type == GestureType.HEAD_RIGHT


def test_head_turn_source_yaw_sequence_yields_only_emitted_events() -> None:
    source = HeadTurnGestureSource(
        turn_threshold_degrees=20.0,
        neutral_threshold_degrees=8.0,
        cooldown_samples=0,
    )

    events = list(source.events_from_yaws([0.0, 21.0, 25.0, 0.0, -21.0]))

    assert [event.gesture_type for event in events] == [
        GestureType.HEAD_RIGHT,
        GestureType.HEAD_LEFT,
    ]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"turn_threshold_degrees": 0.0},
        {"turn_threshold_degrees": float("inf")},
        {"turn_threshold_degrees": 10.0, "neutral_threshold_degrees": 10.0},
        {"turn_threshold_degrees": 10.0, "neutral_threshold_degrees": -1.0},
        {"cooldown_samples": -1},
    ],
)
def test_head_turn_source_invalid_configuration_raises_custom_error(kwargs) -> None:
    with pytest.raises(InvalidGestureSourceConfiguration) as exc_info:
        HeadTurnGestureSource(**kwargs)

    assert isinstance(exc_info.value, GitairError)


@pytest.mark.parametrize(
    ("yaw_degrees", "confidence"),
    [
        (float("nan"), 1.0),
        (float("inf"), 1.0),
        (20.0, -0.1),
        (20.0, 1.1),
    ],
)
def test_head_turn_source_invalid_input_raises_custom_error(
    yaw_degrees: float,
    confidence: float,
) -> None:
    source = HeadTurnGestureSource()

    with pytest.raises(InvalidGestureSourceInput) as exc_info:
        source.observe_yaw(yaw_degrees, confidence=confidence)

    assert isinstance(exc_info.value, GitairError)


def test_head_turn_source_observe_sample_rejects_unvalidated_input() -> None:
    source = HeadTurnGestureSource()

    with pytest.raises(InvalidGestureSourceInput):
        source.observe_sample(object())  # type: ignore[arg-type]


def test_head_turn_source_events_map_to_existing_control_actions() -> None:
    source = HeadTurnGestureSource(
        turn_threshold_degrees=20.0,
        neutral_threshold_degrees=8.0,
        cooldown_samples=0,
    )
    mapper = GestureMapper()

    right_event = source.observe_sample(HeadPoseSample(yaw_degrees=22.0))
    assert right_event is not None
    source.observe_yaw(0.0)
    left_event = source.observe_yaw(-22.0)

    assert left_event is not None
    assert mapper.map_event(right_event).action.name == "BRING_COMPANION_IN"
    assert mapper.map_event(left_event).action.name == "SILENCE_COMPANION"


def test_session_core_stays_gesture_source_agnostic() -> None:
    session_source = inspect.getsource(session_module)

    assert "gitair.gestures" not in session_source
    assert "HeadTurnGestureSource" not in session_source
    assert "HeadPoseSample" not in session_source
