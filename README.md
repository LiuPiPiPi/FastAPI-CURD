# FastAPI-CURD

<img src="https://lpxz.oss-cn-zhangjiakou.aliyuncs.com/picgo/202209181732134.png" alt="FastAPI" style="zoom: 80%;" />

FastAPI 是一个用于构建 API 的现代、快速（高性能）的 web 框架，使用 Python 3.6+ 并基于标准的 Python 类型提示。

关键特性:

- **快速**：可与 **NodeJS** 和 **Go** 比肩的极高性能（归功于 Starlette 和 Pydantic）。[最快的 Python web 框架之一](https://fastapi.tiangolo.com/zh/#_11)。
- **高效编码**：提高功能开发速度约 200％ 至 300％。
- **更少 bug**：减少约 40％ 的人为（开发者）导致错误。
- **智能**：极佳的编辑器支持。处处皆可自动补全，减少调试时间。
- **简单**：设计的易于使用和学习，阅读文档的时间更短。
- **简短**：使代码重复最小化。通过不同的参数声明实现丰富功能。bug 更少。
- **健壮**：生产可用级别的代码。还有自动生成的交互式文档。
- **标准化**：基于（并完全兼容）API 的相关开放标准：[OpenAPI](https://github.com/OAI/OpenAPI-Specification) (以前被称为 Swagger) 和 [JSON Schema](https://json-schema.org/)。

文档： [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com/)

源码： https://github.com/tiangolo/fastapi

---

### 示例程序 Entry Point

环境准备：

1、首先，需要创建一个虚拟环境和 FastAPI。

```bash
conda create -n fastapi
# 进入虚拟环境
conda activate fastapi
# 安装相关依赖
conda install fastapi
conda install gunivorn
```

2、新建 `main.py` 作为入口文件

```python
from fastapi import FastAPI

# initailize FastApi instance
app = FastAPI()

# define endpoint
@app.get("/")
def home():
    return {"Ahoy": "Captain"}
```

3、当前目录命令行执行 `uvicorn main:app --reload`

- main 指的是入口点的名称
- app 指的是从 `main.py` 初始化的 FastAPI 实例
- --reload 是一个标志，它允许服务器在更改项目时重新加载自己

4、访问链接

- http://lcoalhost:8000/（返回 {"Ahoy": "Captain"}）
- http://lcoalhost:8000/docs 自动交互式 API 文档（SwaggerUI）

## 文件结构

fastapi-demo
├── crud.py
├── db.py
├── main.py
└── models.py

`main.py` 初始化 FastAPI 实例：

```python
from fastapi import FastAPI

app = FastAPI()
```

## 数据库连接

初始化数据库时，因为我们不会有太多的数据，所以我们将使用 SQLite 作为数据库。SQLite 是一个内置的 python 库，所以我们不需要安装它。

与 Django 不同，FastAPI 没有自己的对象关系映射工具，因此我们将使用 SQLAlchemy。

```bash
conda install sqlalchemy
```

`db.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# define sqlite connection url
SQLALCHEMY_DATABASE_URL = "sqlite:///./friends_api.db"

# create new engine instance
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

在初始化 FastAPI 实例之后 `main.py` 添加以下内容：

```python
from db import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 定义实体类

`models.py`

```python
from sqlalchemy import Column, Integer, String

from db import Base

# model/table
class  Friend(Base):
    __tablename__ = "friend"

    # fields
    id = Column(Integer,primary_key=True, index=True)
    first_name = Column(String(20))
    last_name = Column(String(20))
    age = Column(Integer)
```

`main.py` 文件中添加：

```python
import models
from db import engine

# create the database tables on app startup or reload
models.Base.metadata.create_all(bind=engine)
```

在将新的更改保存到 `main.py` 之后，目录生成一个新的文件 `friends_api.db`。这是 SQLite 数据库，其名称来自 `db.py` 中的连接字符串。

## CRUD 代码实现

```python
from sqlalchemy.orm import Session

"""
Session manages persistence operations for ORM-mapped objects.
Let's just refer to it as a database session for simplicity
"""

from models import Friend


def create_friend(db:Session, first_name, last_name, age):
    """
    function to create a friend model object
    """
    # create friend instance
    new_friend = Friend(first_name=first_name, last_name=last_name, age=age)
    #place object in the database session
    db.add(new_friend)
    #commit your instance to the database
    db.commit()
    #reefresh the attributes of the given instance
    db.refresh(new_friend)
    return new_friend

def get_friend(db:Session, id:int):
    """
    get the first record with a given id, if no such record exists, will return null
    """
    db_friend = db.query(Friend).filter(Friend.id==id).first()
    return db_friend

def list_friends(db:Session):
    """
    Return a list of all existing Friend records
    """
    all_friends = db.query(Friend).all()
    return all_friends


def update_friend(db:Session, id:int, first_name: str, last_name: str, age:int):
    """
    Update a Friend object's attributes
    """
    db_friend = get_friend(db=db, id=id)
    db_friend.first_name = first_name
    db_friend.last_name = last_name
    db_friend.age = age

    db.commit()
    db.refresh(db_friend) #refresh the attribute of the given instance
    return db_friend

def delete_friend(db:Session, id:int):
    """
    Delete a Friend object
    """
    db_friend = get_friend(db=db, id=id)
    db.delete(db_friend)
    db.commit() #save changes to db
```

## 定义请求接口

`main.py` 文件中添加：

```python
from sqlalchemy.orm import Session

"""
So that FastAPI knows that it has to treat a variable as a dependency, we will import Depends
"""
from fastapi import Depends

# import crud to give access to the operations that we defined
import crud

# define endpoint
@app.post("/create_friend")
def create_friend(first_name: str, last_name: str, age: int, db: Session = Depends(get_db)):
    friend = crud.create_friend(db=db, first_name=first_name, last_name=last_name, age=age)
    # return object created
    return {"friend": friend}


# get/retrieve friend
@app.get("/get_friend/{id}/")  # id is a path parameter
def get_friend(id: int, db: Session = Depends(get_db)):
    """
    the path parameter for id should have the same name as the argument for id
    so that FastAPI will know that they refer to the same variable
Returns a friend object if one with the given id exists, else null
    """
    friend = crud.get_friend(db=db, id=id)
    return friend


@app.get("/list_friends")
def list_friends(db: Session = Depends(get_db)):
    """
    Fetch a list of all Friend object
    Returns a list of objects
    """
    friends_list = crud.list_friends(db=db)
    return friends_list


@app.put("/update_friend/{id}/")  # id is a path parameter
def update_friend(id: int, first_name: str, last_name: str, age: int, db: Session = Depends(get_db)):
    # get friend object from database
    db_friend = crud.get_friend(db=db, id=id)
    # check if friend object exists
    if db_friend:
        updated_friend = crud.update_friend(db=db, id=id, first_name=first_name, last_name=last_name, age=age)
        return updated_friend
    else:
        return {"error": f"Friend with id {id} does not exist"}


@app.delete("/delete_friend/{id}/")  # id is a path parameter
def delete_friend(id: int, db: Session = Depends(get_db)):
    # get friend object from database
    db_friend = crud.get_friend(db=db, id=id)
    # check if friend object exists
    if db_friend:
        return crud.delete_friend(db=db, id=id)
    else:
        return {"error": f"Friend with id {id} does not exist"}
```

## 查看 API 文档

打开浏览器，进入链接：http://localhost:8000/docs

<img src="https://lpxz.oss-cn-zhangjiakou.aliyuncs.com/picgo/202209181759900.png" alt="image-20220918175944662" style="zoom:80%;" />

参考文章：[Simple FastAPI CRUD - DEV Community 👩‍💻👨‍💻](https://dev.to/mungaigikure/simple-fastapi-crud-3ad0)
