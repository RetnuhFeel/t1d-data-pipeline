# Type 1 Diabetes Synthetic Data Pipeline

This project simulates a complete end-to-end data pipeline for analyzing Type 1 Diabetes (T1D) data, using **synthetic continuous glucose monitoring (CGM)** and **insulin pump** records. It demonstrates real-world data workflows, predictive modeling, and pipeline automation — ideal for showcasing data science skills.

---

## 🔧 Project Features

- 🧬 **Synthetic biomedical data generation** (CGM + insulin + carbs)
- 🧹 **Preprocessing** of timestamped physiological data
- 🧠 **Feature engineering** of time-in-range, hypo/hyperglycemic events, daily aggregates
- 📈 **Modeling script** to predict glucose 30 minutes ahead using regression
- 🖥 **Command-line pipeline automation** with `argparse`
- 📓 **Jupyter notebooks** for visualization and exploration

---

## 🗂 Project Structure

```
t1d-data-pipeline/
│
├── data/
│   ├── raw/                 # Raw synthetic data (CGM, insulin)
│   ├── processed/           # Cleaned, timestamp-aligned datasets
│   └── features/            # Daily aggregate features
│
├── models/                  # Glucose prediction outputs
│
├── notebooks/
│   ├── 01_data_generation.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_modeling_and_prediction.ipynb
│
├── scripts/
│   ├── generate_and_preprocess_synthetic.py
│   ├── feature_engineering.py
│   ├── modeling.py
│   └── run_pipeline.py
│
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run the Full Pipeline

```bash
python scripts/run_pipeline.py
```

---

## ⚙️ CLI Options

You can customize the pipeline with command-line arguments:

```bash
# Run pipeline for a different subject ID
python scripts/run_pipeline.py --subject 002

# Skip the modeling step
python scripts/run_pipeline.py --skip-model

# Preview steps without execution
python scripts/run_pipeline.py --dry-run
```

---

## 📊 Engineered Features

From CGM + insulin logs, the pipeline computes:
- Average, min, max glucose per day
- Time-in-range (% in 70–180 mg/dL)
- Hypoglycemia & hyperglycemia events
- Total daily insulin + carb intake

---

## 📈 Modeling: 30-Min Ahead Glucose Prediction

- Model: Linear Regression  
- Target: `glucose_t+30min`  
- Features: `glucose_t`, `insulin_last30min`, `carbs_last30min`  
- Output: RMSE, actual vs. predicted plots  
- Saved to: `/models/{subject}_glucose_predictions.csv`

---

## 📓 Notebooks

Interactive notebooks to explore:
1. Data generation & visualization
2. Daily summary statistics
3. Predictive model results (actual vs. predicted)

---

## ✅ Requirements

Install required packages:

```bash
pip install -r requirements.txt
```

---

## 📄 License

This project is released under the MIT License.