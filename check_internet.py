import requests
import socket

def check_internet():
    print("Checking internet connectivity...")
    try:
        # 1. Resolve popcat.xyz
        print("Resolving api.popcat.xyz...")
        ip = socket.gethostbyname("api.popcat.xyz")
        print(f"Resolved api.popcat.xyz to {ip}")
        
        # 2. Test request to popcat with User-Agent
        print("Requesting api.popcat.xyz with User-Agent...")
        url_popcat = "https://api.popcat.xyz/chatbot?msg=Hi&owner=Teera&botname=TeeraBot"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            resp = requests.get(url_popcat, headers=headers, timeout=5)
            print(f"Popcat status: {resp.status_code}")
        except:
            print("Popcat: TIMEOUT/FAILED")

        # 3. Test request to adviceslip (Different service)
        print("Requesting api.adviceslip.com...")
        try:
            resp = requests.get("https://api.adviceslip.com/advice", timeout=5)
            print(f"AdviceSlip status: {resp.status_code}")
            print(f"Advice content: {resp.text[:50]}")
        except:
            print("AdviceSlip: TIMEOUT/FAILED")

        # 4. Test request to simsimi (Different service)
        print("Requesting api.simsimi.net...")
        try:
            resp = requests.get("https://api.simsimi.net/v2/?text=Hi&lc=en", timeout=5)
            print(f"SimSimi status: {resp.status_code}")
            print(f"SimSimi response: {resp.text[:50]}")
        except:
            print("SimSimi: TIMEOUT/FAILED")
        
    except Exception as e:
        print(f"Connectivity error: {e}")

if __name__ == "__main__":
    check_internet()
