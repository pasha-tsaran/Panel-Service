from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

# Natural Earth representative country points, superseded by the city coordinates below.
_COUNTRY_DATA: dict[str, list[float]] = json.loads(
    (Path(__file__).with_name("static") / "country-points.json").read_text(encoding="utf-8")
)
_COUNTRY_POINTS = {code: (lon, lat) for code, (lon, lat) in _COUNTRY_DATA.items()}
_CITIES: dict[str, tuple[tuple[float, float], tuple[str, ...], str]] = {
    "AM": ((44.5136, 40.1811), ("ереван", "yerevan"), "Ереван"),
    "NL": ((4.8897, 52.374), ("амстердам", "amsterdam"), "Амстердам"),
}


class NodeLocation(Protocol):
    @property
    def country_code(self) -> str: ...
    @property
    def city(self) -> str: ...
    @property
    def display_name(self) -> str: ...


@dataclass(frozen=True)
class MapPin:
    x: float
    y: float
    label: str
    short_label: str
    label_x: float
    anchor: str


def build_map_pins(
    nodes: Iterable[NodeLocation],
    *,
    primary: tuple[str, str] | None,
    has_netherlands_exit: bool,
) -> tuple[list[MapPin], int]:
    sites: dict[tuple[str, tuple[float, float]], tuple[str, str]] = {}
    countries: set[str] = set()

    def add(country: str, city: str, label: str) -> None:
        code = country.upper()
        countries.add(code)
        city_data = _CITIES.get(code)
        at_known_city = city_data is not None and city.casefold().strip() in city_data[1]
        point = city_data[0] if at_known_city and city_data else _COUNTRY_POINTS.get(code)
        if point is None:
            return
        short_label = city_data[2] if at_known_city and city_data else ""
        country_label = label if short_label else f"{label} · {code} (точка страны)"
        sites.setdefault((code, point), (country_label, short_label))

    if primary:
        country, city = primary
        if country.casefold().strip() in {"ам", "am", "армения", "armenia"}:
            add("AM", city, f"{country} · {city}")
    if has_netherlands_exit:
        add("NL", "Амстердам", "Нидерланды · Амстердам")
    for node in nodes:
        add(node.country_code, node.city, f"{node.display_name} · {node.city}")

    pins = []
    for (code, (lon, lat)), (label, short_label) in sites.items():
        x = round((lon + 180) * 8 / 3, 1)
        y = round((84 - lat) * 8 / 3, 1)
        if 0 < x < 960 and 0 < y < 380:
            pins.append(
                MapPin(
                    x,
                    y,
                    label,
                    short_label,
                    x - 11 if code == "NL" else x + 11,
                    "end" if code == "NL" else "start",
                )
            )
    return pins, len(countries)
