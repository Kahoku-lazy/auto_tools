class Calculator:
    def add(self, a, b):
        return a + b

calc = Calculator()

# 获取方法并传参
add_method = getattr(calc, 'add')
result = add_method(5, 3)  # 调用add方法并传入参数
print(result)  # 输出: 8


method_name = 'subtract'
subtract_method = getattr(calc, method_name, lambda x, y: "方法不存在")
result = subtract_method(5, 3)  # 调用不存在的方法
print(result)  # 输出: 方法不存在
