from __future__ import annotations

import math
import re

from app.schemas.detection import BoundingBox, DetectionItem

METERS_PER_DEGREE_LAT = 111_320.0
_DEFAULT_METERS_PER_PIXEL = 0.5


def parse_meters_per_pixel(resolution: str | None) -> float:
    if not resolution:
        return _DEFAULT_METERS_PER_PIXEL
    match = re.search(r"([0-9]*\.?[0-9]+)", str(resolution))
    if not match:
        return _DEFAULT_METERS_PER_PIXEL
    value = float(match.group(1))
    return value if value > 0 else _DEFAULT_METERS_PER_PIXEL


def georeference_offset(
    origin_lat: float,
    origin_lng: float,
    east_m: float,
    north_m: float,
) -> tuple[float, float]:
    lat = origin_lat + north_m / METERS_PER_DEGREE_LAT
    cos_lat = math.cos(math.radians(origin_lat))
    meters_per_deg_lng = METERS_PER_DEGREE_LAT * max(abs(cos_lat), 1e-6)
    lng = origin_lng + east_m / meters_per_deg_lng
    return round(lat, 7), round(lng, 7)


def georeference_bbox(
    origin_lat: float | None,
    origin_lng: float | None,
    bbox: BoundingBox | None,
    resolution: str | None,
) -> tuple[float | None, float | None]:
    """Map a detection box to WGS84 using the scan origin as image (0, 0).

    Pixel +x is east, pixel +y (down the image) is south. The scan lat/lng is
    the vessel/georeference point, not a shared pin for every object.
    """
    if origin_lat is None or origin_lng is None:
        return None, None
    if bbox is None:
        return round(float(origin_lat), 7), round(float(origin_lng), 7)

    meters_per_px = parse_meters_per_pixel(resolution)
    center_x = bbox.x + bbox.width / 2.0
    center_y = bbox.y + bbox.height / 2.0
    east_m = center_x * meters_per_px
    north_m = -center_y * meters_per_px
    return georeference_offset(float(origin_lat), float(origin_lng), east_m, north_m)


def with_detection_coordinates(
    item: DetectionItem,
    origin_lat: float | None,
    origin_lng: float | None,
    resolution: str | None,
) -> DetectionItem:
    lat, lng = georeference_bbox(origin_lat, origin_lng, item.bbox, resolution)
    return item.model_copy(update={"latitude": lat, "longitude": lng})
