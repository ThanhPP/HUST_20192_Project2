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

- drop_row_with_NA : Loại bỏ đi các hàng chứa giá trị N/A.

_ sample_slopes : 

- slope_sum : tổng số chênh lệch giữa cổ phiếu quan tâm và phần còn lại của cổ phiếu trong nhóm.

- create_slope_sum_market : tạo ra cột slope sum theo cổ phiếu được lưu bên cạnh.

    - Tính tổng chênh lệch của 1 cổ phiếu với 2 cổ phiếu ngay sát (trái và phải).

-  create_slope_sum_market : tạo ra cột slope sum theo cổ phiếu và toàn bộ nhóm cổ phiếu.
    
    - Tính tổng chênh lệch của cổ phiếu quan tâm với tất cả các cổ phiếu khác.

- find_percent_change : % chênh lệch giữa 2 số đầu vào

- _sliding_windows : 
    
    - Trả về 1 generator 
    - Kết quả là lần lượt [i + winSize] phần tử sẽ được trả về.
    
_ support_vector

- train :

    - Sử dụng phương pháp Support Vector Machine.
    - Chia dữ liệu đầu vào với tỷ lệ 0.2.
    - Có thể tùy chọn ghi lại model.
    
- predict_out_put : 
    
    - Nhận vào model, và 1 cặp giá trị.
    - Dự đoán xem có nên mua hay không.
    
### 2.2. Chạy chương trình : 

_ Lựa chọn tham số : 

- batch_size : số ngày gộp vào để thành 1 nhóm

- look_ahead : số ngày dự đoán 

_ Lấy dữ liệu của stock :

- Được liệt kê trong biến **tickers**.

- Thời gian được lưu trong các biến **start_date** và **end_date**.

- Sắp xếp lại dữ liệu theo thời gian.

_ Thêm cột CHG : Giá trị thay đổi của stock sau 1 ngày

_ Lưu dữ liệu.

_ Bỏ các hàng có giá trị N/A và lưu lại : 

- Giá trị của ngày đầu tiên

- Giá trị có N/A khác

_ Thêm cột slope_sum_market

- Tên tickers + slope_sum

- Tính tổng chênh lệch của cổ phiếu quan tâm với tất cả các cổ phiếu khác

_ Chạy thuật toán Support Vector Machine 

- y_values : Tập các giá trị 1, -1 đại diện cho giá của cổ phiếu tăng hay giảm.
- x_values : Tập các giá trị chênh lệch của cổ phiếu so với toàn bộ thị trường.
    
