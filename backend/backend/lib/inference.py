"""
推理模块
"""

import torch
from torchvision import transforms
from PIL import Image
from pathlib import Path
from typing import Optional, Union, cast

from .model import get_model
from .config import MODELS_DIR, DEFAULT_IMAGE_SIZE, EuroSAT_CLASSES


class ImageClassifier:
    def __init__(self, model_key: str, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_key = model_key

        model_path = MODELS_DIR / model_key / "best_model.pth"
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        self.model = get_model(model_key, num_classes=10)
        self.model.load_state_dict(
            torch.load(model_path, map_location=self.device, weights_only=True)
        )
        self.model.to(self.device)
        self.model.eval()

        self.transform: transforms.Compose = transforms.Compose(
            [
                transforms.Resize((DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    def predict(self, image_path: str):
        image = Image.open(image_path).convert("RGB")
        transformed = self.transform(image)
        image_tensor = torch.unsqueeze(transformed, 0).to(self.device)

        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            predicted_class = outputs.argmax(1).item()
            confidence = probabilities[0][predicted_class].item()

        return {
            "class": EuroSAT_CLASSES[predicted_class],
            "class_id": predicted_class,
            "confidence": round(confidence, 4),
            "all_probabilities": {
                EuroSAT_CLASSES[i]: round(probabilities[0][i].item(), 4)
                for i in range(len(EuroSAT_CLASSES))
            },
        }

    def predict_batch(self, image_paths: list):
        results = []
        for path in image_paths:
            results.append(self.predict(path))
        return results


def load_all_models():
    classifiers = {}
    for model_key in ["efficientnet_b0", "swin_tiny", "swin_tiny_feature"]:
        try:
            classifiers[model_key] = ImageClassifier(model_key)
        except FileNotFoundError:
            print(f"Warning: Model {model_key} not found, skipping...")
    return classifiers
