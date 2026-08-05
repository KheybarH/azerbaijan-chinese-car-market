import duckdb

con = duckdb.connect("data/warehouse/cars.duckdb")

print("=== Yalnız CHANGAN UNI-Z ===")
uni_z = con.execute("""
    SELECT name, year, mileage_km, price_azn, city, url
    FROM chinese_cars
    WHERE lower(name) LIKE '%uni-z%'
       OR lower(name) LIKE '%uni z%'
    ORDER BY year, price_azn
""").fetchdf()

if len(uni_z) == 0:
    print("Heç bir Uni-Z elanı tapılmadı.")
else:
    print(f"Tapılan elan sayı: {len(uni_z)}")
    print(uni_z.to_string())

    print("\n=== Uni-Z il üzrə orta qiymət ===")
    by_year = con.execute("""
        SELECT year,
               COUNT(*) as say,
               ROUND(AVG(price_azn), 0) as orta_qiymet,
               ROUND(MIN(price_azn), 0) as min_qiymet,
               ROUND(MAX(price_azn), 0) as max_qiymet
        FROM chinese_cars
        WHERE (lower(name) LIKE '%uni-z%' OR lower(name) LIKE '%uni z%')
          AND price_azn IS NOT NULL
        GROUP BY year
        ORDER BY year
    """).fetchdf()
    print(by_year.to_string())
con.close()
import duckdb

con = duckdb.connect("data/warehouse/cars.duckdb")

print("=== Model + İl üzrə orta qiymət (ən az 2 il məlumatı olanlar) ===")
model_year = con.execute("""
    SELECT brand, model, year,
           COUNT(*) as say,
           ROUND(AVG(price_azn), 0) as orta_qiymet
    FROM chinese_cars
    WHERE price_azn IS NOT NULL 
      AND year IS NOT NULL 
      AND model IS NOT NULL
    GROUP BY brand, model, year
    HAVING COUNT(*) >= 2
    ORDER BY brand, model, year
""").fetchdf()
print(model_year.to_string())

print("\n=== Eyni modelin ən yeni və ən köhnə ili arasındakı fərq ===")
depreciation = con.execute("""
    WITH model_stats AS (
        SELECT 
            brand,
            model,
            MIN(year) as en_kohne_il,
            MAX(year) as en_yeni_il,
            COUNT(DISTINCT year) as il_sayi
        FROM chinese_cars
        WHERE price_azn IS NOT NULL AND year IS NOT NULL AND model IS NOT NULL
        GROUP BY brand, model
        HAVING COUNT(DISTINCT year) >= 2
    ),
    prices AS (
        SELECT 
            c.brand,
            c.model,
            c.year,
            ROUND(AVG(c.price_azn), 0) as orta_qiymet
        FROM chinese_cars c
        WHERE c.price_azn IS NOT NULL
        GROUP BY c.brand, c.model, c.year
    )
    SELECT 
        s.brand,
        s.model,
        s.en_kohne_il,
        s.en_yeni_il,
        p_old.orta_qiymet as kohne_qiymet,
        p_new.orta_qiymet as yeni_qiymet,
        ROUND(p_new.orta_qiymet - p_old.orta_qiymet, 0) as ferq,
        ROUND((p_new.orta_qiymet - p_old.orta_qiymet) * 1.0 / (s.en_yeni_il - s.en_kohne_il), 0) as illik_ferq
    FROM model_stats s
    JOIN prices p_old ON s.brand = p_old.brand AND s.model = p_old.model AND s.en_kohne_il = p_old.year
    JOIN prices p_new ON s.brand = p_new.brand AND s.model = p_new.model AND s.en_yeni_il = p_new.year
    ORDER BY illik_ferq ASC
""").fetchdf()

print(depreciation.to_string())

con.close()