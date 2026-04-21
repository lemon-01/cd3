from __future__ import annotations

from pathlib import Path

import pandas as pd


# File dữ liệu gốc và file đầu ra nằm trong thư mục làm việc hiện tại.
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "Doanh số bán hàng Ford 2023-2025.xlsx"
OUTPUT_FILE = BASE_DIR / "Ford_Sales_2023_2025_cleaned_v2.xlsx"


# Các cột có trong từng sheet năm và cần cho phân tích.
SOURCE_COLUMNS = [
    "STT",
    "Tên KH",
    "Tháng",
    "Quý",
    "Dòng xe",
    "Màu",
    "Khu vực",
    "Giá xe",
    "Số lượng (xe)",
]


def normalize_text(value: object) -> object:
    """Chuẩn hóa chuỗi bằng cách xóa khoảng trắng thừa và viết hoa đầu từ."""
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if not text:
        return pd.NA
    return " ".join(text.split()).title()


def normalize_region(value: object) -> object:
    """Chuẩn hóa tên khu vực về một bộ nhãn thống nhất."""
    if pd.isna(value):
        return pd.NA

    text = " ".join(str(value).strip().split())
    if not text:
        return pd.NA

    key = text.casefold()
    region_map = {
        "hcm": "HCM",
        "tp hcm": "HCM",
        "thanh pho ho chi minh": "HCM",
        "hồ chí minh": "HCM",
        "ho chi minh": "HCM",
        "ha noi": "Hà Nội",
        "hà nội": "Hà Nội",
        "da nang": "Đà Nẵng",
        "đà nẵng": "Đà Nẵng",
        "hai phong": "Hải Phòng",
        "hải phòng": "Hải Phòng",
        "can tho": "Cần Thơ",
        "cần thơ": "Cần Thơ",
    }

    return region_map.get(key, text.title())


def normalize_quarter(value: object) -> object:
    """Đưa giá trị quý về định dạng Q1-Q4."""
    if pd.isna(value):
        return pd.NA
    text = str(value).strip().upper()
    if text in {"Q1", "Q2", "Q3", "Q4"}:
        return text
    return pd.NA


def quarter_from_month(month_value: object) -> object:
    """Suy ra quý từ tháng khi ô quý bị thiếu."""
    if pd.isna(month_value):
        return pd.NA
    month = int(month_value)
    if 1 <= month <= 3:
        return "Q1"
    if 4 <= month <= 6:
        return "Q2"
    if 7 <= month <= 9:
        return "Q3"
    if 10 <= month <= 12:
        return "Q4"
    return pd.NA


def load_year_sheet(year: int) -> pd.DataFrame:
    """Đọc một sheet theo năm và thêm cột Năm."""
    frame = pd.read_excel(
        INPUT_FILE,
        sheet_name=str(year),
        usecols=SOURCE_COLUMNS,
        engine="openpyxl",
    )
    frame["Năm"] = year
    return frame


def main() -> None:
    # Đọc từng năm riêng để quy trình tiền xử lý rõ ràng và dễ kiểm tra.
    yearly_frames = [load_year_sheet(year) for year in (2023, 2024, 2025)]
    combined = pd.concat(yearly_frames, ignore_index=True)

    # Xóa cột Giá xe vì không phục vụ mục tiêu phân tích.
    combined = combined.drop(columns=["Giá xe"])

    # Chuẩn hóa các cột chuỗi chính.
    combined["Tên KH"] = combined["Tên KH"].map(normalize_text)
    combined["Dòng xe"] = combined["Dòng xe"].map(normalize_text)
    combined["Màu"] = combined["Màu"].map(normalize_text)
    combined["Khu vực"] = combined["Khu vực"].map(normalize_region)
    combined["Quý"] = combined["Quý"].map(normalize_quarter)

    # Chuyển các cột số sang kiểu dữ liệu phù hợp.
    combined["Tháng"] = pd.to_numeric(combined["Tháng"], errors="coerce").astype("Int64")
    combined["Số lượng (xe)"] = pd.to_numeric(combined["Số lượng (xe)"], errors="coerce").astype("Int64")
    combined["STT"] = pd.to_numeric(combined["STT"], errors="coerce").astype("Int64")

    # Nếu thiếu quý nhưng có tháng hợp lệ thì suy ra quý từ tháng.
    combined["Quý"] = combined.apply(
        lambda row: row["Quý"] if pd.notna(row["Quý"]) else quarter_from_month(row["Tháng"]),
        axis=1,
    )

    # Chỉ giữ các bản ghi hợp lệ với đủ trường thông tin cần thiết.
    essential_columns = ["Năm", "Tháng", "Quý", "Tên KH", "Dòng xe", "Màu", "Khu vực", "Số lượng (xe)"]
    rows_after_load = len(combined)
    combined = combined.dropna(subset=essential_columns).copy()
    rows_after_missing = len(combined)

    # Loại các bản ghi trùng lặp theo nghiệp vụ. Bỏ qua STT vì chỉ là số thứ tự nguồn.
    duplicate_subset = ["Năm", "Tháng", "Quý", "Tên KH", "Dòng xe", "Màu", "Khu vực", "Số lượng (xe)"]
    before_duplicates = len(combined)
    combined = combined.drop_duplicates(subset=duplicate_subset).copy()
    duplicates_removed = before_duplicates - len(combined)

    # Loại giá trị bất thường của Số lượng bằng quy tắc IQR, sau đó chỉ giữ số dương.
    quantity = combined["Số lượng (xe)"].astype(float)
    q1 = quantity.quantile(0.25)
    q3 = quantity.quantile(0.75)
    iqr = q3 - q1
    if pd.notna(iqr) and iqr > 0:
        lower_bound = max(0, q1 - 1.5 * iqr)
        upper_bound = q3 + 1.5 * iqr
        before_outliers = len(combined)
        combined = combined[quantity.between(lower_bound, upper_bound)].copy()
        outliers_removed = before_outliers - len(combined)
    else:
        outliers_removed = 0
    combined = combined[combined["Số lượng (xe)"] > 0].copy()

    # Sắp xếp dữ liệu sạch theo năm -> quý -> tháng.
    quarter_order = pd.CategoricalDtype(categories=["Q1", "Q2", "Q3", "Q4"], ordered=True)
    combined["Quý"] = combined["Quý"].astype(quarter_order)
    combined = combined.sort_values(["Năm", "Quý", "Tháng", "STT"], kind="stable").reset_index(drop=True)
    combined["Quý"] = combined["Quý"].astype(str)

    # Sắp xếp lại thứ tự cột cho bảng phân tích gọn hơn.
    final_columns = ["Năm", "Quý", "Tháng", "STT", "Tên KH", "Dòng xe", "Màu", "Khu vực", "Số lượng (xe)"]
    combined = combined[final_columns]

    # Lưu dữ liệu đã làm sạch và một sheet tổng hợp ngắn trong cùng workbook.
    summary = pd.DataFrame(
        {
            "Metric": [
                "Số dòng đã đọc",
                "Số dòng sau xử lý thiếu",
                "Số dòng trùng bị xóa",
                "Số dòng bất thường bị xóa",
                "Số dòng cuối cùng",
            ],
            "Value": [
                rows_after_load,
                rows_after_missing,
                duplicates_removed,
                outliers_removed,
                len(combined),
            ],
        }
    )

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        combined.to_excel(writer, sheet_name="CleanedData", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=False)

    print("Đã ghi file dữ liệu sạch vào:", OUTPUT_FILE)
    print("Số dòng cuối cùng:", len(combined))
    print("Số dòng trùng bị xóa:", duplicates_removed)
    print("Số dòng bất thường bị xóa:", outliers_removed)


if __name__ == "__main__":
    main()