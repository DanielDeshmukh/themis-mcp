"""Prometheus-compatible metrics for MCP tool calls."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field

logger = logging.getLogger("themis_mcp")


@dataclass
class Metric:
    """A single metric value."""

    name: str
    help_text: str
    value: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collect and format Prometheus-compatible metrics."""

    def __init__(self) -> None:
        self._counters: dict[str, float] = defaultdict(float)
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._gauges: dict[str, float] = {}
        self._start_time = time.monotonic()

    def inc_counter(self, name: str, labels: dict[str, str] | None = None) -> None:
        """Increment a counter."""
        key = self._make_key(name, labels)
        self._counters[key] += 1

    def observe_histogram(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """Record a histogram observation."""
        key = self._make_key(name, labels)
        self._histograms[key].append(value)

    def set_gauge(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """Set a gauge value."""
        key = self._make_key(name, labels)
        self._gauges[key] = value

    def _make_key(self, name: str, labels: dict[str, str] | None) -> str:
        """Create a unique key from name and labels."""
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def to_prometheus(self) -> str:
        """Format all metrics in Prometheus exposition format."""
        lines = []

        # Counters
        for key, value in sorted(self._counters.items()):
            lines.append(f"# TYPE {key.split('{')[0]} counter")
            lines.append(f"{key} {value}")

        # Gauges
        for key, value in sorted(self._gauges.items()):
            lines.append(f"# TYPE {key.split('{')[0]} gauge")
            lines.append(f"{key} {value}")

        # Histograms
        histogram_data: dict[str, list[float]] = defaultdict(list)
        for key, values in self._histograms.items():
            base_name = key.split("{")[0]
            histogram_data[base_name].extend(values)

        for base_name, values in sorted(histogram_data.items()):
            lines.append(f"# TYPE {base_name} histogram")
            sorted_vals = sorted(values)
            count = len(sorted_vals)
            total = sum(sorted_vals)
            lines.append(f"{base_name}_count {count}")
            lines.append(f"{base_name}_sum {total:.6f}")

            # Bucket boundaries
            buckets = [0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf")]
            cumulative = 0
            for bucket in buckets:
                cumulative += sum(1 for v in sorted_vals if v <= bucket)
                bucket_str = "+Inf" if bucket == float("inf") else str(bucket)
                lines.append(f'{base_name}_bucket{{le="{bucket_str}"}} {cumulative}')

        # Uptime
        uptime = time.monotonic() - self._start_time
        lines.append("# TYPE themis_uptime_seconds gauge")
        lines.append(f"themis_uptime_seconds {uptime:.2f}")

        return "\n".join(lines) + "\n"


# Global metrics collector
metrics = MetricsCollector()
