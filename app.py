import streamlit as st
import pandas as pd
from matplotlib.path import Path
import re
from xml.dom import minidom

st.title("📍 Aplikasi Geospasial STO")

menu = st.sidebar.selectbox("Pilih Menu", ["Mapping Project ke STO", "KML ➜ Titik Tengah ➜ CSV"])

# -------------------- FUNGSI BANTU --------------------

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

def calculate_centroid(coords):
    x_list = [p[0] for p in coords]
    y_list = [p[1] for p in coords]
    n = len(coords)
    if n == 0:
        return None, None
    return sum(x_list)/n, sum(y_list)/n

# -------------------- MENU 1: Mapping Project --------------------

if menu == "Mapping Project ke STO":
    sto_file = st.file_uploader("Upload File STO (Excel - .xlsx)", type="xlsx")
    project_file = st.file_uploader("Upload File Project (CSV)", type="csv")

    if sto_file and project_file:
        df_sto = pd.read_excel(sto_file)
        df_project = pd.read_csv(project_file)

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

        csv = df_result.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Hasil CSV", csv, "hasil_mapping.csv", "text/csv")

# -------------------- MENU 2: Titik Tengah dari Polygon KML --------------------

elif menu == "KML ➜ Titik Tengah ➜ CSV":
    kml_file = st.file_uploader("Upload File KML", type="kml")

    if kml_file:
        st.info("📦 Membaca dan memproses file KML...")

        kml = minidom.parse(kml_file)
        placemarks = kml.getElementsByTagName("Placemark")

        data = []

        for placemark in placemarks:
            name = placemark.getElementsByTagName("name")[0].firstChild.nodeValue if placemark.getElementsByTagName("name") else "Unnamed"
            coords_tag = placemark.getElementsByTagName("coordinates")
            if coords_tag:
                coords_text = coords_tag[0].firstChild.nodeValue.strip()
                coords_raw = coords_text.replace('\n', '').split(" ")
                coords = []
                for c in coords_raw:
                    if ',' in c:
                        lon, lat, *_ = map(float, c.split(','))
                        coords.append((lon, lat))
                if coords:
                    centroid_lon, centroid_lat = calculate_centroid(coords)
                    data.append({
                        "name": name,
                        "latitude": centroid_lat,
                        "longitude": centroid_lon
                    })

        df_kml = pd.DataFrame(data)
        st.success(f"✅ Berhasil ditemukan {len(df_kml)} polygon.")

        st.dataframe(df_kml)

        csv_kml = df_kml.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Titik Tengah (CSV)", csv_kml, "titik_tengah_dari_kml.csv", "text/csv")
