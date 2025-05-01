# ManiCrawl

This Python script uses Selenium to crawl the [Manipal University Library Portal](https://libportal.manipal.edu/MIT/Question%20Paper.aspx) and extract links to PDF question papers organized by year and subject.

## Features

- Recursively navigates year and subject folders
- Extracts all PDF links
- Saves results in structured JSON format
- Supports concurrent crawling for multiple years

## Requirements

- Python 3.7+
- Google Chrome
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) (compatible with your Chrome version)

## Installation

```bash
pip install selenium
```

Download and place the matching `chromedriver` in your PATH or the same directory as the script.

## Usage

```bash
python crawler.py
```

Collected PDF links will be saved in the `pdf_results/` folder as `{year}_pdfs.json`.

## Configuration

To crawl specific years, edit the `years` list in `main()`:

```python
years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
```

## GitHub Actions

You can automate crawling using GitHub Actions. Create a workflow file under `.github/workflows/` and define the trigger (manual or scheduled).

## Credits

Thanks to [Epicguest97/crawler](https://github.com/Epicguest97/crawler) for the original inspiration and code structure.

