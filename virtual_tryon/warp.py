import cv2
import numpy as np

def warp_cloth_from_points(cloth_path, person_path, output_path, src_points, dst_points):
    cloth = cv2.imread(cloth_path, cv2.IMREAD_UNCHANGED)
    person = cv2.imread(person_path)
    mask = cv2.imread("output/mask.png", cv2.IMREAD_GRAYSCALE)

    if cloth is None or person is None or mask is None:
        print("[ERROR] Görseller yüklenemedi.")
        return False

    M = cv2.getAffineTransform(src_points, dst_points)
    warped = cv2.warpAffine(cloth, M, (person.shape[1], person.shape[0]), borderMode=cv2.BORDER_TRANSPARENT, flags=cv2.INTER_LANCZOS4)

    if cloth.shape[2] == 4:
        alpha = warped[:, :, 3] / 255.0
    else:
        gray = cv2.cvtColor(warped[:, :, :3], cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(gray, 1, 1, cv2.THRESH_BINARY)

    mask_normalized = mask.astype(np.float32) / 255.0
    alpha = alpha.astype(np.float32)
    combined_alpha = np.clip(alpha * mask_normalized, 0, 1)

    for c in range(3):
        person[:, :, c] = (1 - combined_alpha) * person[:, :, c] + combined_alpha * warped[:, :, c]

    success = cv2.imwrite(output_path, person)
    if not success:
        print(f"[ERROR] Çıktı dosyası kaydedilemedi: {output_path}")
        return False

    print(f"[INFO] Giydirilmiş çıktı kaydedildi: {output_path}")
    return True

def warp_cloth_tps(cloth_path, person_path, output_path, src_points, dst_points):
    print(f"[DEBUG] warp_cloth_tps - src_points: {src_points}, shape: {src_points.shape}")
    print(f"[DEBUG] warp_cloth_tps - dst_points: {dst_points}, shape: {dst_points.shape}")

    try:
        cloth = cv2.imread(cloth_path, cv2.IMREAD_UNCHANGED)
        person = cv2.imread(person_path)
        mask = cv2.imread("output/mask.png", cv2.IMREAD_GRAYSCALE)

        if cloth is None:
            raise Exception(f"Tişört görseli yüklenemedi: {cloth_path}")
        if person is None:
            raise Exception(f"Kişi görseli yüklenemedi: {person_path}")
        if mask is None:
            raise Exception("Segmentasyon maskesi yüklenemedi: output/mask.png")

        if not isinstance(src_points, np.ndarray) or not isinstance(dst_points, np.ndarray):
            raise Exception("Noktalar numpy dizisi formatında olmalı")
        if src_points.shape != (3, 2) or dst_points.shape != (3, 2):
            raise Exception("Her iki görsel için de tam olarak 3 nokta (3x2 matris) gerekli")

        tps = cv2.createThinPlateSplineShapeTransformer()
        src_points_tps = src_points.reshape(-1, 1, 2)
        dst_points_tps = dst_points.reshape(-1, 1, 2)
        
        print(f"[DEBUG] estimateTransformation - src_points_tps: {src_points_tps}, shape: {src_points_tps.shape}")
        print(f"[DEBUG] estimateTransformation - dst_points_tps: {dst_points_tps}, shape: {dst_points_tps.shape}")

        matches = [cv2.DMatch(i, i, 0) for i in range(len(src_points))]
        tps.estimateTransformation(dst_points_tps, src_points_tps, matches)

        warped_cloth = np.zeros((person.shape[0], person.shape[1], cloth.shape[2]), dtype=cloth.dtype)
        
        print(f"[DEBUG] warpImage öncesi - cloth shape: {cloth.shape}, warped_cloth shape: {warped_cloth.shape}")
        
        tps.warpImage(cloth, warped_cloth, cv2.INTER_LINEAR, cv2.BORDER_TRANSPARENT)

        cv2.imwrite("output/debug_warped_cloth.png", warped_cloth)
        print("[DEBUG] Geçici warped görsel kaydedildi: output/debug_warped_cloth.png")

        if np.all(warped_cloth == 0):
            print("[ERROR] Warp işlemi sonucunda dönüştürülmüş görsel boş.")
            raise Exception("Warp işlemi boş bir görsel üretti.")

        if cloth.shape[2] == 4:
            alpha = warped_cloth[:, :, 3] / 255.0
        else:
            gray = cv2.cvtColor(warped_cloth[:, :, :3], cv2.COLOR_BGR2GRAY)
            _, alpha = cv2.threshold(gray, 1, 1, cv2.THRESH_BINARY)

        mask_normalized = mask.astype(np.float32) / 255.0
        alpha = alpha.astype(np.float32)
        combined_alpha = np.clip(alpha * mask_normalized, 0, 1)

        cv2.imwrite("output/debug_combined_alpha.png", (combined_alpha * 255).astype(np.uint8))
        print("[DEBUG] Geçici combined alpha maskesi kaydedildi: output/debug_combined_alpha.png")

        result = person.copy()
        for c in range(3):
            result[:, :, c] = (1 - combined_alpha) * person[:, :, c] + combined_alpha * warped_cloth[:, :, c]

        print(f"[DEBUG] Çıktı dosyası kaydediliyor: {output_path}")
        success = cv2.imwrite(output_path, result)
        if not success:
            raise Exception(f"Çıktı dosyası kaydedilemedi: {output_path}")

        print(f"[INFO] Giydirilmiş çıktı kaydedildi: {output_path}")
        return True

    except Exception as e:
        print(f"[ERROR] Warp işlemi sırasında hata oluştu: {str(e)}")
        return False
