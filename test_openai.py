import os
from openai import OpenAI

def test_openai_connection():
    try:
        # 从环境变量获取 API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("错误: 未找到 OPENAI_API_KEY 环境变量")
            return False
            
        # 初始化 OpenAI 客户端
        client = OpenAI(api_key=api_key)
        
        # 发送一个简单的测试请求
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            max_tokens=10
        )
        
        print("API 连接成功!")
        print(f"响应内容: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"连接测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_connection()