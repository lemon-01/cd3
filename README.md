# Ford Sales Analysis (2023-2025)

Dự án phân tích doanh số bán xe Ford giai đoạn 2023-2025, bao gồm:
- Khám phá dữ liệu theo thời gian, dòng xe và khu vực.
- Trực quan hóa bằng biểu đồ.
- Dự báo ngắn hạn bằng mô hình Holt-Winters.

## Cấu trúc dự án

- `Ford_Sales_Analysis_2023_2025.ipynb`: Notebook phân tích chính.
- `preprocess_ford_sales.py`: Script tiền xử lý dữ liệu.
- `Doanh số bán hàng Ford 2023-2025.xlsx`: Dữ liệu gốc.
- `Ford_Sales_2023_2025_cleaned_v2.xlsx`: Dữ liệu đã làm sạch.

## Yêu cầu môi trường

Khuyến nghị Python 3.10+ và các thư viện:
- pandas
- numpy
- matplotlib
- seaborn
- statsmodels
- openpyxl

Cài đặt nhanh:

```bash
pip install pandas numpy matplotlib seaborn statsmodels openpyxl
```

## Cách chạy

### 1) Chạy notebook
1. Mở file `Ford_Sales_Analysis_2023_2025.ipynb` trong VS Code hoặc Jupyter.
2. Chạy lần lượt các cell từ trên xuống.

### 2) Chạy script tiền xử lý

```bash
python preprocess_ford_sales.py
```

## Nội dung phân tích chính

1. Tổng quan doanh số theo thời gian (tháng, quý, năm).
2. Phân tích doanh số theo dòng xe và màu sắc.
3. Phân tích doanh số theo khu vực.
4. Dự báo doanh số ngắn hạn bằng Holt-Winters.

## Ghi chú

- Bộ dữ liệu hiện không có cột giá bán, nên chỉ số doanh số trong báo cáo được hiểu theo sản lượng xe bán.
- Có thể mở rộng mô hình dự báo nếu bổ sung dữ liệu giá bán, khuyến mại, tồn kho hoặc yếu tố thị trường.
