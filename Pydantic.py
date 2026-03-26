# from pydantic import BaseModel
#1.数据验证
# class User(BaseModel):
#     name: str
#     age: int

# # 验证输入数据
# user_data = {'name': 'Alice', 'age': 30}
# user = User(**user_data)  # 使用 ** 解包字典，将键值对作为参数传递给 User 构造函数
# print(user)

# invalid_data = {'name': 'Alice', 'age': 'not a number'}
# try:
#     user = User(**invalid_data)  # 会抛出错误
# except ValueError as e:
#     print(e)

#2.嵌套模型
# class Address(BaseModel):
#     street: str
#     city: str
#     country: str

# class User(BaseModel):
#     name: str
#     age: int
#     address: Address

# address_data = {
#     'street': '123 Main St',
#     'city': 'Somewhere',
#     'country': 'USA'
# }

# user_data = {
#     'name': 'Alice',
#     'age': 30,
#     'address': address_data
# }

# user = User(**user_data)
# print(user)

#3.自定义验证
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    age: int

    @field_validator('age')
    def check_age(cls, value):
        if value < 18:
            raise ValueError('Age must be greater than or equal to 18')
        return value

user_data = {'name': 'Alice', 'age': 15}
try:
    user = User(**user_data)
except ValueError as e:
    print(e)