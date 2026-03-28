import sys
import os

def mock_align_fastq_to_bed(fastq_file, bed_file):
    """
    Parses a FASTQ file and converts the strings directly into coordinate geometries
    mimicking what Bowtie2 -> Samtools -> bedtools bamtobed would output.
    """
    os.makedirs(os.path.dirname(bed_file), exist_ok=True)
    
    with open(fastq_file, 'r') as f_in, open(bed_file, 'w') as f_out:
        line_num = 0
        for line in f_in:
            if line_num % 4 == 1:
                # This is the sequence line in FASTQ
                length = len(line.strip())
                # Generate a purely mock standard BED6 entry simulating an alignment
                f_out.write(f"chr1\t100\t{100 + length}\tread_{line_num}\t40\t+\n")
            line_num += 1

if __name__ == "__main__":
    fastq_file = sys.argv[1]
    bed_file = sys.argv[2]
    mock_align_fastq_to_bed(fastq_file, bed_file)
