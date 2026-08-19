from typing import TypedDict

type CanciónUri = str
type PlaylistId = str
type Url = str


class TrackObject(TypedDict):
    uri: CanciónUri


class PlaylistTrackObject(TypedDict):
    is_local: bool
    item: TrackObject


class RespuestaSP(TypedDict):
    next: Url | None
    items: list[PlaylistTrackObject]


class RespuestaDetalles(TypedDict):
    name: str
    items: RespuestaSP
