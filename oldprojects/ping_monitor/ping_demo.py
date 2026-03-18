import subprocess

def ping(host="8.8.8.8"):
    result = subprocess.run(["ping", "-n", "4", host], capture_output=True, text=True)
    print(result.stdout)

if __name__ == "__main__":
    ping("google.com")