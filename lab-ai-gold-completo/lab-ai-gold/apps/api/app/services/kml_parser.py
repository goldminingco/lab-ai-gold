"""
Parser server-side de KML e KMZ.
Nunca expõe lógica de parsing ao browser — Regra de Ouro #4.
Retorna GeoJSON padronizado + metadados de área.
"""
from __future__ import annotations

import io
import math
import zipfile
from pathlib import Path
from typing import Any

from lxml import etree
from shapely.geometry import MultiPolygon, Polygon, mapping, shape
from shapely.ops import unary_union

KMZ_MIME = "application/vnd.google-earth.kmz"
KML_MIME = "application/vnd.google-earth.kml+xml"

# ─── Namespace KML ────────────────────────────────────────────────────────────
NS = {"kml": "http://www.opengis.net/kml/2.2"}
NS_ALT = {"kml": ""}  # alguns KMLs sem namespace


def parse_kml_bytes(content: bytes, filename: str) -> dict[str, Any]:
    """
    Faz parse de KML ou KMZ e retorna dict com:
      geojson, area_ha, centroid_lat, centroid_lng, bounds_json
    Lança ValueError com mensagem amigável em caso de falha.
    """
    suffix = Path(filename).suffix.lower()
    if suffix == ".kmz":
        content = _extract_kml_from_kmz(content)

    try:
        tree = etree.fromstring(content)
    except etree.XMLSyntaxError as e:
        raise ValueError(f"Arquivo KML inválido: {e}") from e

    polygons = _extract_polygons(tree)
    if not polygons:
        raise ValueError("Nenhum polígono encontrado no arquivo KML/KMZ")

    union = unary_union(polygons)
    geojson = _to_geojson(union)
    centroid = union.centroid
    bounds = union.bounds   # (minx, miny, maxx, maxy)
    area_ha = _area_wgs84_ha(union)

    return {
        "geojson":     geojson,
        "area_ha":     round(area_ha, 4),
        "centroid_lat": round(centroid.y, 6),
        "centroid_lng": round(centroid.x, 6),
        "bounds_json": {
            "min_lng": bounds[0], "min_lat": bounds[1],
            "max_lng": bounds[2], "max_lat": bounds[3],
        },
    }


# ─── Internos ─────────────────────────────────────────────────────────────────
def _extract_kml_from_kmz(content: bytes) -> bytes:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            kml_files = [n for n in z.namelist() if n.lower().endswith(".kml")]
            if not kml_files:
                raise ValueError("Nenhum arquivo .kml encontrado dentro do KMZ")
            # Prefere doc.kml na raiz
            target = next((f for f in kml_files if f.lower() in ("doc.kml", "document.kml")), kml_files[0])
            return z.read(target)
    except zipfile.BadZipFile as e:
        raise ValueError("Arquivo KMZ corrompido ou inválido") from e


def _extract_polygons(tree: etree._Element) -> list[Polygon]:
    """Extrai todos os Polygon do KML, com ou sem namespace."""
    polygons: list[Polygon] = []

    # Tenta com namespace padrão e sem namespace
    for ns_map in [NS, {}]:
        tag_polygon = "kml:Polygon" if ns_map else "Polygon"
        tag_outer   = "kml:outerBoundaryIs/kml:LinearRing/kml:coordinates" if ns_map else "outerBoundaryIs/LinearRing/coordinates"
        tag_inner   = "kml:innerBoundaryIs/kml:LinearRing/kml:coordinates" if ns_map else "innerBoundaryIs/LinearRing/coordinates"

        for poly_el in tree.iter(
            f"{{{NS['kml']}}}Polygon" if ns_map else "Polygon"
        ):
            outer_el = poly_el.find(
                f".//{{{NS['kml']}}}outerBoundaryIs/{{{NS['kml']}}}LinearRing/{{{NS['kml']}}}coordinates"
                if ns_map else ".//outerBoundaryIs/LinearRing/coordinates"
            )
            if outer_el is None or not outer_el.text:
                continue
            outer_coords = _parse_coords(outer_el.text)
            if len(outer_coords) < 4:
                continue

            inner_rings = []
            for inner_el in poly_el.findall(
                f".//{{{NS['kml']}}}innerBoundaryIs/{{{NS['kml']}}}LinearRing/{{{NS['kml']}}}coordinates"
                if ns_map else ".//innerBoundaryIs/LinearRing/coordinates"
            ):
                if inner_el.text:
                    ic = _parse_coords(inner_el.text)
                    if len(ic) >= 4:
                        inner_rings.append(ic)

            try:
                polygons.append(Polygon(outer_coords, inner_rings))
            except Exception:
                continue

        if polygons:
            break

    return polygons


def _parse_coords(text: str) -> list[tuple[float, float]]:
    coords = []
    for token in text.strip().split():
        parts = token.split(",")
        if len(parts) >= 2:
            try:
                coords.append((float(parts[0]), float(parts[1])))
            except ValueError:
                continue
    return coords


def _to_geojson(geom) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": mapping(geom), "properties": {}}
        ],
    }


def _area_wgs84_ha(geom) -> float:
    """Estimativa de área em hectares via projeção equiretangular simplificada."""
    lat = geom.centroid.y
    lat_rad = math.radians(lat)
    m_per_deg_lat = 111_132.954 - 559.822 * math.cos(2 * lat_rad) + 1.175 * math.cos(4 * lat_rad)
    m_per_deg_lng = 111_412.84 * math.cos(lat_rad) - 93.5 * math.cos(3 * lat_rad)

    # Escala aproximada usando bounds
    bounds = geom.bounds
    width_m  = abs(bounds[2] - bounds[0]) * m_per_deg_lng
    height_m = abs(bounds[3] - bounds[1]) * m_per_deg_lat
    # Usa área real do polígono em graus * fator de escala
    area_deg2 = geom.area
    area_m2   = area_deg2 * m_per_deg_lat * m_per_deg_lng
    return area_m2 / 10_000
