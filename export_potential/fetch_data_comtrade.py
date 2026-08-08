import sys
import pandas as pd
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

def fetch_data(api_key) -> pd.Dataframe:
    data = {
    "data1": [420, 380, 390],
    "data2": [50, 40, 45]
    }
    df = pd.DataFrame(data)
    print(df.head())
    return df

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
