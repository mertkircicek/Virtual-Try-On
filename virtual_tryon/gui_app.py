import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from utils.points_selector import select_points
from warp import warp_cloth_from_points
import segment
import os
import cv2

class VirtualTryOnApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TARVİNA - Virtual Try-On Uygulaması")
        self.root.geometry("900x800")  # Pencere boyutunu küçülttüm
        self.root.configure(bg="#065b65")  
        
        style = ttk.Style()
        style.configure("Title.TLabel", 
                       font=("Helvetica", 28, "bold"), 
                       foreground="#1a1a1a")  
        style.configure("Subtitle.TLabel", 
                       font=("Helvetica", 12), 
                       foreground="#404040")  
        style.configure("Frame.TFrame", 
                       background="#ffffff", 
                       relief="solid", 
                       borderwidth=1)
        style.configure("Accent.TButton", 
                       font=("Helvetica", 10, "bold"),
                       padding=15,
                       background="#e71414",  
                       foreground="white")
        style.configure("Primary.TButton", 
                       font=("Helvetica", 12, "bold"),
                       padding=15,
                       background="#27ae60",  
                       foreground="white")
        style.configure("Secondary.TButton", 
                       font=("Helvetica", 10, "bold"),
                       padding=15,
                       foreground="white")
        style.configure("Info.TLabel", 
                       font=("Helvetica", 10, "bold"),
                       foreground="#2c3e50")
        
        # Ana kısım
        main_frame = ttk.Frame(root, padding="30", style="Frame.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık 
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = ttk.Label(
            title_frame, 
            text="👕 Virtual Try-On", 
            style="Title.TLabel"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Tişörtünüzü sanal olarak deneyin",
            style="Subtitle.TLabel"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Tişört seçim kısmı
        cloth_frame = ttk.LabelFrame(
            main_frame, 
            text="Tişört Seçimi", 
            padding="20",
            style="Frame.TFrame"
        )
        cloth_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.cloth_path = None
        self.person_path = None
        self.last_output_path = None
        self.output_window = None
        
        # Tişört butonları
        cloth_buttons_frame = ttk.Frame(cloth_frame)
        cloth_buttons_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            cloth_buttons_frame,
            text="Tişört 1",
            command=lambda: self.set_cloth("data/cloth1.png"),
            font=("Helvetica", 10, "bold"),
            bg="#594bd8",  
            fg="white",
            padx=15,
            pady=10,
            relief=tk.RAISED,
            borderwidth=2
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            cloth_buttons_frame,
            text="Tişört 2",
            command=lambda: self.set_cloth("data/cloth2.png"),
            font=("Helvetica", 10, "bold"),
            bg="#594bd8",  
            fg="white",
            padx=15,
            pady=10,
            relief=tk.RAISED,
            borderwidth=2
        ).pack(side=tk.LEFT, padx=10)
        
        # Kişi seçim kısmı
        person_frame = ttk.LabelFrame(
            main_frame, 
            text="Kişi Seçimi", 
            padding="20",
            style="Frame.TFrame"
        )
        person_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Kişi butonları
        person_buttons_frame = ttk.Frame(person_frame)
        person_buttons_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            person_buttons_frame,
            text="Kişi 1",
            command=lambda: self.set_person("data/person1.jpg"),
            font=("Helvetica", 10, "bold"),
            bg="#594bd8",  
            fg="white",
            padx=15,
            pady=10,
            relief=tk.RAISED,
            borderwidth=2
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            person_buttons_frame,
            text="Kişi 2",
            command=lambda: self.set_person("data/person2.jpg"),
            font=("Helvetica", 10, "bold"),
            bg="#594bd8",  
            fg="white",
            padx=15,
            pady=10,
            relief=tk.RAISED,
            borderwidth=2
        ).pack(side=tk.LEFT, padx=10)
        
        # İşlem butonları kısmı
        action_frame = ttk.Frame(main_frame, style="Frame.TFrame")
        action_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Ana işlem butonu
        tk.Button(
            action_frame,
            text="📌 Noktaları Seç ve Giydir",
            command=self.run_tryon,
            font=("Helvetica", 12, "bold"),
            bg="#27ae60",  
            fg="white",
            padx=15,
            pady=10,
            relief=tk.RAISED,
            borderwidth=2
        ).pack(fill=tk.X, pady=20, padx=20)
        
        # Seçilen dosya bilgileri
        self.cloth_info = ttk.Label(
            cloth_frame, 
            text="Henüz tişört seçilmedi",
            style="Info.TLabel"
        )
        self.cloth_info.pack(pady=10)
        
        self.person_info = ttk.Label(
            person_frame, 
            text="Henüz kişi seçilmedi",
            style="Info.TLabel"
        )
        self.person_info.pack(pady=10)
        
        # Durum çubuğu
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        status_bar = ttk.Label(
            root, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            padding="10",
            font=("Helvetica", 9, "bold"),  
            foreground="#1a1a1a"  
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_cloth(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Hata", f"Tişört dosyası bulunamadı: {path}")
            return
        self.cloth_path = path
        self.cloth_info.config(text=f"Seçilen fotoğraf: {os.path.basename(path)}")
        self.status_var.set(f"Tişört seçildi: {os.path.basename(path)}")
        print(f"[INFO] Seçilen fotoğraf: {path}")

    def set_person(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Hata", f"Kişi görseli bulunamadı: {path}")
            return
        self.person_path = path
        self.person_info.config(text=f"Seçilen fotoğraf: {os.path.basename(path)}")
        self.status_var.set(f"Kişi seçildi: {os.path.basename(path)}")
        print(f"[INFO] Seçilen fotoğraf: {path}")

    def run_tryon(self):
        if not self.cloth_path or not self.person_path:
            messagebox.showwarning("Uyarı", "Lütfen hem tişört hem kişi görseli seçin.")
            return

        self.status_var.set("İşlem başlatılıyor...")
        self.root.update()

        print(f"[DEBUG] Seçilen tişört: {self.cloth_path}")
        print(f"[DEBUG] Seçilen kişi: {self.person_path}")

        if not os.path.exists(self.cloth_path):
            messagebox.showerror("Hata", f"Tişört dosyası bulunamadı: {self.cloth_path}")
            return
        if not os.path.exists(self.person_path):
            messagebox.showerror("Hata", f"Kişi görseli bulunamadı: {self.person_path}")
            return

        # Kişi görselini tişört görselinin genişliğine göre yeniden boyutlandırma yapmak için;
        try:
            cloth_img = cv2.imread(self.cloth_path, cv2.IMREAD_UNCHANGED) # Alpha kanalını da okumak için UNCHANGED
            person_img = cv2.imread(self.person_path)

            if cloth_img is None:
                 raise FileNotFoundError(f"Tişört görseli yüklenemedi: {self.cloth_path}")
            if person_img is None:
                 raise FileNotFoundError(f"Kişi görseli yüklenemedi: {self.person_path}")

            new_width = cloth_img.shape[1]
            aspect_ratio = person_img.shape[0] / person_img.shape[1]
            new_height = int(new_width * aspect_ratio)
            
            resized_person_img = cv2.resize(person_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            resized_person_path = "output/resized_person.jpg"
            cv2.imwrite(resized_person_path, resized_person_img)
            print(f"[DEBUG] Kişi görseli yeniden boyutlandırıldı ve kaydedildi: {resized_person_path}")
            
            current_person_path = resized_person_path

        except Exception as e:
            print(f"[ERROR] Kişi görselini yeniden boyutlandırma hatası: {str(e)}")
            messagebox.showerror("Hata", f"Kişi görselini yeniden boyutlandırma hatası: {str(e)}")
            return

        # Eski çıktıları temizlemek için;
        output_dir = "output"
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.startswith("warped_") and file.endswith(".png"):
                    try:
                        os.remove(os.path.join(output_dir, file))
                    except:
                        pass

        print("[INFO] Segmentasyon başlatılıyor...")
        print(f"[DEBUG] Segmentasyon için kullanılan kişi görseli: {current_person_path}")
        segment.run_segmentation(input_path=current_person_path)

        # Segmentasyon sonrası mask.png'nin varlığını kontrol etmek için;
        mask_path = "output/mask.png"
        if not os.path.exists(mask_path):
            messagebox.showerror("Hata", "Segmentasyon maskesi oluşturulamadı.")
            return
        print(f"[DEBUG] Segmentasyon maskesi oluşturuldu: {mask_path}")

        # Yüz tespiti yapmak ve maskeden çıkarılması için;
        try:
            # Cascade dosyasının uygulamanın çalıştığı dizine göreceli yolu
            cascade_name = 'haarcascade_frontalface_default.xml'
            # 'data' klasörü içinde aranacak
            cascade_path = os.path.join("data", cascade_name)

            print(f"[DEBUG] Cascade dosyası yolu: {cascade_path}")

            if not os.path.exists(cascade_path):
                 # data klasöründe yoksa, opencv-contrib-python paketinin yüklü olduğu yerden bulmaya çalışır
                try:
                    # opencv-contrib-python paketinin data yolunu bul
                    import site
                    opencv_contrib_path = next(s for s in site.getsitepackages() if 'opencv_contrib_python' in s)
                    alt_cascade_path = os.path.join(opencv_contrib_path, 'cv2', 'data', cascade_name)
                    if os.path.exists(alt_cascade_path):
                        cascade_path = alt_cascade_path
                        print(f"[DEBUG] Alternatif cascade dosyası yolu bulundu: {cascade_path}")
                    else:
                         raise FileNotFoundError(f"Cascade dosyası bulunamadı: {cascade_path} veya {alt_cascade_path}")
                except Exception as e:
                    raise FileNotFoundError(f"Cascade dosyası bulunamadı ve alternatif yol bulunamadı: {e}")


            face_cascade = cv2.CascadeClassifier(cascade_path)
            mask_img = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            person_img_resized_gray = cv2.imread(current_person_path, cv2.IMREAD_GRAYSCALE) # Yüz tespiti için gri tonlama

            if mask_img is None:
                 raise Exception(f"Maske görseli yüklenemedi: {mask_path}")
            if person_img_resized_gray is None:
                 raise Exception(f"Yeniden boyutlandırılmış kişi görseli gri tonlama yüklenemedi: {current_person_path}")

            faces = face_cascade.detectMultiScale(person_img_resized_gray, 1.1, 4)
            print(f"[DEBUG] Tespit edilen yüz sayısı: {len(faces)}")

            # Yüz bölgesini daha geniş bir alan olarak işaretleyerek ayrımı kolaylaştırdım
            for (x, y, w, h) in faces:
                # Yüz bölgesini daha geniş bir alan olarak işaretlemek için;
                padding_x = int(w * 0.3)  # Yüz genişliğinin %30'u kadar yatay boşluk
                padding_y = int(h * 0.4)  # Yüz yüksekliğinin %40'ı kadar dikey boşluk
                
                # Yüz bölgesini genişletmek ve sınırları kontrol etmek için;
                start_y = max(0, y - padding_y)
                end_y = min(mask_img.shape[0], y + h + padding_y)
                start_x = max(0, x - padding_x)
                end_x = min(mask_img.shape[1], x + w + padding_x)

                # Yüz bölgesini maskede siyaha boyar
                mask_img[start_y:end_y, start_x:end_x] = 0
                
                # Yüz bölgesinin etrafına yumuşak geçiş ekler
                feather_size = 20
                for i in range(feather_size):
                    alpha = i / feather_size
                    # Üst kenar
                    if start_y - i >= 0:
                        mask_img[start_y - i, start_x:end_x] = int(255 * alpha)
                    # Alt kenar
                    if end_y + i < mask_img.shape[0]:
                        mask_img[end_y + i, start_x:end_x] = int(255 * alpha)
                    # Sol kenar
                    if start_x - i >= 0:
                        mask_img[start_y:end_y, start_x - i] = int(255 * alpha)
                    # Sağ kenar
                    if end_x + i < mask_img.shape[1]:
                        mask_img[start_y:end_y, end_x + i] = int(255 * alpha)

                print(f"[DEBUG] Maskeden yüz bölgesi çıkarıldı (genişletilmiş ve yumuşatılmış): ({start_x}, {start_y}, {end_x-start_x}, {end_y-start_y})")

            cv2.imwrite(mask_path, mask_img)
            print(f"[DEBUG] Düzenlenmiş maske kaydedildi: {mask_path}")

        except Exception as e:
            print(f"[ERROR] Yüz tespiti ve maske düzenleme hatası: {str(e)}")
            self.status_var.set("Yüz tespiti hatası!")
            messagebox.showwarning("Uyarı", f"Yüz tespiti veya maske düzenleme sırasında bir hata oluştu: {str(e)}\nYine de devam ediliyor...")
            # Hata olsa bile maskenin mevcut haliyle devam eder

        self.status_var.set("Noktalar seçiliyor...")
        self.root.update()
        messagebox.showinfo("Nokta Seçimi", "Tişört üzerinde sırasıyla şu noktaları seçin (Seçimlerinizi mümkün olduğu kadar birbirinden uzakta ve belirtilen bölgelerde yapın.):\n1. Sol omuz\n2. Sağ omuz\n3. Bel ortası")
        print("[INFO] Tişört üzerindeki noktaları seçin")
        src_points = select_points(self.cloth_path, title="Tişört")
        cv2.destroyAllWindows() # Nokta seçimi pencerelerini kapatır
        cv2.waitKey(1) # Pencerenin kapanması için kısa bekleme süresi
        messagebox.showinfo("Bilgi", "Tişört üzerindeki noktalar seçildi!")

        self.status_var.set("Noktalar seçiliyor...")
        self.root.update()
        messagebox.showinfo("Nokta Seçimi", "Kişi üzerinde sırasıyla şu noktaları seçin (Seçimlerinizi mümkün olduğu kadar birbirinden uzakta ve belirtilen bölgelerde yapın.):\n1. Sol omuz\n2. Sağ omuz\n3. Bel ortası")
        print("[INFO] Kişi üzerindeki noktaları seçin")
        dst_points = select_points(current_person_path, title="Kişi")
        cv2.destroyAllWindows() # Nokta seçimi pencerelerini kapatır
        cv2.waitKey(1) # Pencerenin kapanması için kısa bekleme süresi
        messagebox.showinfo("Bilgi", "Kişi üzerindeki noktalar seçildi!")

        # Noktaların sırasını kontrol etmek için;
        if not self.validate_points(src_points, dst_points):
            messagebox.showerror("Hata", "Noktalar yanlış sırada seçildi. Lütfen tekrar deneyin.")
            self.status_var.set("Hata: Yanlış nokta sırası.")
            return

        os.makedirs("output", exist_ok=True)
        output_name = f"output/warped_{os.path.splitext(os.path.basename(self.cloth_path))[0]}_{os.path.splitext(os.path.basename(current_person_path))[0]}.png"
        print(f"[DEBUG] Çıktı dosyası: {output_name}")

        print(f"[DEBUG] Warp işlemi başlatılıyor...")
        print(f"[DEBUG] Tişört: {self.cloth_path}")
        print(f"[DEBUG] Kişi: {current_person_path}")
        print(f"[DEBUG] Mask: {mask_path}")

        self.status_var.set("Giydirme işlemi yapılıyor...")
        self.root.update()

        try:
            # Warp işlemini gerçekleştir (Affine transformasyon kullanılıyor)
            success = warp_cloth_from_points(self.cloth_path, current_person_path, output_name, src_points, dst_points)

            if not success:
                raise Exception("Warp işlemi başarısız oldu veya boş görsel döndürdü")

            # Çıktı dosyasının oluşturulduğunu kontrol et
            if not os.path.exists(output_name) or os.stat(output_name).st_size == 0:
                raise Exception("Çıktı dosyası oluşturulamadı veya boş.")

            self.last_output_path = output_name
            self.status_var.set("İşlem tamamlandı!")
            messagebox.showinfo("Başarılı", "Tişört başarıyla giydirildi!")

            # Başarılı olursa çıktıyı göstermek için;
            self.show_output(output_name)

        except Exception as e:
            print(f"[ERROR] Warp işlemi sırasında hata oluştu: {str(e)}")
            self.status_var.set("Hata oluştu!")
            messagebox.showerror("Hata", f"Tişört giydirme işlemi başarısız oldu: {str(e)}")
            return

        # cv2.destroyAllWindows() # Nokta seçimi dışındaki pencereler kapatılmamalı
        # cv2.destroyAllWindows()

    def validate_points(self, src_points, dst_points):
        # Nokta sayısı kontrolü (her iki listede de 3 nokta olmalı)
        if len(src_points) != 3 or len(dst_points) != 3:
            print("[DEBUG] Hata: Nokta sayısı yanlış")
            return False

        # Sol omuz sağ omuzdan daha solda olmalı
        if src_points[0][0] > src_points[1][0] or dst_points[0][0] > dst_points[1][0]:
            print("[DEBUG] Hata: Sol omuz sağ omuzdan daha sağda")
            return False

        # Omuz noktaları arasındaki mesafe kontrolü
        src_shoulder_distance = abs(src_points[0][0] - src_points[1][0])
        dst_shoulder_distance = abs(dst_points[0][0] - dst_points[1][0])
        
        # Omuz noktaları arasındaki mesafe çok yakın veya çok uzak olmamalı
        min_shoulder_distance = 50  # minimum omuz mesafesi
        if src_shoulder_distance < min_shoulder_distance or dst_shoulder_distance < min_shoulder_distance:
            print("[DEBUG] Hata: Omuz noktaları birbirine çok yakın")
            return False

        # Bel noktası kontrolü
        # Bel noktası omuz noktalarının altında olmalı
        if src_points[2][1] < max(src_points[0][1], src_points[1][1]) or \
           dst_points[2][1] < max(dst_points[0][1], dst_points[1][1]):
            print("[DEBUG] Hata: Bel noktası omuz noktalarının üstünde")
            return False

        # Bel noktası omuz noktalarından çok uzakta olmamalı
        max_vertical_distance = 300  # maksimum dikey mesafe
        if abs(src_points[2][1] - max(src_points[0][1], src_points[1][1])) > max_vertical_distance or \
           abs(dst_points[2][1] - max(dst_points[0][1], dst_points[1][1])) > max_vertical_distance:
            print("[DEBUG] Hata: Bel noktası omuz noktalarından çok uzakta")
            return False

        # Bel noktası omuz noktalarının orta noktasına yakın olmalı (yatay)
        src_shoulder_mid = (src_points[0][0] + src_points[1][0]) / 2
        dst_shoulder_mid = (dst_points[0][0] + dst_points[1][0]) / 2
        
        max_horizontal_offset = 50  # maksimum yatay sapma
        if abs(src_points[2][0] - src_shoulder_mid) > max_horizontal_offset or \
           abs(dst_points[2][0] - dst_shoulder_mid) > max_horizontal_offset:
            print("[DEBUG] Hata: Bel noktası omuzların orta noktasından çok uzakta")
            return False

        return True

    def show_output(self, output_path=None):
        print(f"[DEBUG] show_output çağrıldı, output_path: {output_path}")
        if output_path is None:
            output_dir = "output"
            print(f"[DEBUG] show_output parametresiz çağrıldı. Çıktı dizini aranıyor: {output_dir}")
            if not os.path.exists(output_dir):
                messagebox.showerror("Hata", "Henüz çıktı bulunamadı.")
                print(f"[DEBUG] Çıktı dizini bulunamadı: {output_dir}")
                return
            warped_files = [f for f in os.listdir(output_dir) if f.startswith("warped_") and f.endswith(".png")]
            if not warped_files:
                messagebox.showerror("Hata", "Henüz çıktı bulunamadı.")
                print("[DEBUG] Çıktı dizininde warped_*.png dosyası bulunamadı.")
                return
            output_path = os.path.join(output_dir, warped_files[-1])
            print(f"[DEBUG] Bulunan son çıktı dosyası: {output_path}")

        if not os.path.exists(output_path):
            print(f"[ERROR] Çıktı dosyası bulunamadı: {output_path}")
            messagebox.showerror("Hata", "Çıktı dosyası bulunamadı.")
            return

        # Eğer açık bir çıktı penceresi varsa kapat
        if self.output_window is not None and self.output_window.winfo_exists():
            self.output_window.destroy()

        try:
            # Yeni bir pencere oluştur
            self.output_window = tk.Toplevel(self.root)
            self.output_window.title("Giydirme Sonucu")

            # Görüntüyü yükle
            img = Image.open(output_path)

            # Pencere boyutuna sığdırmak için görseli yeniden boyutlandır (isteğe bağlı çalışır)
            max_size = 800
            width, height = img.size
            if width > max_size or height > max_size:
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            img_tk = ImageTk.PhotoImage(img)

            # Görüntüyü göstermek için Label oluştur
            output_label = ttk.Label(self.output_window, image=img_tk)
            output_label.image = img_tk 
            output_label.pack(padx=10, pady=10)

            self.status_var.set("Çıktı ayrı pencerede gösteriliyor.")

        except Exception as e:
            print(f"[ERROR] Çıktı ayrı pencerede gösterilirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Çıktı ayrı pencerede gösterilirken bir hata oluştu: {str(e)}")
            if self.output_window is not None and self.output_window.winfo_exists():
                self.output_window.destroy() # Hata olursa pencereyi kapat

if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualTryOnApp(root)
    root.mainloop()
