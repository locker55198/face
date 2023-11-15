import base64
import os
import mysql.connector

# 設置MySQL數據庫連接
host = "localhost"
user = "your_username"
password = "your_password"
database = "your_database"

# 創建MySQL數據庫連接
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# 檢查連接是否成功
if conn.is_connected():
    print("已成功連接到MySQL數據庫")
else:
    print("連接MySQL數據庫失敗")

# 獲取POST請求中的圖像數據
image_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxIREhUREhMVFhUXFxUVFhcYFxcXGBcXGBcWFxUVFxcYHSggGBolHRYVITEhJSkrLi4uFx8zODMtNygtLisBCgoKDg0OGxAQGy0mICY1Ly8vLS8tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIAKgBLAMBIgACEQEDEQH/xAAbAAEAAgMBAQAAAAAAAAAAAAAABAUDBAYCB//EADwQAAIBAwIDBQQHBQAAAAAAAAECAwQFEQAGEiExBxNBUWEIFDJhFTJCcYGhsRUWM0JyscHh8f/EABcBAQEBAQAAAAAAAAAAAAAAAAECAwT/xAAjEQACAgIDAQEAAAAAAAAAAAAAAQIRAxIhMQTTQaHR/9oADAMBAAIRAxEAPwCzYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD//2Q=="
# 解碼Base64圖像數據
image_data = image_data.split(",")[1]
image_data = base64.b64decode(image_data)

# 生成圖像文件名
filename = os.path.join(os.getcwd(), f"{os.urandom(16).hex()}.jpg")

# 保存圖像文件到指定目錄
with open(filename, "wb") as file:
    file.write(image_data)

# 將圖像文件名保存到數據庫
cursor = conn.cursor()
sql = "INSERT INTO images (filename) VALUES (%s)"
values = (filename,)
cursor.execute(sql, values)
conn.commit()

if cursor.rowcount > 0:
    print("圖像已保存到數據庫")
else:
    print("保存圖像到數據庫失敗")

# 關閉數據庫連接
cursor.close()
conn.close()