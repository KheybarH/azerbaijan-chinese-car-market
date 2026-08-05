import duckdb
from pathlib import Path
from datetime import datetime


class DuckDBLoader:
    """Təmiz datanı DuckDB-yə yükləyir."""

    def __init__(self, db_path: str = "data/warehouse/cars.duckdb"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.con = duckdb.connect(str(self.db_path))

    def load_from_parquet(self, parquet_path: str, table_name: str = "chinese_cars"):
        """Parquet faylından datanı DuckDB cədvəlinə yükləyir."""
        parquet_path = Path(parquet_path)

        if not parquet_path.exists():
            raise FileNotFoundError(f"Fayl tapılmadı: {parquet_path}")

        # Cədvəli yaradırıq / yeniləyirik
        self.con.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_parquet('{parquet_path.as_posix()}')
        """)

        count = self.con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"'{table_name}' cədvəlinə {count} sətir yükləndi.")
        return self

    def show_sample(self, table_name: str = "chinese_cars", limit: int = 5):
        """Cədvəldən nümunə göstərir."""
        print(f"\n--- {table_name} nümunə ---")
        result = self.con.execute(f"SELECT * FROM {table_name} LIMIT {limit}").fetchdf()
        print(result.to_string())
        return self

    def run_basic_analysis(self, table_name: str = "chinese_cars"):
        """Sadə analitik sorğular işə salır."""
        print("\n=== Əsas Analiz ===")

        # 1. Ümumi elan sayı
        total = self.con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"Ümumi elan sayı: {total}")

        # 2. Marka üzrə say
        print("\nMarka üzrə elan sayı:")
        brands = self.con.execute(f"""
            SELECT brand, COUNT(*) as say 
            FROM {table_name} 
            GROUP BY brand 
            ORDER BY say DESC
        """).fetchdf()
        print(brands.to_string(index=False))

        # 3. Orta qiymət
        print("\nMarka üzrə orta qiymət (AZN):")
        avg_price = self.con.execute(f"""
            SELECT brand, 
                   ROUND(AVG(price_azn), 0) as orta_qiymet,
                   COUNT(*) as say
            FROM {table_name}
            WHERE price_azn IS NOT NULL
            GROUP BY brand
            ORDER BY orta_qiymet DESC
        """).fetchdf()
        print(avg_price.to_string(index=False))

        # 4. Şəhər üzrə paylanma
        print("\nŞəhər üzrə elan sayı:")
        cities = self.con.execute(f"""
            SELECT city, COUNT(*) as say 
            FROM {table_name} 
            GROUP BY city 
            ORDER BY say DESC
            LIMIT 10
        """).fetchdf()
        print(cities.to_string(index=False))

        return self

    def close(self):
        self.con.close()
        print("\nDuckDB bağlantısı bağlandı.")


if __name__ == "__main__":
    # Ən son parquet faylını tap
    processed_files = sorted(Path("data/processed").glob("chinese_cars_clean_*.parquet"))
    
    if not processed_files:
        print("Processed parquet faylı tapılmadı!")
    else:
        latest_parquet = processed_files[-1]
        print(f"İşlənən fayl: {latest_parquet}")

        loader = DuckDBLoader()
        try:
            loader.load_from_parquet(latest_parquet)
            loader.show_sample()
            loader.run_basic_analysis()
        finally:
            loader.close()