import threading
import time

'''
Function to perform intensive arithmetic operations indefinitely,
used to stress the CPU.
'''
def stress_cpu():
    while True:
        x = 0
        for i in range(1000000):
            x += i * i

'''
Main function to start multiple threads running the CPU stress function.
'''
def main():
    num_threads = threading.active_count()  # Current number of active threads
    max_threads = 8  # You can adjust this to the number of CPU cores/threads

    print(f"Starting {max_threads} threads to stress the CPU...")
    threads = []
    for _ in range(max_threads):
        t = threading.Thread(target=stress_cpu)
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Terminating the program...")

if __name__ == "__main__":
    main()
