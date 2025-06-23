import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys

def download_mediafire(url):
    """
    Mengunduh file dari URL MediaFire yang diberikan.
    """
    try:
        print("Mendapatkan informasi halaman...")
        # Headers untuk meniru browser agar tidak diblokir
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 1. Ambil konten halaman web
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Cek jika ada error HTTP (spt 404)

        # 2. Parsing HTML untuk mencari link download
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cari tombol download. Tombol ini biasanya ada di dalam tag <a> dengan id 'downloadButton'
        download_button = soup.find('a', {'id': 'downloadButton'})

        if not download_button:
            print("Error: Tombol download tidak ditemukan.")
            print("Mungkin struktur halaman MediaFire telah berubah atau URL tidak valid.")
            return

        direct_link = download_button['href']
        print(f"Link download langsung ditemukan: {direct_link}")

        # 3. Download file dari link langsung dengan stream=True
        print("Memulai proses download...")
        file_response = requests.get(direct_link, stream=True, headers=headers)
        file_response.raise_for_status()

        # Ambil nama file dari URL
        file_name = direct_link.split('/')[-1]

        # Ambil total ukuran file dari header untuk progress bar
        total_size = int(file_response.headers.get('content-length', 0))

        # Buat progress bar dengan tqdm
        progress_bar = tqdm(
            total=total_size, 
            unit='iB', 
            unit_scale=True,
            desc=file_name
        )

        # Buka file lokal dalam mode 'write binary' ('wb')
        with open(file_name, 'wb') as f:
            for chunk in file_response.iter_content(chunk_size=8192):
                if chunk:
                    progress_bar.update(len(chunk))
                    f.write(chunk)
        
        progress_bar.close()

        # Cek jika ukuran file yang di-download sesuai
        if total_size != 0 and progress_bar.n != total_size:
            print("Error: Download tidak selesai sepenuhnya.")
        else:
            print(f"\nSukses! File berhasil di-download sebagai '{file_name}'")

    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan jaringan: {e}")
    except Exception as e:
        print(f"Terjadi kesalahan tak terduga: {e}")

# --- Bagian Utama untuk Menjalankan Script ---
if __name__ == "__main__":
    # Cek apakah URL diberikan sebagai argumen command line
    if len(sys.argv) > 1:
        mediafire_url = sys.argv[1]
    else:
        # Jika tidak, minta pengguna untuk memasukkan URL
        mediafire_url = input("Masukkan URL MediaFire: ")

    if "mediafire.com" not in mediafire_url:
        print("URL yang Anda masukkan sepertinya bukan URL MediaFire yang valid.")
    else:
        download_mediafire(mediafire_url)
