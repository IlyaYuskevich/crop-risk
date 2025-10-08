import polars as pl

# List your CSV files
csv_files = ["./data/2010_2022.csv", "./data/remainder_2025.csv", "./data/2023_2025.csv"]

# Read all CSVs into LazyFrames
lazy_frames = [pl.scan_csv(path) for path in csv_files]

# Combine them
combined = pl.concat(lazy_frames).with_columns(
        pl.col("date").str.to_date(strict=False).alias("dt"),
    ).sort("dt").with_columns(
        pl.col("dt").dt.year().alias("year")
    ).filter(pl.col("dt").dt.year().is_between(2020, 2025))

# Collect into a single DataFrame and write to Parquet
combined.collect().write_parquet("./data/source.parquet", compression="zstd", statistics=True)