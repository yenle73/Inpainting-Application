## Giới thiệu môn học
* Tên môn học: Xử lý ảnh và Ứng dụng - Image Processing and Application
* Mã môn học: CS406
* Mã lớp: CS406.O12.KHCL
* Giảng viên: Ths. Đỗ Văn Tiến

## Thành viên
1. Lê Thị Kim Yến - 21521695
2. Phạm Trâm Anh - 21520587
3. Nguyễn Tường Duy - 21520782

## Tổng quan đồ án
* Tên đồ án: Ứng dụng web xóa vật thể khỏi ảnh
* Ngôn ngữ lập trình: Python, HTML, CSS, JavaScript
* Input: Một bức ảnh và mặt nạ xác định vị trí vật thể cần xóa
* Output: Ảnh đã xóa vật thể

## Getting Started
### 1. Clone project
Clone project repository về máy:

```git clone https://github.com/yenle73/Inpainting-Application.git```

### 2. Cài đặt các thư viện
Tạo môi trường ảo và install các thư viện cần thiết trong file requirements.txt:

```pip install -r requirements.txt```

### 3. Tải pretraind models
Tải pretrained models tại [đây](https://mycuhk-my.sharepoint.com/:f:/g/personal/1155137927_link_cuhk_edu_hk/EuY30ziF-G5BvwziuHNFzDkBVC6KBPRg69kCeHIu-BXORA?e=7OwJyE). Sau đó, tạo folder "pretrained" và di chuyển các file model vào đây.

### 4. Chạy file main

```uvicorn main:app reload```


