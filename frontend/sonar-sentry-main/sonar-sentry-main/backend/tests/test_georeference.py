from app.schemas.detection import BoundingBox
from app.services.georeference import georeference_bbox, parse_meters_per_pixel


class TestGeoreference:
    def test_parse_resolution(self):
        assert parse_meters_per_pixel("0.5 m/px") == 0.5
        assert parse_meters_per_pixel("0.1 m/px") == 0.1
        assert parse_meters_per_pixel("1 m/px") == 1.0

    def test_same_origin_different_boxes_differ(self):
        origin = (12.9716, 80.2436)
        first = georeference_bbox(
            *origin,
            BoundingBox(x=0, y=0, width=40, height=40),
            "0.5 m/px",
        )
        second = georeference_bbox(
            *origin,
            BoundingBox(x=400, y=300, width=80, height=60),
            "0.5 m/px",
        )
        assert first != second
        assert first[0] != second[0] or first[1] != second[1]

    def test_missing_bbox_stays_on_origin(self):
        lat, lng = georeference_bbox(12.9716, 80.2436, None, "0.5 m/px")
        assert lat == 12.9716
        assert lng == 80.2436
