import sys
import pandas as pd
import xgboost as xgb

def predict_new_samples(model_path, new_data_csv):
    """
    Loads a pre-trained Fragmentomics XGBoost model and predicts the class of new, unseen samples.
    """
    print(f"Loading published Fragmentomics Model from: {model_path}...")
    
    # 1. Load the Published Model
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    
    # 2. Load the New Data (Must be processed by the fragmentomics pipeline first into a CSV)
    print(f"Loading new patient geometries from: {new_data_csv}...")
    df = pd.read_csv(new_data_csv)
    
    # Keep the sample names for the final report
    sample_names = df['sample'].values if 'sample' in df.columns else [f"Sample_{i}" for i in range(len(df))]
    
    # Drop non-numeric metadata (like 'sample' and 'target' if present)
    X_new = df.drop(columns=['sample', 'target'], errors='ignore')
    
    # Ensure missing dimensions are 0 (XGBoost handles sparsity natively, but we align with our training logic)
    X_new = X_new.fillna(0)
    
    # 3. Predict! (1 = Experimental/Cancer/Autoimmune, 0 = Baseline/Healthy)
    print("\n--- CLINICAL PREDICTIONS ---")
    predictions = model.predict(X_new)
    probabilities = model.predict_proba(X_new)[:, 1] # Probability of being the Experimental class
    
    for i in range(len(predictions)):
        class_label = "EXPERIMENTAL / ABNORMAL" if predictions[i] == 1 else "BASELINE / HEALTHY"
        confidence = probabilities[i] * 100
        print(f"[{sample_names[i]}] -> {class_label} (Confidence: {confidence:.1f}%)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python predict_sample.py <path_to_model.json> <path_to_new_features.csv>")
        sys.exit(1)
        
    model_file = sys.argv[1]
    new_csv = sys.argv[2]
    
    predict_new_samples(model_file, new_csv)
