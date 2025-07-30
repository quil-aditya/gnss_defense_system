# ai/spoof_classifier.py

import numpy as np
import joblib
import tensorflow as tf

class SpoofClassifier:
    def __init__(self, model_path="ai/model.tflite", scaler_path="ai/scaler.pkl"):
        # Load TFLite model
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # Get input/output tensor indices
        self.input_index = self.interpreter.get_input_details()[0]['index']
        self.output_index = self.interpreter.get_output_details()[0]['index']

        # Load StandardScaler
        self.scaler = joblib.load(scaler_path)

    def predict(self, input_features):
        """
        Parameters:
            input_features: list or array of [hdop, vdop, sats]
        
        Returns:
            float: predicted probability (0 = clean, 1 = spoofed)
        """
        features = np.array([input_features])  # Shape: (1, 3)
        scaled = self.scaler.transform(features).astype(np.float32)

        self.interpreter.set_tensor(self.input_index, scaled)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_index)
        return float(output[0][0])  # Return as scalar float
