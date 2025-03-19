# Report Generation Agent

Run with `python main.py YYYY-MM-DD`.

Results saved in `test_results/{date}/`.

## Detailed Files Overview

- `keys.py`: store the API keys.
- `main_utils.py`: utility functions for supporting data processing and report generation.
- `plot_utils.py`: generate images to analyze X data.
- `prompt.py`: prompts to used analyze data.
- `research_report_generation.py`: prompts used to generate report sections from data analysis.
- `models.py`: functions to call models API.
- `generate_LPR_analysis.py`: generate LPR analysis part.
- `generate_news_analysis.py`: generate news analysis part.
- `generate_report_images.py`: generate the following report images: LPR hist trend, terms words cloud, words sentiment, xx and xy correlation heatmaps.
- `reflection.py`: reflection agent used to correct report results from previous feedbacks.

