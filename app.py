import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely import wkt
from shapely.geometry import Point

st.set_page_config(page_title="Mapping Project ke STO", layout="wide")
st.title("📍 Identifikasi STO dari Titik Project dan Polygon")

st.markdown("""
Upload:
- 🗺️ **Polygon STO**: CSV dengan kolom Polygon WKT  
- 📌 **Project**: CSV dengan kolom `wkt` (format POINT(...)) dan `name`  
Sistem akan otomatis identifikasi titik masuk ke STO mana.
""")

polygon_file = st.file_uploader("🗺️ Upload File Polygon STO (CSV)", type=["csv"])
project_file = st.file_uploader("📌 Upload File Project (CSV)", type=["csv"])

if polygon_file and project_file:
    try:
        # === Polygon STO ===
        df_poly = pd.read_csv(polygon_file)
        sto_col = st.selectbox("📛 Pilih kolom label STO", df_poly.columns)
        wkt_col = st.selectbox("📐 Pilih kolom polygon (WKT)", df_poly.columns)
        df_poly["geometry"] = df_poly[wkt_col].apply(wkt.loads)
        gdf_poly = gpd.GeoDataFrame(df_poly, geometry="geometry", crs="EPSG:4326")

        # === Project ===
        df_proj = pd.read_csv(project_file)
        if "wkt" not in df_proj.columns or "name" not in df_proj.columns:
            st.error("File project harus punya kolom 'name' dan 'wkt' (format POINT).")
        else:
            df_proj["geometry"] = df_proj["wkt"].apply(wkt.loads)
            gdf_proj = gpd.GeoDataFrame(df_proj, geometry="geometry", crs="EPSG:4326")

            # Ambil koordinat sebagai teks
            gdf_proj["koordinat_project"] = gdf_proj["geometry"].apply(lambda p: f"{p.y}, {p.x}")

            # Spatial join
            gdf_result = gpd.sjoin(gdf_proj, gdf_poly, how="left", predicate="within")
            gdf_result = gdf_result.rename(columns={sto_col: "STO"})

            # Pilih kolom hasil
            result_df = gdf_result[["name", "STO", "koordinat_project"]]

            st.success("✅ Mapping selesai!")
            st.dataframe(result_df)

            # Download Excel
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                result_df.to_excel(writer, index=False, sheet_name="Hasil Mapping")
            st.download_button("⬇️ Download Hasil ke Excel", output.getvalue(), "hasil_mapping.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"❌ Error saat memproses: {e}")

else:
    st.info("Silakan upload kedua file.")
