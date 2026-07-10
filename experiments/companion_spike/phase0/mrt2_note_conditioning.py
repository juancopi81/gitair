"""Pure conditioning plan for the throwaway MRT2 Phase 0 experiment."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

FRAMES_PER_SECOND = 25

# These voicings preserve the fixture's descending bass as the lowest note:
# C3 -> B2 -> Bb2 -> A2 -> G2. Upper notes stay close so the experiment tests
# harmony following without asking MRT2 to interpret chord symbols itself.
CHORD_VOICINGS: dict[str, dict[str, int]] = {
    "C": {"C3": 48, "C4": 60, "E4": 64, "G4": 67},
    "Cmaj7/B": {"B2": 47, "C4": 60, "E4": 64, "G4": 67},
    "C7/Bb": {"Bb2": 46, "C4": 60, "E4": 64, "G4": 67},
    "Am7": {"A2": 45, "C4": 60, "E4": 64, "G4": 67},
    "G": {"G2": 43, "B3": 59, "D4": 62, "G4": 67},
    "Gadd4": {"G2": 43, "B3": 59, "C4": 60, "D4": 62, "G4": 67},
}

ConditioningMode = Literal["strict", "creative"]


@dataclass(frozen=True)
class BarConditioning:
    bar_number: int
    chord: str
    note_names: tuple[str, ...]
    midi_pitches: tuple[int, ...]
    start_frame: int
    frames: int


def load_fixture(path: Path) -> dict[str, Any]:
    fixture = json.loads(path.read_text())
    if fixture["meter"] != {"beats": 4, "beat_type": 4}:
        raise ValueError("This Phase 0 prototype expects the canonical loop in 4/4.")
    if fixture["bar_count"] != len(fixture["chords_per_bar"]):
        raise ValueError("Fixture bar_count does not match chords_per_bar.")
    unknown_chords = set(fixture["chords_per_bar"]) - CHORD_VOICINGS.keys()
    if unknown_chords:
        raise ValueError(f"Missing MIDI voicings for: {sorted(unknown_chords)}")
    return fixture


def build_bar_plan(fixture: dict[str, Any]) -> list[BarConditioning]:
    seconds_per_bar = fixture["meter"]["beats"] * 60 / fixture["tempo_bpm"]
    plan = []
    for index, chord in enumerate(fixture["chords_per_bar"]):
        start_frame = round(index * seconds_per_bar * FRAMES_PER_SECOND)
        end_frame = round((index + 1) * seconds_per_bar * FRAMES_PER_SECOND)
        voicing = CHORD_VOICINGS[chord]
        plan.append(
            BarConditioning(
                bar_number=index + 1,
                chord=chord,
                note_names=tuple(voicing),
                midi_pitches=tuple(voicing.values()),
                start_frame=start_frame,
                frames=end_frame - start_frame,
            )
        )
    return plan


def build_notes_vector(midi_pitches: tuple[int, ...], mode: ConditioningMode) -> list[int]:
    # MRT2 note states: -1 masked, 0 off, 3 active with onset/continuation freedom.
    background_state = 0 if mode == "strict" else -1
    notes = [background_state] * 128
    for pitch in midi_pitches:
        notes[pitch] = 3
    return notes
