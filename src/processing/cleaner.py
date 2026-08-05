import json
import re
from pathlib import Path
from datetime import datetime
import pandas as pd


class CarDataCleaner:
    def __init__(self, raw_file: str):
        self.raw_file = Path(raw_file)
        self.df = None

    def load_raw_data(self):
        with open(self.raw_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.df = pd.DataFrame(data)
        print(f"Yükləndi: {len(self.df)} elan")
        return self

    def clean_price(self):
        def parse_price(price_text):
            if not price_text or pd.isna(price_text):
                return None
            numbers = re.sub(r"[^\d]", "", str(price_text))
            return int(numbers) if numbers else None
        self.df["price_azn"] = self.df["price_text"].apply(parse_price)
        return self

    def parse_attributes(self):
        def extract_year(text):
            if not text:
                return None
            match = re.search(r"(20\d{2})", str(text))
            return int(match.group(1)) if match else None

        def extract_engine(text):
            if not text:
                return None
            match = re.search(r"(\d+\.?\d*)\s*L", str(text), re.IGNORECASE)
            return float(match.group(1)) if match else None

        def extract_mileage(text):
            if not text:
                return None
            match = re.search(r"([\d\s]+)\s*km", str(text), re.IGNORECASE)
            if match:
                numbers = re.sub(r"\s", "", match.group(1))
                return int(numbers) if numbers else None
            return None

        self.df["year"] = self.df["attributes"].apply(extract_year)
        self.df["engine_l"] = self.df["attributes"].apply(extract_engine)
        self.df["mileage_km"] = self.df["attributes"].apply(extract_mileage)
        return self

    def parse_brand_model(self):
        def split_name(name):
            if not name:
                return None, None
            parts = str(name).strip().split(" ", 1)
            brand = parts[0]
            model = parts[1] if len(parts) > 1 else None
            return brand, model

        self.df[["brand", "model"]] = self.df["name"].apply(
            lambda x: pd.Series(split_name(x))
        )
        return self

    def parse_location(self):
        def extract_city(text):
            if not text:
                return None
            city = str(text).split(",")[0].strip()
            if city.lower() in ["sifarişlə", "sifarisle"]:
                return "Sifarişlə"
            return city
        self.df["city"] = self.df["location_date"].apply(extract_city)
        return self

    def remove_non_chinese(self):
        chinese = [
            "changan", "byd", "chery", "haval", "geely", "jac",
            "jetour", "gac", "dongfeng", "faw", "lifan", "gwm",
            "baic", "exeed", "omoda", "jaecoo", "great wall"
        ]
        before = len(self.df)
        self.df = self.df[self.df["brand"].str.lower().isin(chinese)].copy()
        print(f"Cin olmayan markalar silindi: {before - len(self.df)} setir")
        return self

    def add_metadata(self):
        self.df["scraped_at"] = pd.to_datetime(self.df["scraped_at"])
        self.df["processed_at"] = datetime.now()
        return self

    def select_final_columns(self):
        columns = [
            "brand", "model", "name", "year", "engine_l",
            "mileage_km", "price_azn", "city", "url",
            "scraped_at", "processed_at"
        ]
        existing = [c for c in columns if c in self.df.columns]
        self.df = self.df[existing]
        return self

    def run(self):
        (
            self
            .load_raw_data()
            .clean_price()
            .parse_attributes()
            .parse_brand_model()
            .parse_location()
            .remove_non_chinese()
            .add_metadata()
            .select_final_columns()
        )
        print("Cleaning tamamlandi.")
        print(f"Yekun setir sayi: {len(self.df)}")
        print("\nNumune data:")
        print(self.df.head(3).to_string())
        return self.df

    def save(self, output_path: str = None):
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/processed/chinese_cars_clean_{timestamp}"

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        parquet_file = f"{output_path}.parquet"
        self.df.to_parquet(parquet_file, index=False)

        csv_file = f"{output_path}.csv"
        self.df.to_csv(csv_file, index=False, encoding="utf-8-sig")

        print(f"\nTemiz data saxlanildi:")
        print(f"  - {parquet_file}")
        print(f"  - {csv_file}")
        return self


if __name__ == "__main__":
    raw_files = sorted(Path("data/raw").glob("chinese_cars_*.json"))
    if not raw_files:
        print("Raw data tapilmadi!")
    else:
        latest_raw = raw_files[-1]
        print(f"Islenen fayl: {latest_raw}")
        cleaner = CarDataCleaner(latest_raw)
        cleaner.run()
        cleaner.save()