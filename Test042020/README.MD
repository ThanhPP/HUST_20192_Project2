# Xây dựng neural network đơn giản dự đoán xu hướng chứng khoán bằng tensorflow

## I. Chi tiết :

_ Python : 3.7.7

_ Tensorflow : 2.1.0 

## II. Chi tiết chương trình :

### 1. Lấy dữ liệu :

_ DataFrame của dữ liệu chứng khoán được tạo tại file : **ticker_data.py**

_ Dữ liệu được lấy theo các tham số và trả về kết quả trong 1 từ điển

_ Các tham số nhận vào :

- Dữ liệu : APPL (Apple)

- Thời gian :
    - Bắt đầu : 1/1/2001
    - Kết thúc : 31/12/2019

- LOOKUP_STEPS = 0.1

- N_STEPS = 50

- TEST_SIZE = 0.1

_ Kết quả trả về :

- df : dataframe crawl về từ yahoo API

- column_scaler : scale lại data bằng MinMaxScaler

- last_sequence : sử dụng để dự đoán trong những ngày trong tương lai không có sẵn trong tập dữ liệu

- Dữ liệu để huấn luyện model 
    
    - X_train
    
    - X_test
    
    - y_train
    
    - y_test
    
### 2.Tạo model

_ Được tạo tại file **model.py**