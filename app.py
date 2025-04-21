import streamlit as st
import pandas as pd
from matplotlib.path import Path
import re
import io

st.title("📍 Mapping Project ke Polygon STO (Tanpa Shapely)")

sto_file = st.file_uploader("Upload File STO (CSV)", type="csv")
project_file = st.file_uploader("Upload File Project (CSV)", type="csv")

def parse_point(wkt):
    match = re.match(r"POINT\s*\(\s*([\d\.\-]+)\s+([\d\.\-]+)\s*\)", wkt)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None

def parse_polygon(wkt):
    match = re.search(r"POLYGON\s*\(\((.*?)\)\)", wkt)
    if match:
        coords = match.group(1).split(",")
        polygon = []
        for coord in coords:
            x, y = map(float, coord.strip().split())
            polygon.append((x, y))
        return polygon
    return None

if sto_file and project_file:
    df_sto = pd.read_csv(sto_file)
    df_project = pd.read_csv(project_file)

    # Parsing polygon ke Path object
    df_sto['polygon_path'] = df_sto['Polygon dalam Format WKT'].apply(parse_polygon).apply(lambda p: Path(p) if p else None)

    results = []

    for _, row in df_project.iterrows():
        name = row['name']
        wkt_point = row['wkt']
        coord = parse_point(wkt_point)
        found_sto = "Tidak ditemukan"

        if coord:
            for _, sto in df_sto.iterrows():
                polygon_path = sto['polygon_path']
                if polygon_path and polygon_path.contains_point(coord):
                    found_sto = sto['Nama STO']
                    break

        results.append({
            'name': name,
            'sto': found_sto,
            'wkt': wkt_point
        })

    df_result = pd.DataFrame(results)
    st.success("🎉 Mapping selesai!")

    st.dataframe(df_result)

    # Download
    csv = df_result.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Hasil CSV", csv, "hasil_mapping.csv", "text/csv")
