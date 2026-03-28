import pandas as pd
import sys
import glob
import os

def main(input_dir, output_file):
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    if not csv_files:
        sys.exit(1)
        
    df_list = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            df_list.append(df)
        except:
            pass
            
    master_df = pd.concat(df_list, ignore_index=True)
    master_df = master_df.fillna(0)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    master_df.to_csv(output_file, index=False)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(1)
        
    input_dir = sys.argv[1]
    output_file = sys.argv[2]
    main(input_dir, output_file)
