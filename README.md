# Stock trending using Machine Learning

## MỤC LỤC : 

### [Stock trending using Machine Learning](#stock-trending-using-machine-learning)

#### [I. MỤC LỤC](#mục-lục-)

#### [II. Chi tiết đề tài](#chi-tiết-đề-tài-)

#### [III. Tài liệu tham khảo](#tài-liệu-tham-khảo-)

#### [IV. Benchmark hệ thống](#benchmark-hệ-thống-)

## Chi tiết đề tài : 

_ **Tên học phần** : Project 2.

_ **Tên đề tài** : Ứng dụng học máy trong phân tích dữ liệu tài chính.

_ **Người hướng dẫn** : giảng viên Đỗ Tuấn Anh.

_ **Sinh viên thực hiện** : 

- Phan Phú Thành

- [Nguyễn Thanh Tùng](https://github.com/pinezapple)

_ [**Các tài liệu khác**](https://drive.google.com/open?id=1bVA8XYJ_cDb9mNIbi9VGlNTvnni_0VFJ)

## Tổng quan hệ thống:

### SystemX

- Hệ thống bao gồm 3 components chính là:
    + Data Crawler (getStockData)
    + Price Generator
    + Poral API

- Dưới đây là hình ảnh tổng quan về sơ đồ  các components hệ thống tương tác:
![SystemOverall](Picture/image.png)

### Chi tiết về các thành phần :

#### [1. Data Crawler & Portal](https://github.com/ThanhPP/HUST_20192_Project2/tree/master/systemX)

#### [2. Price Predictor](https://github.com/ThanhPP/HUST_20192_Project2/tree/master/systemX/Price_Generator)


### Benchmark hệ thống : 

#### 2.1. Crawler performance:
+ Để ghi 3000 dòng record vào 1 shard, Crawler tốn khoảng thời gian giao động từ 11.6 - 13.4 giây (DBMS là mysql).

#### 2.2. Training Data Performance: 

+ Cấu hình máy : Dell M4800 - Intel I7 - 4910MQ

+ Đối với [mô hình LSTM 2 lớp](https://github.com/ThanhPP/HUST_20192_Project2/tree/master/systemX/Price_Generator#2-m%C3%B4-h%C3%ACnh-lstm-2-l%E1%BB%9Bp--1)
    - Thời gian trung bình hết khoảng 1 phút 20 giây cho 1 ticker.
    - Settings :
      - Thời gian lấy dữ liệu : 01/01/2010 - 01/01/2020
      - BATCH_SIZE = 365
      - EPOCHS = 10
      - UNITS = 365
      - CELL = LSTM
      - N_LAYERS = 2
      - DROPOUT = 0.3

## Tài liệu tham khảo : 

_ [Machine Learning cơ bản](https://drive.google.com/open?id=0B7ujsutwirjXLXlwcnZUTjVVRXVjd19WNlVmREdac0xFNGIw)

_ [A Novel Algorithmic Trading Framework](https://drive.google.com/open?id=0B7ujsutwirjXc2YzVWdYWUZUZnBzNEp1MXotNVhrUEpfTmlj)

_ [Machine Learning Algorithm To Predict Stock Direction](https://medium.com/@jasonbamford/machine-learning-algorithm-to-predict-stock-direction-d54b7666cc7c)