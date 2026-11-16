from types import SimpleNamespace

from kenai_vpn_admin.web.geography import build_map_pins


def test_map_projects_known_cities_and_deduplicates_configured_nodes() -> None:
    armenia = SimpleNamespace(country_code="am", city="Yerevan", display_name="Ingress")
    pins, countries = build_map_pins(
        [armenia], primary=("Армения", "Ереван"), has_netherlands_exit=True
    )

    assert countries == 2
    assert [(pin.x, pin.y, pin.short_label) for pin in pins] == [
        (598.7, 116.9, "Ереван"),
        (493.0, 84.3, "Амстердам"),
    ]


def test_map_uses_country_points_for_other_cities_without_inventing_a_pin() -> None:
    nodes = [
        SimpleNamespace(country_code="DE", city="Düsseldorf", display_name="West"),
        SimpleNamespace(country_code="ZZ", city="Unknown", display_name="Other"),
    ]
    pins, countries = build_map_pins(nodes, primary=None, has_netherlands_exit=False)

    assert countries == 2
    assert len(pins) == 1
    assert pins[0].label == "West · Düsseldorf · DE (точка страны)"
    assert pins[0].short_label == ""
