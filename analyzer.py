"""
Pobieranie danych z Kitsu Anime API oraz ich analiza
"""

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class AnimeDataAnalyzer:

    def __init__(self):
        self.api_url = "https://kitsu.io/api/edge/anime"
        self.df = pd.DataFrame()

    def fetch_top_anime_data(self):
        """Dynamicznie pobiera dane o najpopularniejszych anime bezpośrednio z API na żywo."""
        # Pobieramy paczkę najlepiej ocenianych i najpopularniejszych tytułów (limit 20 rekordów na zapytanie)
        params = {
            "page[limit]": 20,
            "sort": "-userCount"  # Sortowanie malejąco (popularność)
        }

        try:
            headers = {'Accept': 'application/vnd.api+json', 'Content-Type': 'application/vnd.api+json'}
            response = requests.get(self.api_url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                json_data = response.json()
                all_data = json_data.get("data", [])
            else:
                return False
        except requests.RequestException as e:
            print(f"Błąd sieciowy podczas zapytania do API: {e}")
            return False

        if not all_data:
            return False

        # Mapowanie struktury JSON Kitsu API do płaskiej tabeli pandas DataFrame
        processed_records = []
        for item in all_data:
            attributes = item.get("attributes", {})

            # Kitsu zwraca format jako 'TV', 'movie'
            anime_type = attributes.get("subtype", "Unknown")
            if anime_type:
                anime_type = str(anime_type).upper()

            processed_records.append(
                {
                    "id": item.get("id"),
                    "title": attributes.get("canonicalTitle"),
                    "type": anime_type,
                    "episodes": attributes.get("episodeCount"),
                    "score": attributes.get("averageRating"), # Ocena w skali 1-100
                    "members": attributes.get("userCount", 0), # Liczba widzów
                    "year": attributes.get("startDate"), # Zwraca np. "1999-10-20"
                }
            )

        self.df = pd.DataFrame(processed_records)

        # Oczyszczanie i konwersja danych przy użyciu pandas i numpy
        # Kitsu zwraca oceny w skali 0-100 (np. 85.4). Dzielimy przez 10, aby uzyskać standardową skalę 1-10
        self.df["score"] = pd.to_numeric(self.df["score"]).fillna(80.0) / 10.0
        self.df["episodes"] = pd.to_numeric(self.df["episodes"]).fillna(1).astype(int)
        self.df["members"] = pd.to_numeric(self.df["members"]).fillna(0).astype(int)

        # Wyciąganie roku z pełnej daty przy użyciu operacji na tekstach w pandas
        self.df["year"] = self.df["year"].astype(str).str.slice(0, 4)
        self.df["year"] = pd.to_numeric(self.df["year"], errors='coerce').fillna(2000).astype(int)

        return True

    def filter_data(self, anime_type="Wszystkie", year_from=1980, year_to=2026):
        """Filtruje dane w locie na podstawie parametrów przekazanych z interfejsu GUI."""
        if self.df.empty:
            return pd.DataFrame()

        filtered_df = self.df.copy()

        if anime_type != "Wszystkie":
            filtered_df = filtered_df[filtered_df["type"] == anime_type.upper()]

        filtered_df = filtered_df[(filtered_df["year"] >= year_from) & (filtered_df["year"] <= year_to)]
        return filtered_df

    def generate_correlation_plot(self, filtered_df):
        """Analiza 1: Wykres punktowy korelacji popularności do ocen z linią trendu numpy."""
        fig, ax = plt.subplots(figsize=(6, 4))

        if filtered_df.empty:
            ax.text(0.5, 0.5, "Brak danych dla wybranych filtrów", ha="center", va="center")
            return fig

        x = filtered_df["score"].values
        y = filtered_df["members"].values

        ax.scatter(x, y, alpha=0.7, color="#1f77b4", edgecolors="black", s=50)

        # Dopasowanie linii trendu za pomocą numpy.polyfit
        if len(x) > 1:
            try:
                m, b = np.polyfit(x, y, 1)
                x_sort = np.sort(x)
                ax.plot(x_sort, m * x_sort + b, color="#ff7f0e", linestyle="--", linewidth=2, label="Linia trendu")
                ax.legend()
            except Exception:
                pass

        ax.set_title("Korelacja: Ocena użytkowników vs Popularność serii")
        ax.set_xlabel("Średnia ocena (Skala 1-10)")
        ax.set_ylabel("Liczba członków społeczności")
        ax.grid(True, linestyle=":", alpha=0.6)
        plt.tight_layout()
        return fig

    def generate_type_distribution_plot(self, filtered_df):
        """Analiza 2: Wykres pudełkowy (Boxplot) ocen w zależności od formatu wydania."""
        fig, ax = plt.subplots(figsize=(6, 4))

        if filtered_df.empty or filtered_df["type"].nunique() < 1:
            ax.text(0.5, 0.5, "Brak wystarczającej ilości danych do wykresu", ha="center", va="center")
            return fig

        grouped_data = []
        labels = []
        for anime_type, group in filtered_df.groupby("type"):
            grouped_data.append(group["score"].dropna().values)
            labels.append(f"{anime_type}\n(n={len(group)})")

        ax.boxplot(grouped_data, tick_labels=labels, patch_artist=True,
                   boxprops=dict(facecolor="#c9daf8", color="#3c78d8"),
                   medianprops=dict(color="#1155cc"))

        ax.set_title("Rozkład ocen w zależności od formatu produkcji")
        ax.set_ylabel("Ocena (Skala 1-10)")
        ax.grid(True, axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        return fig

    def get_summary_statistics(self, filtered_df):
        """Wylicza podstawowe statystyki opisowe dla przefiltrowanego zbioru danych."""
        if filtered_df.empty:
            return "Brak danych do wyliczenia statystyk."

        summary = (
            f"--- STATYSTYKI OPISOWE ---\n"
            f"Liczba serii w filtrze: {len(filtered_df)}\n"
            f"Średnia ocena: {filtered_df['score'].mean():.2f}/10\n"
            f"Mediana ocen: {filtered_df['score'].median():.2f}\n"
            f"Najwyższa ocena: {filtered_df['score'].max():.2f}\n"
            f"Najniższa ocena: {filtered_df['score'].min():.2f}\n"
            f"Max populacja: {filtered_df['members'].max():,}\n"
            f"Średnia liczba odc.: {filtered_df['episodes'].mean():.1f}"
        )
        return summary