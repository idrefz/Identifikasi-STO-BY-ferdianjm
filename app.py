import streamlit as st
import pandas as pd
from shapely import wkt
from shapely.geometry import shape, Point
from io import BytesIO

st.set_page_config(page_title="Mapping Project ke STO", layout="wide")
st.title("📍 Identifikasi STO dari Titik Project dan Polygon")

st.markdown("""
Upload:
- 🗺️ **Polygon STO** (CSV) → harus punya kolom polygon (WKT) dan nama STO
- 📌 **Project** (CSV) → harus punya kolom `name` dan `wkt` (format POINT)
""")

# Upload
polygon_file = st.file_uploader("🗺️ Upload File Polygon STO", type=["csv"])
project_file = st.file_uploader("📌 Upload File Project", type=["csv"])

if polygon_file and project_file:
    try:
        # === Baca Polygon CSV ===
        df_poly = pd.read_csv(polygon_file)
        poly_cols = df_poly.columns.tolist()
        sto_col = st.selectbox("📛 Kolom Nama STO", poly_cols)
        poly_col = st.selectbox("📐 Kolom Polygon (WKT)", poly_cols)

        df_poly["polygon"] = df_poly[poly_col].apply(wkt.loads)

        # === Baca Project CSV ===
        df_proj = pd.read_csv(project_file)
        if "name" not in df_proj.columns or "wkt" not in df_proj.columns:
            st.error("CSV Project harus punya kolom 'name' dan 'wkt'")
        else:
            df_proj["point"] = df_proj["wkt"].apply(wkt.loads)
            df_proj["latitude"] = df_proj["point"].apply(lambda p: p.y)
            df_proj["longitude"] = df_proj["point"].apply(lambda p: p.x)
            df_proj["koordinat"] = df_proj["latitude"].astype(str) + ", " + df_proj["longitude"].astype(str)

            # === Cek point dalam polygon ===
            def find_sto(point):
                for idx, row in df_poly.iterrows():
                    if row["polygon"].contains(point):
                        return row[sto_col]
                return "TIDAK TERDETEKSI"

            df_proj["STO"] = df_proj["point"].apply(find_sto)

            result = df_proj[["name", "STO", "koordinat"]]

            st.success("✅ Mapping selesai!")
            st.dataframe(result)

            # Download Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                result.to_excel(writer, index=False, sheet_name="Mapping")
            st.download_button("⬇️ Download Hasil Excel", output.getvalue(), "hasil_mapping.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"Terjadi error: {e}")
else:
    st.info("Silakan upload kedua file.")
