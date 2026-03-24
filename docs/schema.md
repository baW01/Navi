# Canonical schema

## Junction

- `id`
- `lat`
- `lon`
- `connected_segment_ids`

## RoadSegment

- `id`
- `from_junction_id`
- `to_junction_id`
- `geometry`
- `name`
- `ref`
- `road_class`
- `oneway`
- `maxspeed`
- `lanes`
- `surface`
- `access_car`
- `toll`
- `bridge`
- `tunnel`

## TurnRestriction

- `id`
- `from_segment_id`
- `via_junction_id` lub `via_segment_id`
- `to_segment_id`
- `restriction_type`

## Address

- `id`
- `house_number`
- `street`
- `city`
- `postcode`
- `country`
- `lat`
- `lon`

## POI

- `id`
- `name`
- `category`
- `subcategory`
- `lat`
- `lon`

## Metadata

- `source_data`
- `imported_at`
- `bounding_box`
- `region`
- `pipeline_version`
