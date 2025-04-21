import streamlit as st
import pandas as pd
from shapely.wkt import loads as load_wkt
from shapely.geometry import Point
import io

st.title("Mapping Project ke Polygon STO")

# Upload file STO
sto_file = st.file_uploader("Upload File STO (CSV)", type="csv")
# Upload file project
project_file = st.file_uploader("Upload File Project (CSV)", type="csv")

if sto_file and project_file:
    # Load CSV
    df_sto = pd.read_csv(sto_file)
    df_project = pd.read_csv(project_file)

    # Ubah kolom polygon STO jadi objek Polygon
    df_sto['polygon_geom'] = df_sto['Polygon dalam Format WKT'].apply(load_wkt)

    result = []

    for idx, project in df_project.iterrows():
        point = load_wkt(project['wkt'])  # diasumsikan berbentuk POINT(x y)
        matched_sto = None

        for _, sto in df_sto.iterrows():
            if sto['polygon_geom'].contains(point):
                matched_sto = sto['Nama STO']
                break

        result.append({
            'name': project['name'],
            'sto': matched_sto if matched_sto else "Tidak ditemukan",
            'wkt': project['wkt']
        })

    df_result = pd.DataFrame(result)
    st.success("Mapping selesai!")

    st.dataframe(df_result)

    # Download link
    csv = df_result.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Hasil CSV",
        data=csv,
        file_name="hasil_mapping.csv",
        mime='text/csv',
    )
