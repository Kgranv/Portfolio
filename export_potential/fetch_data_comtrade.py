import sys
import pandas as pd
import comtradeapicall
import requests

def get_api_key(filepath="api_key.txt") -> str:
    try:
        with open(filepath) as f:
            key = f.read().strip()
        if not key:
            raise ValueError(f"'{filepath}' is empty.")
        return key

    except FileNotFoundError:
        raise FileNotFoundError(f"'{filepath}' file is missing.")

def get_all_country() -> str:
    data = pd.read_parquet("./data/reporter.parquet")
    data = data[pd.isna(data["entryExpiredDate"])]
    country_list = data["id"].astype(str).to_list()
    
    return ",".join(country_list)

def fetch_data(api_key, product_code="TOTAL,260300", year="2025") -> pd.Dataframe:
    all_goods = "TOTAL," + product_code
    try:
        data = comtradeapicall.getFinalData(api_key, typeCode='C', freqCode='A', clCode='HS', period=year,
                                        reporterCode=get_all_country(), cmdCode=all_goods, flowCode='X', partnerCode='0',
                                        partner2Code=None,
                                        customsCode=None, motCode='0', maxRecords=2500, format_output='JSON',
                                        aggregateBy=None, breakdownMode='classic', countOnly=False, includeDesc=False)
        if not data:
            raise requests.exceptions.RequestException("Something went wrong with the request")
        return pd.DataFrame(data)

    except requests.exceptions.RequestException:
        raise requests.exceptions.RequestException("Something went wrong with the request")
    

def save_data(data, filepath="data/data.parquet") -> None:
    try: 
        data.to_parquet(filepath, engine='auto', compression='snappy', index=False)
        print(f"Data saved in file : '{filepath}'")
    except:
        raise ValueError(f"Unable to save data in '{filepath}'.")

def main():
    try:
        api_key = get_api_key()
        data = fetch_data(api_key)
        print(data.head())
        save_data(data)

    except FileNotFoundError as e:
        print(f"[File Error] {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"[API Error] {e}", file=sys.stderr)
        sys.exit(2) 
    except Exception as e:
        print(f"[Unexpected Error] {e}", file=sys.stderr)
        sys.exit(99)

if __name__ == "__main__":
    main()
