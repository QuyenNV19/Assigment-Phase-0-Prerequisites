import time
import random

def call_api_with_retry(url, max_retries=3, delay=1, backoff=2):
    for attempt in range(max_retries + 1):
        try:
            r = random.random()
            print(f"Đang gọi API {url} (Lần thử {attempt})...")
            
            if r < 0.5:
                raise TimeoutError("Lỗi Timeout")
            else:
                return {"status": 200, "data": "OK"}

        except TimeoutError as e:
            if attempt == max_retries:
                print("Đã hết lượt thử lại.")
                raise e
            
            wait_time = delay * (backoff ** attempt)
            print(f"Lỗi: {e}. Thử lại sau {wait_time} giây...")
            time.sleep(wait_time)

if __name__ == "__main__":
    try:
        res = call_api_with_retry("https://api.llm.com", max_retries=3, delay=1, backoff=2)
        print(f"Kết quả: {res}")
    except Exception as e:
        print(f"Thất bại cuối cùng: {e}")
