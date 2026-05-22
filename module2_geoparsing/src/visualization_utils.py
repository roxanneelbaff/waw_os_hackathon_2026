from __future__ import annotations

from pathlib import Path

import folium
import pandas as pd


def validate_coordinates(df: pd.DataFrame, lat_col: str = "lat", lon_col: str = "lon") -> pd.DataFrame:
    if df is None or df.empty or lat_col not in df.columns or lon_col not in df.columns:
        return pd.DataFrame(columns=list(df.columns) if df is not None else [lat_col, lon_col])

    out = df.copy()
    out[lat_col] = pd.to_numeric(out[lat_col], errors="coerce")
    out[lon_col] = pd.to_numeric(out[lon_col], errors="coerce")
    return out[out[lat_col].between(-90, 90) & out[lon_col].between(-180, 180)].reset_index(drop=True)


def create_location_map(
    df: pd.DataFrame,
    lat_col: str = "lat",
    lon_col: str = "lon",
    popup_cols: list[str] | None = None,
) -> folium.Map:
    valid = validate_coordinates(df, lat_col=lat_col, lon_col=lon_col)
    if valid.empty:
        return folium.Map(location=[20.0, 0.0], zoom_start=2)

    center = [valid[lat_col].mean(), valid[lon_col].mean()]
    fmap = folium.Map(location=center, zoom_start=4, control_scale=True)
    popup_cols = popup_cols or [col for col in ["mention", "selected_name", "name", "country", "method"] if col in valid.columns]

    for _, row in valid.iterrows():
        popup_html = "<br>".join(f"<b>{col}</b>: {row.get(col, '')}" for col in popup_cols)
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=folium.Popup(popup_html, max_width=350),
        ).add_to(fmap)

    return fmap


def save_map(map_obj: folium.Map, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    map_obj.save(str(path))
    return path

