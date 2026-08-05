import streamlit as st
import duckdb
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Azərbaycan Çin Avtomobil Bazarı",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Azərbaycan Çin Avtomobil Bazarı Analizi")
st.markdown("Turbo.az-dan toplanmış Çin markalı avtomobillərin analizi")

# DuckDB bağlantısı
DB_PATH = "data/warehouse/cars.duckdb"

@st.cache_data
def load_data():
    if not Path(DB_PATH).exists():
        st.error("DuckDB faylı tapılmadı. Əvvəlcə loader.py-ni işə sal.")
        return None
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute("SELECT * FROM chinese_cars").fetchdf()
    con.close()
    return df

df = load_data()

if df is not None:
    # Üst statistika
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ümumi elan", len(df))
    col2.metric("Marka sayı", df["brand"].nunique())
    col3.metric("Orta qiymət", f"{df['price_azn'].mean():,.0f} ₼")
    col4.metric("Median qiymət", f"{df['price_azn'].median():,.0f} ₼")

    st.divider()

    # Marka üzrə analiz
    st.subheader("Marka üzrə elan sayı")
    brand_counts = df["brand"].value_counts().reset_index()
    brand_counts.columns = ["Marka", "Say"]
    st.bar_chart(brand_counts.set_index("Marka"))

    st.subheader("Marka üzrə orta qiymət (AZN)")
    brand_price = (
        df.groupby("brand")["price_azn"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    brand_price.columns = ["Marka", "Orta qiymət"]
    st.bar_chart(brand_price.set_index("Marka"))

    # Şəhər paylanması
    st.subheader("Şəhər üzrə paylanma")
    city_counts = df["city"].value_counts().head(10).reset_index()
    city_counts.columns = ["Şəhər", "Say"]
    st.bar_chart(city_counts.set_index("Şəhər"))

    # İl üzrə
    st.subheader("İl üzrə elan sayı")
    year_counts = df["year"].value_counts().sort_index().reset_index()
    year_counts.columns = ["İl", "Say"]
    st.bar_chart(year_counts.set_index("İl"))

    # Data cədvəli
    st.subheader("Bütün elanlar")
    st.dataframe(
        df[["brand", "model", "year", "engine_l", "mileage_km", "price_azn", "city", "url"]],
        use_container_width=True
    )
else:
    st.warning("Data yüklənmədi.")