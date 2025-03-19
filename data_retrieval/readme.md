# Automatic Data Retrieval

Run with `python retrieve_all_data.py`.

Data saved in `data/` and `yifangda_news`.

## Detailed Files Overview

- `create_X_dataset.py`: Generates timeseries dataset containing X variables and Y.
- `faiss_db_generate.py`: Generate FAISS database from news articles.
- `faiss_db_update.py`: Update FAISS database from news articles.
- `faiss_db_utils.py`: Do search on FAISS database.
- `keys.py`: Store API keys.
- `retrieve_all_data.py`: Create full dataset.
- `utils.py`: Utils functions to create dataset and scrape data.
- `scrape_{data_type}.py`: Scrape all kind of data based on `{data_type}`

## Detailed Folders Overview

- `data/`: Contains all the data used by the agent to generate reports.
- `faiss_db/`: Stores the Vector DB used for Retrieval-Augmented Generation (RAG).
- `data_media/`: Contains framework pipeline images, and data cards.
- `notebook/`: Includes experimental and analytical notebooks. These can be ignored unless you want to explore further analysis.
- `yifangda_news/`: Code relatives to retrieval news from 易方达 database.

The data is stored in the following way:

- **Timeseries Data**: Stored in `data/XY_aug_feat.csv`.
- **News Data**: Stored in files named `data/news_{source}.csv`, where `{source}` corresponds to the data source.
- **Meeting Reports**: The following CSV files contain meeting reports:
    - `data/中央银行会议报告.csv` (Central Bank Meeting Reports)
    - `data/政治局会议.csv` (Politburo Meeting Reports)
    - `data/政策货币报告.csv` (Monetary Policy Reports)
- **易方达 News**: Stored in `yifangda_news/通联宏观类舆情的表.csv`.

For a comprehensive analysis of the data, refer to **`EDA_X.ipynb`**.

## Adding Custom Data

### Custom X timeseries data

- Add your custom timeseries data csv file in `data/`. Refer to `data/X_data_Fred.csv` for data format.
- Suppose your file is called `X_data_custom.csv`, the file should be in `data/X_data_custom.csv`.
- In line 49 of `retrieve_all_data.py` add your csv file to the function `merge_csv_files`:
  ```
  merge_csv_files('data/X_data_Fred.csv', 'data/X_data_iFind.csv', 'data/M1_M2_data.csv',
                  'data/ppi_data.csv', 'data/XY_aug_feat.csv', `data/X_data_custom.csv`)
  ```

### Custom news data

- Add your custom news data csv file in `data/`. Refer to `data/news_wind.csv` for data format.
- Suppose your file is called `news_data_custom.csv`, the file should be in `data/news_data_custom.csv`.
- In line 19 of `faiss_db_generate.py` add your csv file to the list `news_files`:
  ```
  news_files = [
      'news_xinhua_政策执行.csv', 'news_xinhua_银行.csv', 'news_xinhua_LPR.csv', 'news_xinhua_债券.csv',
      'news_xinhua_利率.csv', 'news_xinhua_general.csv', 'news_wind.csv', 'news_eastmoney.csv',
      'news_data_custom.csv'
  ]
  ```

