from dataclasses import dataclass
from datetime import timedelta

from kenai_vpn_admin.infrastructure.models import ServerMetricModel, naive_utc, utc_now

MAX_SAMPLE_AGE = timedelta(minutes=15)


@dataclass(frozen=True)
class TrafficRate:
    receive_mbps: float | None
    transmit_mbps: float | None


def _rate(previous: int | None, current: int | None, seconds: float) -> float | None:
    if previous is None or current is None or current < previous:
        return None
    return (current - previous) * 8 / seconds / 1_000_000


def latest_traffic_rate(samples: list[ServerMetricModel]) -> TrafficRate | None:
    if len(samples) < 2:
        return None
    previous, current = samples[-2:]
    observed = naive_utc(current.captured_at) - naive_utc(previous.captured_at)
    if not timedelta(0) < observed <= MAX_SAMPLE_AGE or not is_fresh(current):
        return None
    seconds = observed.total_seconds()
    return TrafficRate(
        _rate(previous.received_bytes, current.received_bytes, seconds),
        _rate(previous.transmitted_bytes, current.transmitted_bytes, seconds),
    )


def is_fresh(sample: ServerMetricModel) -> bool:
    age = utc_now() - naive_utc(sample.captured_at)
    return timedelta(0) <= age <= MAX_SAMPLE_AGE
