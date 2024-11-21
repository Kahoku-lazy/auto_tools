""" 教程链接：
https://github.com/datawhalechina/handy-ollama/blob/main/docs/C4/2.%20%E5%9C%A8%20Python%20%E4%B8%AD%E4%BD%BF%E7%94%A8%20Ollama%20API.md
"""
import ollama

MODELFIEL='''
FROM qwen2.5-coder:0.5b
SYSTEM 你是一名专业的Python开发者, 针对问题你需要输出代码即可,不需要注释与环境配置
'''
def write_code(file_name, code):
    if '```' in code:
        code.replace('```', '')
    with open(file_name, 'w') as file:
        file.write(code)

def ollama_qwen2_5_0_5b(messages):

    model_name = "qwen2.5-coder:0.5b"
    values = ollama.generate(model = model_name, prompt=messages)
    return values
    
if __name__ == '__main__':
    messages = '使用Python写一个函数或方法, 需要只输出可执行的代码; 使用pandas用于读取csv文件并返回其中的数据'
    result = ollama_qwen2_5_0_5b(messages)

    write_code('code.py', result)

