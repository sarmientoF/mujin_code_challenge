# import threading
# from concurrent.futures import ThreadPoolExecutor, as_completed


# x = 0


# def increment():
#     global x
#     x = 0
#     for _ in range(100_000):
#         x += 1
#     return x


# with ThreadPoolExecutor(max_workers=2) as executor:
#     future_increment = {executor.submit(increment): i for i in range(2)}
#     for future in as_completed(future_increment):
#         result = future_increment[future]
#         try:
#             data = future.result()
#         except Exception as exc:
#             print("%r generated an exception: %s" % (result, exc))
#         else:
#             print("%r page is %d bytes" % (result, data))
#     print(x)


from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import math
import time

PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419,
]


def is_prime(n: int):
    if n < 2:
        False
    if n == 2:
        True
    if n % 2 == 0:
        return False

    sq = math.floor(math.sqrt(n))
    for i in range(3, sq, 2):
        if n % i == 0:
            return False
    return True


def main():
    # with ProcessPoolExecutor() as executor:
    # for number, prime in zip(PRIMES, executor.map(is_prime, PRIMES)):
    #     print(f"Number {number} -> Prime: {prime}")
    process_start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(is_prime, n=prime): prime for prime in PRIMES}
        for future in as_completed(futures):
            number = futures[future]
            isPrime = future.result()
            print(f"{number} is prime: {isPrime}")
    print(f"Time for process: {time.time() - process_start}")

    thread_start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(is_prime, n=prime): prime for prime in PRIMES}
        for future in as_completed(futures):
            number = futures[future]
            isPrime = future.result()
            print(f"{number} is prime: {isPrime}")
    print(f"Time for process: {time.time() - thread_start}")

if __name__ == "__main__":
    main()
