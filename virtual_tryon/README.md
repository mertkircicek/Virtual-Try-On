# Virtual Try-On Uygulaması

Bu uygulama, kullanıcıların seçtikleri tişörtleri sanal olarak denemelerini sağlayan bir masaüstü uygulamasıdır.

## Kurulum

1. Python 3.8 veya daha yüksek bir sürümü yükleyin:
   - [Python İndirme Sayfası](https://www.python.org/downloads/)
   - Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin

2. Projeyi indirin ve açın:
   - Zip dosyasını indirin
   - İstediğiniz bir klasöre çıkartın (örn: `C:\Users\Kullanici\Desktop\virtual_tryon`)

3. Komut istemini (Command Prompt) açın:
   - Windows tuşu + R'ye basın
   - `cmd` yazıp Enter'a basın
   - Proje klasörüne gidin:
     ```bash
     cd C:\Users\Kullanici\Desktop\virtual_tryon
     ```

4. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

5. Cascade dosyasını indirin:
   - `setup.py` dosyasını çalıştırın:
     ```bash
     python setup.py
     ```
   - Bu komut otomatik olarak cascade dosyasını indirip `data` klasörüne koyacaktır

6. Örnek görselleri hazırlayın:
   - `data` klasörü oluşturun (eğer yoksa)
   - Bu klasöre denemek istediğiniz görselleri koyun:
     - Tişört görselleri: PNG formatında, şeffaf arka planlı (örn: `cloth1.png`, `cloth2.png`)
     - Kişi görselleri: JPG formatında (örn: `person1.jpg`, `person2.jpg`)

## Kullanım

1. Uygulamayı başlatın:
   ```bash
   python gui_app.py
   ```

2. Arayüzden:
   - Önce bir tişört seçin
   - Sonra bir kişi görseli seçin
   - "Noktaları Seç ve Giydir" butonuna tıklayın
   - Tişört üzerinde sırasıyla sol omuz, sağ omuz ve bel ortası noktalarını seçin
   - Kişi görseli üzerinde aynı noktaları seçin
   - Sonucu görmek için "Çıktıyı Göster" butonuna tıklayın

## Notlar

- Tişört görselleri PNG formatında ve şeffaf arka planlı olmalıdır
- Kişi görselleri JPG formatında olmalıdır
- Nokta seçimlerinde sıraya dikkat edin: sol omuz -> sağ omuz -> bel ortası
- Yüz tanıma özelliği için cascade dosyasının doğru konumda olduğundan emin olun

## Sorun Giderme

1. "Python bulunamadı" hatası alırsanız:
   - Python'un doğru kurulduğundan emin olun
   - Komut istemini kapatıp yeniden açın
   - `python --version` komutu ile Python'un kurulu olduğunu kontrol edin

2. Paket kurulum hatası alırsanız:
   - İnternet bağlantınızı kontrol edin
   - `pip install --upgrade pip` komutu ile pip'i güncelleyin
   - Sonra tekrar `pip install -r requirements.txt` komutunu çalıştırın

3. Cascade dosyası hatası alırsanız:
   - `data` klasörünün varlığını kontrol edin
   - `setup.py` dosyasını tekrar çalıştırın
   - Manuel olarak [cascade dosyasını indirip](https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml) `data` klasörüne koyun 