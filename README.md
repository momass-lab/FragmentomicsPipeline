# Universal Fragmentomics Pipeline

This repository provides an End-to-End Snakemake workflow designed to extract and analyze **RNA** or **cfDNA** fragmentomics features. By feeding raw or annotated sequencing fragments, this pipeline automatically constructs a highly interpretable Machine Learning classifier to discover primary biomarker drivers defining different conditions.

---

## 🔬 Core Theory & Pipeline Steps

Unlike standard RNA-seq which relies primarily on counting overlapping read depth (abundance) over complete genes, **Fragmentomics** relies heavily on analyzing the exact geometric footprint of fragments. Different biological processes (e.g., RNA degradation via specific ribonucleases or cfDNA fragmentation between nucleosomes) leave explicit length and endpoint signatures.

### Pipeline Workflow:
1. **Multi-Mapping Resolution (Phase 1)**: If provided raw raw unmapped reads (`.fastq`), the pipeline uses custom indexing rules to align against structural RNAs (tRNAs/snoRNAs). This resolves "multi-mapping" issues (where a tiny fragment perfectly matches multiple identical tRNA genes).
2. **Dynamic Format Conversion (Phase 2)**: Standard binary alignment files (`.bam`) are naturally converted into mapped coordinate sets (`.bed`).
3. **Feature Extraction (Phase 3)**: Utilizing Python, the pipeline iteratively tears through files, pulling out descriptive global metrics (*Median Fragment lengths*, *Short-to-Long Ratios*) and gene-level abundances.
4. **Machine Learning Classifier (Phase 4)**: The generated `nSamples × nFeatures` matrix runs through an XGBoost binary classifier (differentiating an Experimental class from a configured Baseline class). The output definitively highlights the "main driver" features using Gini Importance methodologies.

---

## 🛠 Installation

You can install all dependencies cleanly via Conda, preventing software conflicts:

```bash
conda env create -f envs/environment.yml
conda activate fragmentomics_env
```

---

## ⚙️ Configuration (`config.yaml`)

This pipeline is universally parameterized. You can plug in any dataset (FASTQ, BAM, or BED strings) by simply modifying your `config.yaml`:

```yaml
directories:
  input: "data/raw_bed"   # Name of the folder containing your input data
  output: "results"       
  ml_output: "ml_output"  

pipeline:
  input_type: "bed"       # Set to "fastq", "bam", or "bed"

machine_learning:
  baseline_class: "Normal" # The prefix defining your control class (e.g. "Healthy")
```

---

## 🚀 Running the Pipeline

1. Place your target files into the directory identified by `config.yaml` $\rightarrow$ `directories:input`.
2. Ensure filenames contain class prefixes (e.g. `Normal_1.bed`, `Prostate_2.bed`) to allow the ML model to understand the targets automatically.
3. Because the extraction logic is heavy, execute utilizing parallel multi-threading processing via Python:

```bash
python -m snakemake --cores all
```

Output matrices and ML visual interpretation plots (ROC-AUC metrics, Top 20 Feature Importance rankings) will populate natively under the `ml_output/` folder!

---

## 📚 Citations & Data Source
The cfDNA Fragmentomics Metrics data used to develop and thoroughly test the robustness of this parameter-driven pipeline originates from:
- **Paper**: *Comprehensive Analysis of cfDNA Fragmentomics Metrics and Commercial Targeted Sequencing Panels* (Nature Communications, 2025). [DOI/Link to Paper](https://www.nature.com/articles/s41467-025-64153-z)
- **Data (FigShare)**: [10.6084/m9.figshare.28611500](https://doi.org/10.6084/m9.figshare.28611500)
- **Original Code**: [Zhao-Lab-UW-DHO/fragmentomics_metrics](https://github.com/Zhao-Lab-UW-DHO/fragmentomics_metrics)

---

## 📖 Interpreting Output (Afterword)
If you are new to clinical omics and machine learning or simply wondering what the XGBoost output means biologically, please read the [**Results Afterword & Interpretation Guide**](./RESULTS_AFTERWORD.md) for a plain-language extrapolation of why fragment geometries predict disease states using these exact datasets.
