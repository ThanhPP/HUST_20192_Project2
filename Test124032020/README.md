# Thử nghiệm theo "Machine Learning Algorithm To Predict Stock Direction" :

## 1. Thư viện sử dụng : 

_ [yfinance](https://github.com/ranaroussi/yfinance) : Lấy dữ liệu bằng Yahoo! Finance.

_ [pandas](https://pandas.pydata.org/) : phân tích dữ liệu.

- *pandas_datareader.data* : không sử dụng vì các nguồn dữ liệu có sẵn đều yêu cầu trả phí hoặc giới hạn số lượng truy vấn.

    - IEX : cho phép 50,000 core messages/tháng.
    
## 2. Chương trình : 

### 2.1. Class :

_ TickerData : Dùng để lưu dữ liệu.

- append_change_column : Thêm cột change vào dataframe chứa dữ liệu
    
    - Lấy hiệu của giá trị **'Close'** giữa 2 ngày.
    
- drop_row_with_zeros : Loại bỏ đi các hàng chứa giá trị 0.