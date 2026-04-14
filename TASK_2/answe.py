age = 25
message = "나이: "
print(message + str(age))



fruits = ["apple", "bann", "orange"]
print(fruits[0])
fruits.append("orange")
fruits[1] = "mange"

dict = {"name": "홍길동", "age": 30}
print(dict["name"])
dict["age"] = 31
print(dict["age"])



score = 65
if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
elif score >= 60:
    print("D")
else:
    print("F")

class Dog:
    def __init__(self, name, age):
            self.name = name
            self.age = age

    def bark(self):
            print("멍멍!")
my_dog = Dog("뽀삐", 3)
print(my_dog.name)
print(my_dog.age)
my_dog.bark()


{
    "name": "홍길동",
    "age": 30,
    "hobbies": ["독서", "운동", "요리"],
    "is_student": False
    
}