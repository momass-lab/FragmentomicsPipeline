import pandas as pd
import numpy as np
import sys
import os
import yaml
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import xgboost as xgb

def train_and_evaluate(csv_path, output_dir, config_path):
    print(f"Loading data from {csv_path} and config from {config_path}")
    df = pd.read_csv(csv_path)

    # Parse config
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    baseline_class = config["machine_learning"]["baseline_class"]

    if 'target' not in df.columns:
        print("Missing target column needed for Machine Learning.")
        sys.exit(1)

    print(f"Class distribution:\n{df['target'].value_counts()}")

    # Dynamically separate Control vs Experimental classes
    df['label_binary'] = df['target'].apply(lambda x: 0 if x == baseline_class else 1)
    
    drop_cols = ['sample', 'target', 'label_binary']
    X = df.drop(columns=[col for col in drop_cols if col in df.columns])
    y = df['label_binary']

    if y.nunique() < 2:
        print(f"Not enough variation to train. Needs '{baseline_class}' and at least one other class.")
        sys.exit(0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    model = xgb.XGBClassifier(
        n_estimators=100, 
        max_depth=4, 
        learning_rate=0.1, 
        random_state=42,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    report = classification_report(y_test, y_pred, zero_division=0, target_names=[baseline_class, "Experimental"])
    print(report)

    # Main Driver Extraction
    importances = model.feature_importances_
    feat_imp = pd.DataFrame({
        'Feature': X.columns,
        'Importance': importances
    }).sort_values('Importance', ascending=False).head(20)

    os.makedirs(output_dir, exist_ok=True)
    
    # Plot feature importances
    plt.figure(figsize=(10, 8))
    sns.barplot(x='Importance', y='Feature', data=feat_imp)
    plt.title(f'Top 20 Main Fragmentomics Drivers (vs {baseline_class})')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'feature_importances.png'))
    plt.close()
    
    # Plot Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=[baseline_class, 'Experimental'], yticklabels=[baseline_class, 'Experimental'])
    plt.title(f'Confusion Matrix: Experimental vs {baseline_class}')
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
    plt.close()

    # Save the trained model for publication/deployment
    model.save_model(os.path.join(output_dir, 'fragmentomics_xgboost.json'))
    
    # Text Log
    with open(os.path.join(output_dir, "classification_log.txt"), "w") as f:
        f.write(f"Baseline Condition: {baseline_class}\n\n")
        f.write(report + "\n\n")
        f.write(feat_imp.to_string(index=False))

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python train_model.py <training_matrix.csv> <output_dir> <config.yaml>")
        sys.exit(1)
        
    csv_path = sys.argv[1]
    output_dir = sys.argv[2]
    config_path = sys.argv[3]
    train_and_evaluate(csv_path, output_dir, config_path)
