import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import json
from pathlib import Path


class TurboAzScraper:
    """Turbo.az saytindan Cin markali avtomobil elanlarini toplayan scraper."""

    BASE_URL = "https://turbo.az"
    SEARCH_URL = "https://turbo.az/autos"

    CHINESE_BRANDS = [
        "changan",
        "byd",
        "chery",
        "haval",
        "geely",
        "jac",
        "jetour",
        "gac",
        "dongfeng",
        "faw",
        "lifan",
        "great wall",
        "baic",
        "exeed",
        "omoda",
        "jaecoo"
    ]

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "az,en;q=0.9",
        }
        self.client = httpx.Client(headers=self.headers, timeout=30.0, follow_redirects=True)

    def get_page(self, page: int = 1) -> str:
        params = {"page": page}
        response = self.client.get(self.SEARCH_URL, params=params)
        response.raise_for_status()
        return response.text

    def parse_listing(self, card) -> dict | None:
        try:
            link_tag = card.select_one("a.products-i__link")
            if not link_tag:
                return None

            relative_url = link_tag.get("href", "")
            full_url = self.BASE_URL + relative_url if relative_url.startswith("/") else relative_url

            name_tag = card.select_one(".products-i__name")
            name = name_tag.get_text(strip=True) if name_tag else None

            price_text = None
            price_selectors = [".product-price", ".products-i__price", ".price", "[class*='price']"]
            for selector in price_selectors:
                price_tag = card.select_one(selector)
                if price_tag:
                    price_text = price_tag.get_text(strip=True)
                    if price_text:
                        break

            attributes_tag = card.select_one(".products-i__attributes")
            attributes = attributes_tag.get_text(strip=True) if attributes_tag else None

            datetime_tag = card.select_one(".products-i__datetime")
            location_date = datetime_tag.get_text(strip=True) if datetime_tag else None

            return {
                "name": name,
                "price_text": price_text,
                "attributes": attributes,
                "location_date": location_date,
                "url": full_url,
                "scraped_at": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"Parse xetasi: {e}")
            return None

    def is_chinese_brand(self, name: str) -> bool:
        if not name:
            return False
        name_lower = name.lower()
        return any(brand in name_lower for brand in self.CHINESE_BRANDS)

    def scrape_pages(self, max_pages: int = 3) -> list[dict]:
        all_cars = []

        for page in range(1, max_pages + 1):
            print(f"Sehife {page} islenir...")
            html = self.get_page(page)
            soup = BeautifulSoup(html, "lxml")

            cards = soup.select(".products-i")
            print(f"  -> {len(cards)} elan tapildi")

            for card in cards:
                car = self.parse_listing(card)
                if car and self.is_chinese_brand(car["name"]):
                    all_cars.append(car)

        print(f"\nUmumi Cin markali elan: {len(all_cars)}")
        return all_cars

    def save_to_json(self, data: list[dict], filename: str = None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/raw/chinese_cars_{timestamp}.json"

        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Data yadda saxlanildi: {path}")
        return path

    def close(self):
        self.client.close()


if __name__ == "__main__":
    scraper = TurboAzScraper()
    try:
        cars = scraper.scrape_pages(max_pages=70)
        if cars:
            scraper.save_to_json(cars)
            print("\nNumune elan:")
            print(cars[0])
        else:
            print("Hec bir Cin markali elan tapilmadi.")
    finally:
        scraper.close()