from datetime import timedelta

from kenai_vpn_admin.application.dashboard_metrics import is_fresh, latest_traffic_rate
from kenai_vpn_admin.infrastructure.models import ServerMetricModel, utc_now


def test_latest_rates_handle_zero_and_counter_reset() -> None:
    now = utc_now()
    previous = ServerMetricModel(
        captured_at=now - timedelta(minutes=6),
        received_bytes=0,
        transmitted_bytes=100_000,
    )
    current = ServerMetricModel(
        captured_at=now - timedelta(minutes=1),
        received_bytes=37_500_000,
        transmitted_bytes=0,
    )
    result = latest_traffic_rate([previous, current])
    assert result is not None
    assert result.receive_mbps == 1.0
    assert result.transmit_mbps is None


def test_latest_rates_expire_and_ignore_large_sampling_gaps() -> None:
    now = utc_now()
    stale = ServerMetricModel(captured_at=now - timedelta(minutes=20))
    fresh = ServerMetricModel(captured_at=now - timedelta(minutes=2))
    assert not is_fresh(stale)
    assert is_fresh(fresh)
    assert latest_traffic_rate([stale, fresh]) is None
    assert latest_traffic_rate([stale]) is None
