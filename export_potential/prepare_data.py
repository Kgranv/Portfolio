import pandas as pd
import numpy as np
import country_converter as coco
import comtradeapicall

def get_raw_data(filepath) -> pd.Dataframe:
    return pd.read_parquet(filepath)

def filter_data(raw_data) -> pd.DataFrame:
    data_filtered = raw_data[["period","reporterCode","cmdCode","qty","qtyUnitCode","primaryValue"]]
    return data_filtered

def add_iso_code(df) -> pd.DataFrame:
    reporter_data = pd.read_parquet("./data/reporter.parquet")
    df = df.merge(reporter_data[["reporterCode", "reporterCodeIsoAlpha3", "text"]], on="reporterCode", how="inner")
    df.rename(columns={'text': 'countryName'}, inplace=True)
    return df

def add_goods_description(df) -> pd.DataFrame:
    goods_data = pd.read_parquet("./data/goods.parquet")
    df = df.merge(goods_data[["id", "text"]],left_on="cmdCode", right_on="id", how="inner")
    df = df.drop(columns=["id"])
    return df

def add_quantity_description(df) -> pd.DataFrame:
    qty_data = pd.read_parquet("./data/qty_unit.parquet")
    df = df.merge(qty_data[["qtyCode", "qtyAbbr"]],left_on="qtyUnitCode", right_on="qtyCode", how="inner")
    df = df.drop(columns=["qtyCode"])
    df.rename(columns={'qtyAbbr': 'qtyUnit'}, inplace=True)
    return df

def calculate_RCA_RSCA(df) -> pd.DataFrame:
    all_export_world = df[df["cmdCode"]=="TOTAL"][["reporterCode","primaryValue"]]
    goods_export_world = df[df["cmdCode"]!="TOTAL"][["reporterCode","primaryValue"]]

    value_all_export_world = all_export_world["primaryValue"].sum()
    value_goods_export_world = goods_export_world["primaryValue"].sum()

    all_export_world = all_export_world.set_index("reporterCode")
    goods_export_world = goods_export_world.set_index("reporterCode")

    goods_export_world["RCA"] = ((goods_export_world["primaryValue"]/all_export_world["primaryValue"])/(value_goods_export_world/value_all_export_world))
    all_export_world["RCA"] = np.nan


    goods_export_world['RSCA'] = (goods_export_world['RCA'] - 1) / (goods_export_world['RCA'] + 1)
    all_export_world["RSCA"] = np.nan

    mask = df["cmdCode"] == "TOTAL"
    df.loc[mask, "RCA"] = df.loc[mask, "reporterCode"].map(all_export_world["RCA"])
    df.loc[mask, "RSCA"] = df.loc[mask, "reporterCode"].map(all_export_world["RSCA"])

    # Pour le reste (via goods_export_world)
    df.loc[~mask, "RCA"] = df.loc[~mask, "reporterCode"].map(goods_export_world["RCA"])
    df.loc[~mask, "RSCA"] = df.loc[~mask, "reporterCode"].map(goods_export_world["RSCA"])
    return df

def convert_data(data_filtered) -> pd.DataFrame:
    data_converted = add_iso_code(data_filtered)
    data_converted = add_goods_description(data_converted)
    data_converted = add_quantity_description(data_converted)
    data_converted = calculate_RCA_RSCA(data_converted)
    return data_converted

def main():
    files = ["RAW_COMTRADE_COCOA_2022","RAW_COMTRADE_COPPER_2022","RAW_COMTRADE_LITHIUM_2022","RAW_COMTRADE_OILS_2022","RAW_COMTRADE_WOOD_2022"]

    for file in files:
        raw_data = get_raw_data(f"./data/raw/{file}.parquet")
        data_filtered = filter_data(raw_data)
        data_converted = convert_data(data_filtered)
        data_converted.to_parquet(f"./data/clean/{file.strip("RAW_")}.parquet",engine='auto', compression='snappy', index=False)


if __name__ == "__main__":
    main()
