import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import sys
from datetime import datetime

try:
    import tkintermapview
    from geopy.geocoders import Nominatim
except ImportError:
    messagebox.showerror("Error", "Missing libraries.\nPlease run: pip install tkintermapview geopy")
    sys.exit()

class UltimateMetaTagger:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Metadata")
        self.root.geometry("1200x800")
        
        self.files = []
        self.current_marker = None
        
        left_panel = tk.Frame(root, width=300, bg="#e0e0e0")
        left_panel.pack(side="left", fill="y")
        
        right_panel = tk.Frame(root)
        right_panel.pack(side="right", fill="both", expand=True)

        tk.Label(left_panel, text="1. Select Media Files", font=("Arial", 12, "bold"), bg="#e0e0e0").pack(pady=10)
        
        btn_frame = tk.Frame(left_panel, bg="#e0e0e0")
        btn_frame.pack(fill="x", padx=10)
        tk.Button(btn_frame, text="+ Add Files", command=self.select_files, bg="#fff").pack(side="left", fill="x", expand=True)
        tk.Button(btn_frame, text="Clear", command=self.clear_files, bg="#fff").pack(side="right", padx=(5,0))
        
        self.listbox = tk.Listbox(left_panel, selectmode=tk.EXTENDED)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.lbl_count = tk.Label(left_panel, text="0 files selected", bg="#e0e0e0")
        self.lbl_count.pack(pady=5)

        self.btn_run = tk.Button(left_panel, text="WRITE METADATA", command=self.process_files, 
                                 bg="#28a745", fg="white", font=("Arial", 14, "bold"), height=2)
        self.btn_run.pack(fill="x", padx=10, pady=20)

        tk.Label(left_panel, text="Process Log:", bg="#e0e0e0", anchor="w").pack(fill="x", padx=10)
        self.log_text = tk.Text(left_panel, height=10, font=("Consolas", 8), state="disabled")
        self.log_text.pack(fill="x", padx=10, pady=(0, 10))

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_general = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_general, text="  General Info  ")
        self.build_general_tab()

        self.tab_rights = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_rights, text="  People & Rights  ")
        self.build_rights_tab()

        self.tab_map = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_map, text="  Location / Map  ")
        self.build_map_tab()

        self.var_backup = tk.BooleanVar(value=False)
        tk.Checkbutton(right_panel, text="Keep original files as backup (file_original)", variable=self.var_backup).pack(anchor="e", padx=10)

    def build_general_tab(self):
        f = tk.Frame(self.tab_general, padx=20, pady=20)
        f.pack(fill="both", expand=True)

        tk.Label(f, text="Date Created (YYYY-MM-DD HH:MM:SS):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.entry_date = tk.Entry(f, width=30)
        self.entry_date.grid(row=0, column=1, sticky="w", pady=10)
        tk.Button(f, text="Set to Now", command=self.set_now).grid(row=0, column=2, padx=10)

        tk.Label(f, text="Title / Headline:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w")
        self.entry_title = tk.Entry(f, width=50)
        self.entry_title.grid(row=1, column=1, columnspan=2, sticky="w", pady=10)

        tk.Label(f, text="Description / Caption:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="nw") 
        self.entry_desc = tk.Text(f, width=50, height=4)
        self.entry_desc.grid(row=2, column=1, columnspan=2, sticky="w", pady=10)

        tk.Label(f, text="Keywords / Tags:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w")
        self.entry_keywords = tk.Entry(f, width=50)
        self.entry_keywords.grid(row=3, column=1, columnspan=2, sticky="w", pady=10)
        tk.Label(f, text="(comma separated, e.g.: Vacation, Summer, Family)", fg="gray").grid(row=4, column=1, sticky="w")

    def build_rights_tab(self):
        f = tk.Frame(self.tab_rights, padx=20, pady=20)
        f.pack(fill="both", expand=True)

        tk.Label(f, text="Artist / Creator:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=10)
        self.entry_artist = tk.Entry(f, width=40)
        self.entry_artist.grid(row=0, column=1, pady=10)

        tk.Label(f, text="Copyright Notice:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
        self.entry_copyright = tk.Entry(f, width=40)
        self.entry_copyright.grid(row=1, column=1, pady=10)

        tk.Label(f, text="Credit / Source:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=10)
        self.entry_credit = tk.Entry(f, width=40)
        self.entry_credit.grid(row=2, column=1, pady=10)

    def build_map_tab(self):
        top_frame = tk.Frame(self.tab_map, pady=5)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Search:").pack(side="left", padx=5)
        self.entry_search = tk.Entry(top_frame, width=30)
        self.entry_search.pack(side="left")
        self.entry_search.bind("<Return>", self.search_location)
        tk.Button(top_frame, text="Go", command=self.search_location).pack(side="left", padx=5)

        coord_frame = tk.Frame(self.tab_map, pady=5)
        coord_frame.pack(fill="x")
        
        tk.Label(coord_frame, text="Lat:").pack(side="left", padx=(10, 2))
        self.entry_lat = tk.Entry(coord_frame, width=12)
        self.entry_lat.pack(side="left")
        
        tk.Label(coord_frame, text="Lon:").pack(side="left", padx=(10, 2))
        self.entry_lon = tk.Entry(coord_frame, width=12)
        self.entry_lon.pack(side="left")

        tk.Label(coord_frame, text="City:").pack(side="left", padx=(10, 2))
        self.entry_city = tk.Entry(coord_frame, width=15)
        self.entry_city.pack(side="left")

        tk.Label(coord_frame, text="Country:").pack(side="left", padx=(10, 2))
        self.entry_country = tk.Entry(coord_frame, width=15)
        self.entry_country.pack(side="left")

        tk.Label(self.tab_map, text="Right-click on map to set location", fg="gray", font=("Arial", 8)).pack()

        self.map_widget = tkintermapview.TkinterMapView(self.tab_map, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_address("New York, USA")
        self.map_widget.add_right_click_menu_command(label="Set Location Here", command=self.add_marker_event, pass_coords=True)


    def add_marker_event(self, coords):
        if self.current_marker:
            self.map_widget.delete_marker(self.current_marker)
        
        self.current_marker = self.map_widget.set_marker(coords[0], coords[1], text="Selected")
        
        self.entry_lat.delete(0, tk.END)
        self.entry_lat.insert(0, str(round(coords[0], 6)))
        self.entry_lon.delete(0, tk.END)
        self.entry_lon.insert(0, str(round(coords[1], 6)))
        
        try:
            geolocator = Nominatim(user_agent="geo_tagger_app_v2")
            location = geolocator.reverse(f"{coords[0]}, {coords[1]}", language='en')
            if location:
                addr = location.raw.get('address', {})
                city = addr.get('city') or addr.get('town') or addr.get('village') or ""
                country = addr.get('country') or ""
                
                self.entry_city.delete(0, tk.END)
                self.entry_city.insert(0, city)
                self.entry_country.delete(0, tk.END)
                self.entry_country.insert(0, country)
        except Exception as e:
            print(f"Geocoding warning: {e}")

    def search_location(self, event=None):
        addr = self.entry_search.get()
        if addr:
            self.map_widget.set_address(addr)

    def select_files(self):
        filenames = filedialog.askopenfilenames()
        for f in filenames:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))
        self.lbl_count.config(text=f"{len(self.files)} files selected")

    def clear_files(self):
        self.files = []
        self.listbox.delete(0, tk.END)
        self.lbl_count.config(text="0 files selected")

    def set_now(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, now)

    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"> {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update_idletasks()

    def process_files(self):
        if not self.files:
            messagebox.showwarning("Warning", "No files selected.")
            return

        try:
            c_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            subprocess.run(["exiftool", "-ver"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=c_flags)
        except:
            messagebox.showerror("Error", "ExifTool executable not found in path or current folder.")
            return

        args = ["exiftool"]
        if not self.var_backup.get():
            args.append("-overwrite_original")

        
        date_str = self.entry_date.get().strip()
        if date_str:
            fmt_date = date_str.replace("-", ":")
            args += [f"-AllDates={fmt_date}", f"-QuickTime:CreateDate={fmt_date}", f"-QuickTime:ModifyDate={fmt_date}"]

        title = self.entry_title.get().strip()
        if title:
            args += [f"-Title={title}", f"-XPTitle={title}", f"-QuickTime:DisplayName={title}"]

        desc = self.entry_desc.get("1.0", tk.END).strip()
        if desc:
            args += [f"-ImageDescription={desc}", f"-Description={desc}", f"-Caption-Abstract={desc}", f"-QuickTime:Description={desc}"]

        keywords = self.entry_keywords.get().strip()
        if keywords:
            args += ["-sep", ", "]
            args += [f"-Keywords={keywords}", f"-Subject={keywords}"]

        artist = self.entry_artist.get().strip()
        if artist:
            args += [f"-Artist={artist}", f"-Creator={artist}", f"-QuickTime:Artist={artist}", f"-XPAuthor={artist}"]

        copyright_txt = self.entry_copyright.get().strip()
        if copyright_txt:
            args += [f"-Copyright={copyright_txt}", f"-Rights={copyright_txt}"]
            
        credit = self.entry_credit.get().strip()
        if credit:
             args += [f"-Credit={credit}", f"-Source={credit}"]

        lat = self.entry_lat.get().strip()
        lon = self.entry_lon.get().strip()
        city = self.entry_city.get().strip()
        country = self.entry_country.get().strip()

        if lat and lon:
            try:
                lat_v = float(lat)
                lon_v = float(lon)
                lat_ref = "N" if lat_v >= 0 else "S"
                lon_ref = "E" if lon_v >= 0 else "W"
                
                args += [
                    f"-GPSLatitude={abs(lat_v)}", f"-GPSLatitudeRef={lat_ref}",
                    f"-GPSLongitude={abs(lon_v)}", f"-GPSLongitudeRef={lon_ref}",
                    f"-QuickTime:GPSCoordinates={lat_v}, {lon_v}" 
                ]
            except ValueError:
                self.log("Error: Invalid GPS coordinates.")

        if city:
            args += [f"-City={city}", f"-IPTC:City={city}"]
        if country:
            args += [f"-Country={country}", f"-IPTC:Country-PrimaryLocationName={country}"]

        args.append("-charset")
        args.append("iptc=UTF8")
        
        args.extend(self.files)

        self.log(f"Processing {len(self.files)} files...")
        
        try:
            c_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            
            result = subprocess.run(args, capture_output=True, text=True, creationflags=c_flags)
            
            if result.returncode == 0:
                self.log("Success!")
                messagebox.showinfo("Done", "Metadata updated successfully.")
            else:
                self.log("Completed with warnings:")
                self.log(result.stderr)
                messagebox.showwarning("Warning", "Process finished, but check logs for details.")
                
        except Exception as e:
            self.log(f"Critical Error: {str(e)}")
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateMetaTagger(root)
    root.mainloop()