import torch
import torch.nn.functional as F
import numpy as np
import cv2
from torchvision import transforms
from PIL import Image
from u2net_model import U2NET

MODEL_PATH = "models/u2net.pth"

transform = transforms.Compose([
    transforms.Resize((320, 320)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def predict_mask(model, image_tensor):
    with torch.no_grad():
        d0, *_ = model(image_tensor)
        pred = d0[:, 0, :, :]
        pred = (pred - pred.min()) / (pred.max() - pred.min())
        return pred.squeeze().cpu().numpy()

def visualize_segmentation(input_path, output_mask, output_segmented):
    image = cv2.imread(input_path)
    mask = cv2.imread(output_mask, cv2.IMREAD_GRAYSCALE)
    segmented = cv2.imread(output_segmented)

    cv2.imshow("Original Image", image)
    cv2.imshow("Segmentation Mask", mask)
    cv2.imshow("Segmented Image", segmented)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def run_segmentation(input_path="data/person.jpg", output_mask="output/mask.png", output_segmented="output/segmented.png"):
    print(f"[DEBUG] Segmentasyon başlatılıyor...")
    print(f"[DEBUG] Girdi dosyası: {input_path}")
    print(f"[DEBUG] Mask çıktı dosyası: {output_mask}")
    print(f"[DEBUG] Segmentasyon çıktı dosyası: {output_segmented}")

    model = U2NET(3, 1)
    model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
    model.eval()

    image = Image.open(input_path).convert('RGB')
    original_np = np.array(image)
    input_tensor = transform(image).unsqueeze(0)

    print("[INFO] Segmentasyon tahmini yapılıyor...")
    mask = predict_mask(model, input_tensor)
    mask_resized = cv2.resize(mask, (original_np.shape[1], original_np.shape[0]))

    cv2.imwrite(output_mask, (mask_resized * 255).astype(np.uint8))
    print(f"[DEBUG] Mask kaydedildi: {output_mask}")

    mask_3ch = cv2.merge([mask_resized] * 3)
    segmented = (original_np * mask_3ch).astype(np.uint8)
    cv2.imwrite(output_segmented, segmented)
    print(f"[DEBUG] Segmentasyon sonucu kaydedildi: {output_segmented}")

    print("[INFO] Segmentasyon tamamlandı.")
