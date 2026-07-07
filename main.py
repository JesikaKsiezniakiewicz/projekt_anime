"""
Punkt uruchomieniowy aplikacji - buduje interfejs graficzny użytkownika (GUI)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from analyzer import AnimeDataAnalyzer


class AnimeAnalyzerGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("System Analizy Danych Rynku Anime (Kitsu API Live)")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f5f5f5")

        # Inicjalizacja instancji silnika analitycznego
        self.analyzer = AnimeDataAnalyzer()

        # Zmienne sterujące tkinter połączenia z polami GUI
        self.type_var = tk.StringVar(value="Wszystkie")
        self.year_from_var = tk.StringVar(value="1990")
        self.year_to_var = tk.StringVar(value="2026")

        # Przechowywanie aktualnie osadzonych wykresów w celu ich odświeżania
        self.canvas_plot1 = None
        self.canvas_plot2 = None

        self._create_widgets()
        self._load_initial_data_from_api()

    def _create_widgets(self):
        """Konstruuje estetyczny i użyteczny podział elementów w oknie aplikacji."""

        # --- PANEL GÓRNY (Pasek statusu żądania sieciowego) ---
        self.status_frame = tk.Frame(self.root, bg="#3c78d8", height=40)
        self.status_frame.pack(fill=tk.X, side=tk.TOP)

        self.status_label = tk.Label(
            self.status_frame,
            text="Nawiązywanie połączenia i pobieranie danych na żywo z Kitsu API...",
            fg="white",
            bg="#3c78d8",
            font=("Arial", 10, "bold"),
        )
        self.status_label.pack(pady=8)

        # --- PANEL LEWY (Filtry, parametry i przyciski akcji) ---
        left_panel = tk.LabelFrame(
            self.root, text=" Parametry Filtrowania Analiz ", font=("Arial", 10, "bold"), bg="#ffffff", padx=15, pady=15
        )
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)

        # Wybór typu
        tk.Label(left_panel, text="Format produkcji (Type):", bg="#ffffff", font=("Arial", 9)).pack(anchor=tk.W,pady=(5, 2))
        type_combo = ttk.Combobox(left_panel, textvariable=self.type_var, state="readonly", width=22)
        type_combo["values"] = ("Wszystkie", "TV", "Movie")
        type_combo.pack(pady=(0, 15))

        # Wybór przedziału czasowego
        tk.Label(left_panel, text="Rok wydania od:", bg="#ffffff", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 2))
        entry_from = ttk.Entry(left_panel, textvariable=self.year_from_var, width=25)
        entry_from.pack(pady=(0, 10))

        tk.Label(left_panel, text="Rok wydania do:", bg="#ffffff", font=("Arial", 9)).pack(anchor=tk.W, pady=(5, 2))
        entry_to = ttk.Entry(left_panel, textvariable=self.year_to_var, width=25)
        entry_to.pack(pady=(0, 20))

        # Przyciski sterujące
        self.btn_analyze = ttk.Button(left_panel, text="Uruchom Analizę Danych", command=self._execute_analysis, state=tk.DISABLED)
        self.btn_analyze.pack(fill=tk.X, pady=5)

        ttk.Button(left_panel, text="Resetuj Filtry", command=self._reset_filters).pack(fill=tk.X, pady=5)

        # Sekcja tekstowa statystyk opisowych
        tk.Label(left_panel, text="Raport tekstowy:", bg="#ffffff", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(25, 5))
        self.txt_report = tk.Text(left_panel, height=12, width=25, font=("Consolas", 9), bg="#fafafa", relief=tk.SOLID, bd=1)
        self.txt_report.pack(fill=tk.BOTH, expand=True)

        # --- PANEL PRAWY (Obszar rysowania interaktywnych wykresów) ---
        self.right_panel = tk.Frame(self.root, bg="#f5f5f5")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.plot_frame1 = tk.Frame(self.right_panel, bg="#ffffff", relief=tk.SOLID, bd=1)
        self.plot_frame1.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))

        self.plot_frame2 = tk.Frame(self.right_panel, bg="#ffffff", relief=tk.SOLID, bd=1)
        self.plot_frame2.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def _load_initial_data_from_api(self):
        """Pobiera dane na bieżąco z sieci i odblokowuje interfejs aplikacji."""
        self.root.update()
        success = self.analyzer.fetch_top_anime_data()

        if success:
            self.status_label.config(text="Dane z Kitsu API pobrane na żywo! Status: Połączono.", bg="#27ae60")
            self.status_frame.config(bg="#27ae60")
            self.btn_analyze.config(state=tk.NORMAL)
            self._execute_analysis()
        else:
            self.status_label.config(text="Błąd krytyczny: Brak odpowiedzi od API sieciowego.", bg="#c0392b")
            self.status_frame.config(bg="#c0392b")
            messagebox.showerror("Błąd Połączenia", "Nie można pobrać danych rynkowych z API. Sprawdź swoje połączenie z internetem.")

    def _execute_analysis(self):
        """Pobiera parametry z GUI, waliduje je, wykonuje filtry w pandas i odświeża rysunki matplotlib."""
        try:
            yr_from = int(self.year_from_var.get())
            yr_to = int(self.year_to_var.get())
        except ValueError:
            messagebox.showwarning("Błąd wejścia", "Pola przedziału czasowego muszą zawierać poprawne liczby całkowite (lata)!")
            return

        # Pobranie przefiltrowanej ramki danych
        filtered_df = self.analyzer.filter_data(
            anime_type=self.type_var.get(), year_from=yr_from, year_to=yr_to
        )

        # Wyświetlenie wyliczeń statystycznych w oknie aplikacji
        stats_text = self.analyzer.get_summary_statistics(filtered_df)
        self.txt_report.delete("1.0", tk.END)
        self.txt_report.insert(tk.END, stats_text)

        # Usunięcie starych wykresów z kontenerów tkinter
        if self.canvas_plot1:
            self.canvas_plot1.get_tk_widget().destroy()
        if self.canvas_plot2:
            self.canvas_plot2.get_tk_widget().destroy()

        # Osadzenie nowego wykresu korelacji (Analiza 1)
        fig1 = self.analyzer.generate_correlation_plot(filtered_df)
        self.canvas_plot1 = FigureCanvasTkAgg(fig1, master=self.plot_frame1)
        self.canvas_plot1.draw()
        self.canvas_plot1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Osadzenie nowego wykresu pudełkowego (Analiza 2)
        fig2 = self.analyzer.generate_type_distribution_plot(filtered_df)
        self.canvas_plot2 = FigureCanvasTkAgg(fig2, master=self.plot_frame2)
        self.canvas_plot2.draw()
        self.canvas_plot2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _reset_filters(self):
        """Przywraca domyślne stany kontrolek wejściowych."""
        self.type_var.set("Wszystkie")
        self.year_from_var.set("1990")
        self.year_to_var.set("2026")
        self._execute_analysis()


if __name__ == "__main__":
    main_window = tk.Tk()
    app = AnimeAnalyzerGUI(main_window)
    main_window.mainloop()