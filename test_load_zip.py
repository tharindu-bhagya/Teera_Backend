import keras
import os

MODEL_PATH = "d:/TEERA/backend_teera/cinnamon_model.keras"

print(f"Testing Keras version: {keras.__version__}")
if os.path.exists(MODEL_PATH):
    print(f"Loading ML model from {MODEL_PATH}...")
    try:
        disease_model = keras.models.load_model(MODEL_PATH)
        print("ML model loaded successfully.")
    except Exception as e:
        print(f"FAILED to load model: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"Model path {MODEL_PATH} does not exist.")
