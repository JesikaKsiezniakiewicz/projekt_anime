# System Analizy Danych Rynku Anime (Kitsu API Live)

Projekt zaliczeniowy z języka Python realizujący dynamiczną analizę danych rynkowych z wykorzystaniem zaawansowanych bibliotek analitycznych oraz interfejsu graficznego użytkownika (GUI).

## Autor: 
Jesika Księżniakiewicz

## Wykorzystane Technologie i Biblioteki
- **Python 3** (Główny język programowania)
- **Tkinter / TTK** (Interfejs graficzny użytkownika)
- **Requests** (Pobieranie dynamiczne danych z API HTTP GET)
- **Pandas & NumPy** (Czyszczenie, filtrowanie, agregacja i statystyka opisowa)
- **Matplotlib** (Generowanie i osadzanie wykresów w oknie aplikacji)

## Struktura Projektu
- `main.py` - Warstwa prezentacji (GUI, zarządzanie widżetami, walidacja pól wejściowych, osadzanie wykresów).
- `analyzer.py` - Warstwa logiki biznesowej (komunikacja z API, operacje na DataFrame, zaawansowane filtrowanie, generowanie wykresów).
- `.gitignore` - Plik konfiguracyjny wykluczający pliki tymczasowe z repozytorium.

## Instrukcja Uruchomienia
1. Zainstaluj wymagane biblioteki zewnętrzne:
   ```bash
   pip install requests pandas numpy matplotlib