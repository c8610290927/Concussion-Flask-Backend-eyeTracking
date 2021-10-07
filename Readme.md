Concussion-Cloud-Flask 
===
# Design Goal
接收來自 VEP, Eyetracking unity 遊戲的資料，並在遊戲結束後通知計算 server 計算特徵。
![images/img.png](images/img.png)

# Relational Database Schema
![images/img.png](images/db_schema.jpg)

# Usage
```bash
// edit environment variable
vim .env

// 安裝 dependency
pip install -r requirements.txt

python app.py
```
