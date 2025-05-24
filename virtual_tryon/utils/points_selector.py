# utils/points_selector.py
import cv2
import numpy as np

def select_points(image_path, title="Görsel"):
    points = []
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"[ERROR] Görsel bulunamadı: {image_path}")
    img = cv2.resize(img, (800, 600))

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 3:
            points.append((x, y))
            cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow(title, img)
            print(f"[{len(points)}] Nokta seçildi: ({x}, {y})")
            if len(points) == 3:
                print("3 nokta seçildi, pencere otomatik kapanacak.")
                cv2.destroyWindow(title)

    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.imshow(title, img)
    cv2.setMouseCallback(title, click_event)

    print("Lütfen sırayla 3 noktaya tıklayın (sol omuz, sağ omuz, bel ortası).")
    print("Noktaları seçtikten sonra pencere otomatik kapanacak.")

    while len(points) < 3:
        if cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) < 1:
            break
        cv2.waitKey(1)

    cv2.destroyAllWindows()

    if len(points) != 3:
        raise ValueError("❌ 3 nokta seçilmedi. Lütfen tekrar deneyin.")

    # Seçilen ve yeniden ölçeklenen noktaları yazdır
    print(f"[DEBUG] Seçilen ham noktalar (yeniden boyutlandırılmış görselde): {[(p[0], p[1]) for p in points]}")

    # Noktaları orijinal görsel boyutuna göre yeniden ölçekle
    original_width = cv2.imread(image_path).shape[1]
    original_height = cv2.imread(image_path).shape[0]
    scaled_points = []
    for p in points:
        scaled_x = int(p[0] * original_width / 800)
        scaled_y = int(p[1] * original_height / 600)
        scaled_points.append((scaled_x, scaled_y))
        
    print(f"[DEBUG] Yeniden ölçeklenen noktalar (orijinal görsel boyutunda): {scaled_points}")

    return np.float32(scaled_points)
