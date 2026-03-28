import glob
import os
import yaml

# ----------------------------------------------------
# 1. Configuration Parsing
# ----------------------------------------------------
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

INPUT_DIR = config["directories"]["input"]
INPUT_TYPE = config["pipeline"]["input_type"]
OUT_DIR = f"{config['directories']['output']}_{INPUT_TYPE}"
ML_DIR = f"{config['directories']['ml_output']}_{INPUT_TYPE}"

# Gather Inputs based on configured format
if INPUT_TYPE == "bed":
    FILES = glob.glob(os.path.join(INPUT_DIR, "*.bed*"))
elif INPUT_TYPE == "bam":
    FILES = glob.glob(os.path.join(INPUT_DIR, "*.bam"))
elif INPUT_TYPE == "fastq":
    FILES = glob.glob(os.path.join(INPUT_DIR, "*.fastq*"))
else:
    FILES = []

SAMPLES = [os.path.basename(f).split('.')[0] for f in FILES]

# Prevent empty expansion breaking DAG on test setups
if not SAMPLES:
    SAMPLES = ["test_sample"]

# ----------------------------------------------------
# 2. Main Target Graph execution
# ----------------------------------------------------
ALL_INPUTS = [
    os.path.join(ML_DIR, "feature_importances.png"),
    os.path.join(ML_DIR, "confusion_matrix.png")
]

if INPUT_TYPE == "fastq":
    ALL_INPUTS.append("reference/rRNA_tRNA_index.done")

rule all:
    input:
        ALL_INPUTS

# ----------------------------------------------------
# 3. FASTQ Multi-Mapping Rules (Structural RNA support)
# ----------------------------------------------------
rule build_custom_index:
    """Uses Python standard library os.makedirs preventing Windows cmd.exe failures"""
    output:
        "reference/rRNA_tRNA_index.done"
    run:
        os.makedirs("reference", exist_ok=True)
        with open(output[0], "w") as f:
            f.write("Specialized custom multi-mapping index ready!\n")

rule align_multi_map:
    """Mocks tracking multi-mapping RNA species before BED extraction"""
    input:
        "reference/rRNA_tRNA_index.done",
        # Mocking finding corresponding fastq files
        fastq = f"{INPUT_DIR}/{{sample}}.fastq"
    output:
        f"{INPUT_DIR}/{{sample}}.bam"
    shell:
        """
        echo "Placeholder: Would align FASTQ to BAM with multi-mapping enabled..." > {output}
        """

# ----------------------------------------------------
# 4. BAM Format Rule (Dynamic Route)
# ----------------------------------------------------
rule convert_bam_to_bed:
    input:
        bam=f"{INPUT_DIR}/{{sample}}.bam",
        fastq=f"{INPUT_DIR}/{{sample}}.fastq"
    output:
        f"{INPUT_DIR}/{{sample}}.bed"
    shell:
        'python scripts/mock_align.py "{input.fastq}" "{output}"'

# ----------------------------------------------------
# 5. Core Feature Extraction (Any BED source)
# ----------------------------------------------------
def get_bed_input(wildcards):
    if INPUT_TYPE == "bed":
        for f in FILES:
            if wildcards.sample in os.path.basename(f):
                return f
    return f"{INPUT_DIR}/{wildcards.sample}.bed"

rule extract_features:
    input:
        get_bed_input
    output:
        f"{OUT_DIR}/features/{{sample}}.csv"
    shell:
        'python scripts/extract_features.py "{input}" "{output}"'

rule combine_features:
    input:
        # Collects extracted features only for successfully parsed input SAMPLES
        expand(f"{OUT_DIR}/features/{{sample}}.csv", sample=SAMPLES)
    output:
        f"{OUT_DIR}/training_matrix.csv"
    shell:
        'python scripts/combine_features.py "{OUT_DIR}/features" "{output}"'

# ----------------------------------------------------
# 6. Biomarker Classification (ML)
# ----------------------------------------------------
rule train_ml_model:
    input:
        f"{OUT_DIR}/training_matrix.csv"
    output:
        f"{ML_DIR}/feature_importances.png",
        f"{ML_DIR}/confusion_matrix.png"
    shell:
        'python scripts/train_model.py "{input}" "{ML_DIR}" "config.yaml"'
