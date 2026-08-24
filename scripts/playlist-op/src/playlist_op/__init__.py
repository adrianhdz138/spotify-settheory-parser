import re
from collections.abc import Iterable
from itertools import batched
from urllib.parse import parse_qs, unquote, urlencode, urlparse

from core.tipos import (
    CanciónUri,
    PlaylistId,
    PlaylistTrackObject,
    RespuestaDetalles,
    RespuestaSP,
)
from services.spotify import spotify as sp
from utils.operaciones import resolver_operación


def arreglar_next_url(get_playlist_respuesta: RespuestaSP, campos_nuevo: bytes) -> None:
    # Corrección de error debido a que en el next url el endpoint cambia pero no los campos
    next_url_query_params_str = urlparse(get_playlist_respuesta["next"]).query
    next_url_stem = get_playlist_respuesta["next"].removesuffix(f"?{next_url_query_params_str}")
    next_url_query_params = parse_qs(next_url_query_params_str)
    next_url_query_params["fields"] = [campos_nuevo]
    get_playlist_respuesta["next"] = f"{next_url_stem}?{unquote(urlencode(next_url_query_params, doseq=True))}"


def obtener_items(spr: RespuestaSP, nombre_playlist: str):
    items = spr["items"]

    paged = False

    if spr["next"]:
        paged = True
        print(f"Coleccionando más canciones de {nombre_playlist}", end=".", flush=True)

    while spr["next"]:
        print(".", end="", flush=True)
        spr = sp.next(spr)
        items.extend(spr["items"])

    if paged:
        print()

    return items


def to_uri_set(items_list: Iterable[PlaylistTrackObject]):
    return {
        item["item"]["uri"]
        for item in items_list
        if not item["is_local"]
    }


def mapas_sets_y_nombres(pl_ids: Iterable[PlaylistId]) -> tuple[
        dict[PlaylistId, set[CanciónUri]],
        dict[PlaylistId, str]
    ]:
    mapa_sets: dict[PlaylistId, set[CanciónUri]] = {}
    mapa_nombres: dict[PlaylistId, str] = {}

    for pl_id in pl_ids:
        campos_interno = "next,items(is_local,item.uri)"

        campos = f"name,items({campos_interno})"

        print(f"Petición a playlist {pl_id}...")
        respuesta: RespuestaDetalles = sp.playlist(pl_id, fields=campos, market='MX')

        mapa_nombres[pl_id] = respuesta["name"]

        print(f"Playlist actual: {mapa_nombres[pl_id]}")

        respuesta_items = respuesta["items"]

        if campos in str(respuesta_items["next"]):
            arreglar_next_url(respuesta_items, bytes(campos_interno, encoding="UTF-8"))

        items = obtener_items(respuesta_items, mapa_nombres[pl_id])

        playlist_set = to_uri_set(items)

        mapa_sets[pl_id] = playlist_set

    return mapa_sets, mapa_nombres


def reemplazar_items(id_target: PlaylistId, set_target: set[CanciónUri], set_resultado: set[CanciónUri]):
    SPOTIFY_ITEMS_IO_LIMIT = 100

    if items_agregar := set_resultado - set_target:
        for items in batched(items_agregar, SPOTIFY_ITEMS_IO_LIMIT):
            print(f"Agregando {len(items)} canciones a playlist {id_target}...")
            sp.playlist_add_items(id_target, items)

    if items_eliminar := set_target - set_resultado:
        for items in batched(items_eliminar, SPOTIFY_ITEMS_IO_LIMIT):
            print(f"Limpiando {len(items)} canciones de playlist {id_target}...")
            sp.playlist_remove_all_occurrences_of_items(id_target, items)


def main():
    print("Escribe el id de la playlist igual a una operación de conjuntos con las playlists")
    print("Ejemplo: <playlist_id> = <operación>")

    expresión = input("> ")

    print()

    pl_id_target: PlaylistId
    pl_id_target, operación = expresión.split("=")
    pl_id_target = pl_id_target.strip()
    operación = operación.strip()

    print(f"Petición a playlist objetivo: {pl_id_target}...")

    respuesta_pl_target: RespuestaSP = sp.playlist_items(pl_id_target, fields="next,items(is_local,item.uri)", market='MX')

    pl_target_items = obtener_items(respuesta_pl_target, pl_id_target)

    pl_target_items_set = to_uri_set(pl_target_items)

    conjuntos: set[PlaylistId] = set(re.findall(r"[a-zA-Z0-9]{22}", operación))

    print("Coleccionando playlists...")

    mapa_sets, mapa_nombres = mapas_sets_y_nombres(conjuntos)

    print("Colección de playlists finalizada")

    pl_target_descripción = operación

    for pl_id, nombre in mapa_nombres.items():
        pl_target_descripción = pl_target_descripción.replace(pl_id, nombre)

    print(f"Calculando operación: {pl_target_descripción}...")

    resultado_operación = resolver_operación(operación, mapa_sets)

    reemplazar_items(pl_id_target, pl_target_items_set, resultado_operación)

    print(f"Escribiendo operación calculada en la descripción de la playlist objetivo: {pl_id_target}...")

    sp.playlist_change_details(pl_id_target, description=pl_target_descripción)

    print("Fin.")


if __name__ == '__main__':
    main()
