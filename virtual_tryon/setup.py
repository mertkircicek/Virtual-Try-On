import os
import urllib.request
import shutil

def download_cascade():
    #Cascade dosyasını indirir ve data klasörüne kaydeder
    cascade_url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    cascade_path = os.path.join("data", "haarcascade_frontalface_default.xml")
    
    # data klasörünü oluştur
    os.makedirs("data", exist_ok=True)
    
    print("Cascade dosyası indiriliyor...")
    try:
        # Dosyayı indir
        urllib.request.urlretrieve(cascade_url, cascade_path)
        print(f"Cascade dosyası başarıyla indirildi: {cascade_path}")
    except Exception as e:
        print(f"Cascade dosyası indirilirken hata oluştu: {str(e)}")
        print("Lütfen dosyayı manuel olarak indirin ve data klasörüne kopyalayın.")
        print(f"İndirme linki: {cascade_url}")

if __name__ == "__main__":
    download_cascade() 