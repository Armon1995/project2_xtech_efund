# Project 2: Loan Prime Rate Prediction and Report Generation Using Large Language Models from Time-Series and Textual Data 

## Required Version
- `python>=3.10`

**Note**: if **not** using Efund models, `python>=3.8` will also work. However `python>=3.10` is recommended.

## Installation

Install dependencies with `pip install -r requirements.txt`.

To use Efund models, install `luluai` with the following command:
```
pip install -U lulu-ai -i https://python-public-1659087108189:4b3c57f36e7d7bef2bf1e43966dddbf6fd464a22@devops-pypi.pkg.coding.dev.efunds.com.cn/public-artifact-repo/python-public/simple
```

Write your API keys in `data_retrieval/keys.py` and `report_generation/keys.py`.
The following API keys are required:
- Efund (required)

Next steps do to only if using news from 易方达 database (both no needed).
- Modify S3 config in `data_retrieval/yifangda_news/retrieve_s3_news.py`.
- Modify news database config in `data_retrieval/yifangda_news/retrieve_news_db.py`.

## Report Generation

Run report generation with
```
cd report_generation
python main.py YYYY-MM-DD
```

Change `YYYY-MM-DD` with the dates we want to generate the report.
For example: `python main.py 2024-01-01 2024-02-01 2024-03-01` generates reports for 2024-01, 2024-02, 2024-03.
Predictions are based on the next month, for example the report generated for date 2024-01-01 will predict month 2024-02-01.

Results saved in `report_generation/test_results/{date}/`. Where `date` is the date of the generated report.
The final generated Word report is called `report_generation/test_results/{date}_report.docx`, other generated files can be ignored.

## Quick Run

To sum up, once the environment is ready you can update data and generate report with:
```
cd ../report_generation
python main.py YYYY-MM-DD
```
