"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Utils functions to create dataset
"""
import statsmodels.api as sm
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def setup_chrome_driver() -> webdriver.Chrome:
    """
    Sets up the Chrome WebDriver with the necessary options.

    Returns:
        webdriver.Chrome: The configured Chrome WebDriver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def retry(func, max_attempts=5, wait_seconds=10, *args, **kwargs):
    """Retry a function up to max_attempts times before giving up.

    Args:
        func (callable): The function to execute.
        max_attempts (int): Maximum number of attempts.
        wait_seconds (int): Wait time between attempts in seconds.
        *args: Positional arguments to pass to func.
        **kwargs: Keyword arguments to pass to func.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)  # Execute with arguments
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                print(f"Retrying in {wait_seconds} seconds...")
                time.sleep(wait_seconds)
            else:
                print(f"Failed after {max_attempts} attempts. Skipping.")
                return None  # Indicate failure


def add_taylor_indicator(df, lamb=100):
    """
    Computes the Taylor Rule-based interest rate and potential GDP using the HP filter.

    Parameters:
    - df (pd.DataFrame): DataFrame containing 'China_GDP' and 'China_Inflation'.
    - lamb (int): Smoothing parameter for the HP filter (default is 100 for quarterly data).

    Returns:
    - pd.DataFrame: Updated DataFrame with 'Potential_GDP' and 'TR_Interest_Rate' columns.
    """
    # target_inflation = 0.02  # 2% target inflation
    # real_interest_rate = 0.01  # 1% equilibrium real interest rate

    # Function to calculate interest rate based on the Taylor Rule
    def taylor_rule(actual_gdp, inflation_rate, potential_gdp, target_inflation=0.02, r_star=0.01):
        """
        Calculate the Taylor Rule interest rate.

        Parameters:
        - actual_gdp (float): Actual GDP value.
        - inflation_rate (float): Inflation rate (as a decimal).
        - potential_gdp (float): Estimated potential GDP.
        - target_inflation (float, optional): Target inflation rate (default 2%).
        - r_star (float, optional): Real neutral interest rate (default 1%).

        Returns:
        - float: Predicted interest rate based on the Taylor Rule.
        """
        return r_star + inflation_rate + 0.5 * (inflation_rate - target_inflation) + 0.5 * (actual_gdp - potential_gdp) / potential_gdp

    # Apply HP Filter to compute potential GDP
    # Lambda for quarterly data: 1600
    # Lambda for quarterly data: 100
    cycle, potential_gdp = sm.tsa.filters.hpfilter(df['China_GDP'], lamb=lamb)
    df['Potential_GDP'] = potential_gdp
    # Calculate the interest rate using the Taylor Rule (TR)
    df['TR_Interest_Rate'] = df.apply(
        lambda row: taylor_rule(row['China_GDP'], row['China_Inflation'], row['Potential_GDP']), axis=1
    )
    return df


def add_short_long_bond_spread(df):
    """
    Adds the bond spread (10-year yield minus 1-year yield) to the DataFrame.

    Parameters:
    - df (pd.DataFrame): DataFrame containing bond yield data.

    Returns:
    - pd.DataFrame: Updated DataFrame with 'Bond_Spread' column.
    """
    df['Bond_Spread'] = df['国债到期收益率:10年'] - df['国债到期收益率:1年']
    return df


def close_advertisement_eastmoney(driver, sleep_time=1):
    """
    Checks if the advertisement appears and closes it before scraping.
    """
    try:
        close_button = driver.find_element(By.XPATH, "//img[@src='https://emcharts.dfcfw.com/fullscreengg/ic_close.png']")
        close_button.click()
        time.sleep(sleep_time)  # Allow time for ad to close
    except Exception:
        pass  # If the ad is not found, continue normally
