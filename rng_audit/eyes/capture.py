"""Visual & Frame Capture Utilities for PILL RED Eyes.

Provides motion stabilization and reel settle detection to capture spin outcomes
passively from video frames or screen crops.
"""

import time
from typing import Callable, Dict, List, Optional, Tuple
import numpy as np


class SpinSettleDetector:
    """Detects spin start and completion by tracking frame-to-frame pixel motion energy."""

    def __init__(
        self,
        motion_threshold: float = 15.0,
        settle_duration_sec: float = 0.5,
        min_spin_duration_sec: float = 1.0
    ):
        self.motion_threshold = motion_threshold
        self.settle_duration_sec = settle_duration_sec
        self.min_spin_duration_sec = min_spin_duration_sec

        self.is_spinning = False
        self.spin_start_time = 0.0
        self.last_motion_time = 0.0
        self.prev_frame: Optional[np.ndarray] = None

    def process_frame(self, frame: np.ndarray, current_time: Optional[float] = None) -> Tuple[str, float]:
        """Processes a new frame (grayscale or RGB array) and returns the state event.

        Returns:
            (event_type, motion_energy)
            event_type: "IDLE", "SPIN_STARTED", "SPINNING", "SPIN_SETTLED"
        """
        now = current_time or time.time()
        
        # Convert to 2D grayscale if RGB
        if frame.ndim == 3:
            gray = np.mean(frame, axis=2)
        else:
            gray = frame.astype(np.float64)

        if self.prev_frame is None or self.prev_frame.shape != gray.shape:
            self.prev_frame = gray
            return "IDLE", 0.0

        # Compute mean absolute pixel difference (motion energy)
        motion_energy = float(np.mean(np.abs(gray - self.prev_frame)))
        self.prev_frame = gray

        event = "IDLE"

        if not self.is_spinning:
            if motion_energy > self.motion_threshold:
                self.is_spinning = True
                self.spin_start_time = now
                self.last_motion_time = now
                event = "SPIN_STARTED"
        else:
            if motion_energy > self.motion_threshold:
                self.last_motion_time = now
                event = "SPINNING"
            else:
                # Motion is below threshold
                spin_duration = now - self.spin_start_time
                settle_duration = now - self.last_motion_time

                if spin_duration >= self.min_spin_duration_sec and settle_duration >= self.settle_duration_sec:
                    self.is_spinning = False
                    event = "SPIN_SETTLED"
                else:
                    event = "SPINNING"

        return event, motion_energy
