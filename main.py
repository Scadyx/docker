
import json
import time
from fastapi import FastAPI, Body
import uvicorn
from pydantic import BaseModel
from typing import Optional


def setup_raw_data(file_path: str):
    with open(file_path, 'r') as f:
        data = list(map(json.loads, f))

    for i, x in enumerate(data):
        x['id'] = i + 1

    with open(file_path, 'w') as f:
        for user in data:
            f.write(json.dumps(user) + '\n')


class UserModel(BaseModel):
    id: int
    name: str
    last_name: Optional[str] = None
    time_created: int
    age: Optional[int] = None
    city: Optional[str] = None
    gender: Optional[str] = None
    birth_day: Optional[str] = None
    ip: Optional[str] = None
    premium: Optional[str] = None

    def update(self, new_user: dict):
        for key in new_user:
            if hasattr(self, key) and key != id:
                setattr(self, key, new_user[key])


class UserDict:
    user_dict: dict
    max_id: int

    def __init__(self, filename):
        self.user_dict = {}
        self.max_id = 0
        with open(filename, 'r') as f:
            data = list(map(json.loads, f))
        users = [UserModel(**x) for i, x in enumerate(data)]
        for user in users:
            if user.id is not None:
                self.max_id = max(self.max_id, user.id)
            else:
                user.id = self.max_id + 1
                self.max_id = self.max_id + 1
            self.user_dict[user.id] = user

        self.max_id = max(self.user_dict.keys())
        print("User data loaded")

    def create_user(self, new_user_dict):
        if new_user_dict["name"] is not None:
            name = new_user_dict["name"]
        else:
            raise Exception("Name didn't specified")
        new_user = UserModel(id=self.max_id + 1, time_created=int(time.time()), name=name)
        self.user_dict[self.max_id + 1] = new_user
        self.user_dict[self.max_id + 1].update(new_user_dict)
        self.max_id = self.max_id + 1

    def update_user(self, user_id, new_data):
        if int(user_id) in self.user_dict:
            self.user_dict[int(user_id)].update(new_data)
        else:
            raise Exception("User not found")

    def return_by_key(self, id):
        data_id = int(id)
        if data_id in self.user_dict:
            return self.user_dict[data_id]
        else:
            raise Exception("User not found")

    def get_list(self):
        return self.user_dict

    def get_max_id(self):
        return self.max_id

    def delete_user(self, id):
        data_id = int(id)
        if data_id in self.user_dict:
            del self.user_dict[data_id]

    def delete_list(self):
        self.user_dict = {}

    def write_to_file(self, file_name):
        user_list = [self.user_dict[x].__dict__ for x in self.user_dict]
        with open(file_name, 'w') as f:
            for user in user_list:
                json.dump(user, f)
                f.write('\n')







file = 'data.jsonl'
setup_raw_data(file)
data = UserDict(file)
app = FastAPI()

@app.get("/users")
def get_users():
    return data.get_list()


@app.delete("/users")
def delete_users():
    data.delete_list()
    data.write_to_file(file)
    return data


@app.get("/user")
def get_users(key):
    return data.return_by_key(key)


@app.delete("/user")
def delete_user(key):
    data.delete_user(key)
    data.write_to_file(file)
    return True


@app.put("/user")
def update_user(id, body: dict = Body(...)):
    data.update_user(id, body)
    data.write_to_file(file)
    return True


@app.post("/user")
def create_user(body: dict = Body(...)):
    data.create_user(body)
    data.write_to_file(file)
    return True


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)

