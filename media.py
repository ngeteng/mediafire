import requests
from bs4 import BeautifulSoup
import speedtest
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.live import Live
from rich.spinner import Spinner
import sys
import time
import os

# Inisialisasi console Rich untuk output yang cantik
console = Console()

def check_internet_speed():
    """
    Mengecek kecepatan download dan upload menggunakan speedtest-cli dan menampilkannya dalam tabel.
    """
    try:
        # Menampilkan spinner agar pengguna tahu ada proses yang berjalan
        with console.status("[bold cyan]Menguji kecepatan internet...", spinner="dots") as status:
            st = speedtest.Speedtest(secure=True)
            st.get_best_server()
            
            status.update("[bold cyan]Mengukur kecepatan download...")
            download_speed = st.download() / 1_000_000  # Konversi dari bit ke Megabit
            
            status.update("[bold cyan]Mengukur kecepatan upload...")
            upload_speed = st.upload() / 1_000_000    # Konversi dari bit ke Megabit
        
        # Buat tabel yang rapi untuk menampilkan hasil
        table = Table(title="🚀 Hasil Tes Kecepatan Internet", style="green", title_style="bold magenta")
        table.add_column("Tipe Koneksi", justify="right", style="cyan", no_wrap=True)
        table.add_column("Kecepatan (Mbps)", style="green")
        
        table.add_row("Download", f"{download_speed:.2f}")
        table.add_row("Upload", f"{upload_speed:.2f}")
        
        console.print(table)
        return True
    except speedtest.ConfigRetrievalError:
        console.print(Panel("[bold red]❌ Gagal menguji kecepatan internet. Pastikan Anda terhubung ke jaringan.[/bold red]", title="Error Koneksi", border_style="red"))
        return False
    except Exception as e:
        console.print(Panel(f"[bold red]Terjadi error tak terduga saat tes kecepatan: {e}[/bold red]", title="Error", border_style="red"))
        return False

def download_mediafire(url):
    """
    Mengunduh file dari URL MediaFire dengan tampilan yang dipercantik oleh Rich.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 1. Gunakan spinner saat mengambil info halaman untuk feedback visual
        with console.status("[bold yellow]Menganalisis halaman MediaFire...", spinner="earth") as status:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            download_button = soup.find('a', {'id': 'downloadButton'})

        if not download_button:
            console.print(Panel("[bold red]Tombol download tidak ditemukan. Struktur halaman mungkin berubah.[/bold red]", title="Error Parsing", border_style="red"))
            return

        direct_link = download_button['href']
        console.print(f"✅ [bold green]Link download langsung ditemukan![/bold green]")
        
        # 2. Download file dari link langsung dengan progress bar Rich yang canggih
        file_response = requests.get(direct_link, stream=True, headers=headers)
        file_response.raise_for_status()
        
        # Dapatkan nama file yang lebih bersih
        file_name = direct_link.split('/')[-1].split('?')[0]
        total_size = int(file_response.headers.get('content-length', 0))

        with Progress(
            TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("download", total=total_size, filename=file_name)
            
            # Buka file dan mulai menulis
            with open(file_name, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
        
        # 3. Verifikasi ukuran file setelah download
        downloaded_size = os.path.getsize(file_name)
        if total_size != 0 and downloaded_size != total_size:
            console.print(Panel(f"[bold yellow]Peringatan: Ukuran file yang diunduh ({downloaded_size} byte) tidak cocok dengan ukuran total ({total_size} byte).[/bold yellow]", title="Download Tidak Sempurna", border_style="yellow"))
        else:
            console.print(Panel(f"🎉 [bold green]Sukses! File disimpan sebagai '{file_name}'[/bold green]", title="Download Selesai", border_style="green"))

    except requests.exceptions.HTTPError as e:
        console.print(Panel(f"[bold red]Error HTTP: {e}. URL mungkin tidak valid atau file telah dihapus.[/bold red]", title="Error Jaringan", border_style="red"))
    except requests.exceptions.RequestException as e:
        console.print(Panel(f"[bold red]Terjadi kesalahan jaringan: {e}[/bold red]", title="Error Jaringan", border_style="red"))
    except Exception as e:
        console.print(Panel(f"[bold red]Terjadi kesalahan tak terduga: {e}[/bold red]", title="Error Kritis", border_style="red"))

# --- Bagian Utama untuk Menjalankan Script ---
if __name__ == "__main__":
    console.print(Panel(
        "🔥 [bold magenta]MediaFire Downloader Pro[/bold magenta] v2.0 🔥", 
        subtitle="[cyan]dipersembahkan oleh Ahli Python[/cyan]",
        expand=False, 
        border_style="yellow"
    ))

    # Lakukan tes kecepatan terlebih dahulu
    if check_internet_speed():
        console.print("\n") # Beri spasi
        
        # Logika untuk mendapatkan URL tetap sama
        if len(sys.argv) > 1:
            mediafire_url = sys.argv[1]
        else:
            mediafire_url = console.input("[bold]➡️ Masukkan URL MediaFire: [/bold]")

        if "mediafire.com" not in mediafire_url:
            console.print(Panel("[bold red]URL yang Anda masukkan sepertinya bukan URL MediaFire yang valid.[/bold red]", title="Error Input", border_style="red"))
        else:
            download_mediafire(mediafire_url)
            
    console.print("\n[bold]Program Selesai. Terima kasih![/bold]")
