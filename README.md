# Azerbaijan Chinese Car Market Pipeline
# Bu layihə şəxsi portfoliodur və yalnız öyrənmə məqsədlidir. Kommersiya istifadəsi yoxdur. Mənbə ictimai elan səhifələridir.

End-to-end Data Engineering layihəsi: Azərbaycanda Çin markalı avtomobillərin bazar analizi.

## Nə edir?
- Turbo.az-dan Çin markalı avtomobil elanlarını scrape edir
- Datani təmizləyir və strukturlaşdırır
- DuckDB-yə yükləyir
- Streamlit dashboard ilə vizuallaşdırır

## Əsas nəticələr
- 297 Çin markalı elan analiz edilib
- Bazarda lider: **Changan**
- Uni-Z aktiv satılan modellərdəndir (orta qiymət ~35.000 ₼)
- Elanların əksəriyyəti Bakıdadır

## Texnologiyalar
- Python
- Poetry
- httpx + BeautifulSoup (scraping)
- Pandas (cleaning)
- DuckDB (storage)
- Streamlit (dashboard)

## Layihə strukturu
src/
scraper/      # Data ingestion
processing/   # Cleaning & transformation
storage/      # DuckDB loader
analysis/     # SQL analizlər
dashboards/     # Streamlit app
data/
raw/          # Xam data
processed/    # Təmiz data
warehouse/    # DuckDB


## İşə salmaq
```bash
poetry install
poetry run python src/scraper/turbo_az.py
poetry run python src/processing/cleaner.py
poetry run python src/storage/loader.py
poetry run streamlit run dashboards/app.py
