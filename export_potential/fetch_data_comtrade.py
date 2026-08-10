import sys
import pandas as pd
import comtradeapicall
import requests
import time

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

def fetch_data(api_key, product_code="260300", year="2025", reporterCode = None) -> pd.DataFrame:
    all_goods = "TOTAL," + product_code
    if reporterCode is None:
        country = get_all_country()
        partnerCode = "0"
    else:
        country = reporterCode
        partnerCode = get_all_country()
        
    try:
        data = comtradeapicall.getFinalData(api_key, typeCode='C', freqCode='A', clCode='HS', period=year,
                                        reporterCode=country, cmdCode=all_goods, flowCode='X', partnerCode=partnerCode,
                                        partner2Code=None,
                                        customsCode=None, motCode='0', maxRecords=2500, format_output='JSON',
                                        aggregateBy=None, breakdownMode='classic', countOnly=False, includeDesc=False)

        if isinstance(data, pd.DataFrame):
            if data.empty:
                raise requests.exceptions.RequestException(
                    "No data returned with the request"
                )
            return data

        if data is None or len(data) == 0:
            raise requests.exceptions.RequestException(
                "No data returned with the request"
            )
        return pd.DataFrame(data)

    except requests.exceptions.RequestException:
        raise requests.exceptions.RequestException("Something went wrong with the request")
    

def save_data(data, filepath="./data/data.parquet") -> None:
    try: 
        data.to_parquet(filepath, engine='auto', compression='snappy', index=False)
        print(f"Data saved in file : '{filepath}'")
    except:
        raise ValueError(f"Unable to save data in '{filepath}'.")

def main():
    try:
        api_key = get_api_key()
        
        # For world data
        # cmdCode_Dict = {"260300":"COPPER","180100":"COCOA","282520":"LITHIUM","270900":"OILS","4403":"WOOD","110100":"WHEAT"} 
        # reporterCode_Dict = None # None for all country
        
        # For oils
        # cmdCode_Dict = {"270900":"OILS"} 
        # reporterCode_Dict = {682: 'SAU', 784: 'ARE', 124: 'CAN', 842: 'USA', 368: 'IRQ', 414: 'KWT', 579: 'NOR', 566: 'NGA', 398: 'KAZ', 76: 'BRA', 24: 'AGO', 484: 'MEX', 512: 'OMN', 826: 'GBR', 364: 'IRN', 328: 'GUY', 31: 'AZE', 634: 'QAT', 170: 'COL', 218: 'ECU'}

        # For copper
        # cmdCode_Dict = {"260300":"COPPER"} 
        # reporterCode_Dict = {152: 'CHL', 604: 'PER', 360: 'IDN', 36: 'AUS', 124: 'CAN', 484: 'MEX', 842: 'USA', 591: 'PAN', 76: 'BRA', 496: 'MNG', 398: 'KAZ', 688: 'SRB', 410: 'KOR', 218: 'ECU', 724: 'ESP', 268: 'GEO', 598: 'PNG', 682: 'SAU', 51: 'ARM', 458: 'MYS'}
        
        # For Lithium
        # cmdCode_Dict = {"282520":"LITHIUM"} 
        # reporterCode_Dict = {156: 'CHN', 152: 'CHL', 842: 'USA', 528: 'NLD', 410: 'KOR', 826: 'GBR', 56: 'BEL', 251: 'FRA', 784: 'ARE', 392: 'JPN', 699: 'IND', 233: 'EST', 616: 'POL', 642: 'ROU', 757: 'CHE', 124: 'CAN', 566: 'NGA', 792: 'TUR', 705: 'SVN', 203: 'CZE'}
            
        # For wood
        # cmdCode_Dict = {"4403":"WOOD"} 
        # reporterCode_Dict = {554: 'NZL', 842: 'USA', 276: 'DEU', 203: 'CZE', 858: 'URY', 124: 'CAN', 251: 'FRA', 616: 'POL', 428: 'LVA', 528: 'NLD', 56: 'BEL', 579: 'NOR', 598: 'PNG', 752: 'SWE', 76: 'BRA', 178: 'COG', 703: 'SVK', 724: 'ESP', 705: 'SVN', 233: 'EST'}
         
        # For Cocoa
        # cmdCode_Dict = {"180100":"COCOA"} 
        # reporterCode_Dict = {384: 'CIV', 288: 'GHA', 218: 'ECU', 566: 'NGA', 120: 'CMR', 528: 'NLD', 458: 'MYS', 604: 'PER', 180: 'COD', 598: 'PNG', 800: 'UGA', 360: 'IDN', 56: 'BEL', 233: 'EST', 450: 'MDG', 834: 'TZA', 276: 'DEU', 768: 'TGO', 170: 'COL', 842: 'USA'}

        # For wheat
        cmdCode_Dict = {"110100":"WHEAT"} 
        reporterCode_Dict = {792: 'TUR', 398: 'KAZ', 276: 'DEU', 699: 'IND', 860: 'UZB', 380: 'ITA', 32: 'ARG', 124: 'CAN', 842: 'USA', 56: 'BEL', 818: 'EGY', 826: 'GBR', 704: 'VNM', 251: 'FRA', 512: 'OMN', 392: 'JPN', 528: 'NLD', 348: 'HUN', 784: 'ARE', 156: 'CHN'}
        
        year = "2022"

        for cmdCode,goods in cmdCode_Dict.items():
            if reporterCode_Dict is None:
                data = fetch_data(api_key, cmdCode, year, None)
                save_data(data, f"./data/raw/RAW_COMTRADE_{goods}_{year}.parquet")
                time.sleep(3)
            else:
                for reporterCode,countryName in reporterCode_Dict.items():
                    data = fetch_data(api_key, cmdCode, year, reporterCode)
                    save_data(data, f"./data/raw/{goods.lower()}/RAW_COMTRADE_{goods}_{year}_{countryName}.parquet")
                    time.sleep(3)
            

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
