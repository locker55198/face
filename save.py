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

if os.environ.get('REQUEST_METHOD') == 'POST':
    # 從前端接收圖像數據
    image_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxIREhUREhMVFhUXFxUVFhcYFxcXGBcXGBcWFxUVFxcYHSggGBolHRYVITEhJSkrLi4uFx8zODMtNygtLisBCgoKDg0OGxAQGy0mICY1Ly8vLS8tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIAKgBLAMBIgACEQEDEQH/xAAbAAEAAgMBAQAAAAAAAAAAAAAABAUDBAYCB//EADwQAAIBAwMCAwUFBQAAAAAAAAECAwQFEQAGIRIxQVEGEyJhcYGRobHwBxRDUpGxwfAf/EABcBAQEBAQAAAAAAAAAAAAAAAAECAwT/xAAjEQACAgIDAQEAAAAAAAAAAAAAAQIRAxIhMQTTQaHR/9oADAMBAAIRAxEAPwCzYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD//2Q=="
    
    # 將數據解碼為圖片
    image_data = image_data.split(",")[1]
    decoded_image = base64.b64decode(image_data)
    
    # 生成一個唯一的圖像文件名
    image_name = os.urandom(16).hex() + '.jpg'
    
    # 將圖像保存到伺服器上的指定目錄
    image_path = os.path.join('path/to/save', image_name)
    with open(image_path, 'wb') as file:
        file.write(decoded_image)
    
    # 將圖像與數據庫中的圖像進行比較
    user_exists = False  # 标记用户是否存在
    
    # 在数据库中查询用户信息
    # 例如：SELECT * FROM users WHERE image_path = '$imagePath'
    
    # 如果查询到匹配的用户记录
    if user_exists:
        # 登录成功
        print("Login successful")
    else:
        # 登录失败
        print("Login failed")

# 關閉數據庫連接
conn.close()