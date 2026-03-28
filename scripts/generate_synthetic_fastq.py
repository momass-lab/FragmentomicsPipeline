import os
import random

def generate_fastq(filename, mean_length, num_reads=500):
    """
    Generates a synthetic FASTQ file containing fake short-read sequences.
    Simulates underlying fragmentation biology by drawing from a normal distribution around the mean_length.
    """
    bases = ['A', 'C', 'G', 'T']
    with open(filename, 'w') as f:
        for i in range(num_reads):
            # Normally distributed read lengths, bounding it mathematically.
            length = max(30, int(random.gauss(mean_length, 25)))
            
            # 1. Header Line
            f.write(f"@SEQ_ID_{i}_length_{length}\n")
            # 2. Sequence Line (mock random DNA)
            seq = ''.join(random.choices(bases, k=length))
            f.write(f"{seq}\n")
            # 3. Plus Line
            f.write("+\n")
            # 4. Quality Line (arbitrary high quality "I" == Q40)
            f.write("I" * length + "\n")

if __name__ == "__main__":
    out_dir = "data/synthetic_fastq"
    os.makedirs(out_dir, exist_ok=True)
    
    # Generate 15 Healthy (Regular nucleosomal cfDNA fragments)
    for i in range(1, 16):
        generate_fastq(os.path.join(out_dir, f"Healthy_{i}.fastq"), mean_length=166)
        
    # Generate 15 Autoimmune (Shorter, more chaotic fragments due to elevated cell death metrics)
    for i in range(1, 16):
        generate_fastq(os.path.join(out_dir, f"Autoimmune_{i}.fastq"), mean_length=135)

    print(f"Generated 30 synthetic `.fastq` samples in {out_dir}")
