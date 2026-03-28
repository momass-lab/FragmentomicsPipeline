import pandas as pd
import numpy as np
import sys
import os
import gzip

def parse_bed(file_path):
    """
    Universally parse a BED format file.
    If the BED file lacks UW-DHO custom annotation columns (like Gene_Symbol),
    it degrades gracefully and only extracts coordinate metrics.
    """
    # Standard format: chr, start, end. The remaining are optional extensions.
    cols = ['chr', 'start', 'end', 'ENST_ID', 'RefSeq_ID', 'Gene_Symbol', 'score', 'strand']
    
    try:
        # Try to read standard columns. Ignore extra columns or missing columns.
        df = pd.read_csv(
            file_path, sep='\t', header=None,
            compression='gzip' if file_path.endswith('.gz') else None, 
            on_bad_lines='skip'
        )
        
        # Determine how many columns exist in this specific BED file
        num_cols = len(df.columns)
        actual_cols = cols[:num_cols]
        df.columns = actual_cols

        df['length'] = df['end'] - df['start']
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame(columns=['start', 'end', 'length'])

def extract_features(df, sample_name):
    """Extracts features dynamically based on available columns."""
    features = {'sample': sample_name}
    
    # Generic Label (assuming Prefix_1 type format like 'Bladder_1')
    target = sample_name.split('_')[0]
    if target.isdigit():
        target = "Unknown_Class"
    features['target'] = target

    total_frags = len(df)
    if total_frags == 0:
        return pd.DataFrame([features])

    # 1. Global Metrics (Available on ANY BED sequence)
    features['global_median_length'] = df['length'].median()
    features['global_mean_length'] = df['length'].mean()
    features['global_prop_short'] = (df['length'] < 150).sum() / total_frags
    features['global_prop_long'] = (df['length'] >= 150).sum() / total_frags

    # 2. Gene-level annotations (If available from custom panels or prior GTF intersections)
    if 'Gene_Symbol' in df.columns:
        df_annotated = df.dropna(subset=['Gene_Symbol'])
        if len(df_annotated) > 0:
            gene_counts = df_annotated['Gene_Symbol'].value_counts()
            gene_abundance = gene_counts / total_frags
            gene_lengths = df_annotated.groupby('Gene_Symbol')['length'].median()

            # Limit to 200 tops to prevent memory collapse
            top_genes = gene_abundance.head(200).index
            for gene in top_genes:
                features[f'abund_{gene}'] = gene_abundance[gene]
                features[f'medlen_{gene}'] = gene_lengths.get(gene, 0)
        
    return pd.DataFrame([features])

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python extract_features.py <input.bed> <output.csv>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    base_name = os.path.basename(input_file).replace('.bed.gz', '').replace('.bed', '')
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    df = parse_bed(input_file)
    feature_df = extract_features(df, base_name)
    feature_df.to_csv(output_file, index=False)
