from tls import TLSConnection
from threading import Thread, Barrier, Lock, active_count
from time import sleep

NUM_CALLS = 2000
TIMEOUT =  10
REFRESH = 0.1


class Counter(object):
    def __init__(self: object) -> None:
        self.__success, self.__failed = 0, 0
        # two locks used as a safe mechanism
        self.__lock_success, self.__lock_failed = Lock(), Lock()

    def success(self: object) -> None:
        # if the lock is acquired, wait; else, increment success counter
        with self.__lock_success:
            self.__success += 1

    def failed(self: object) -> None:
        # if the lock is acquired, wait; else, increment failed counter
        with self.__lock_failed:
            self.__failed += 1

    def get_counters(self: object) -> tuple:
        # return both counter as a tuple
        return self.__success, self.__failed

def main() -> None:
    barrier, counter = Barrier(NUM_CALLS + 1), Counter()

    # create NUM_CALLS number of threads that will connect to 10.0.23.14:443 and wait for all other threads
    for i in range(NUM_CALLS):
        connection = TLSConnection('10.0.23.14', 443)

        print(f'\r[*] Connecting to 10.0.23.14:443 ({i + 1}/{NUM_CALLS} connections)...', end='')

        # create a daemon thread that will execute the do_handshake function with two arguments: the barrier and the counter objects
        thread = Thread(target=connection.do_handshake, args=(barrier, counter), daemon=True)
        thread.start()

    print('\n[*] Initiating handshakes, please wait for the results...')
    barrier.wait()  # start all handshakes simultaneously

    elapsed, start_fail = 0.0, 0.0
    num_success = 0

    for _ in range(int(TIMEOUT / REFRESH)):
        # get and unpack both counters
        success, failed = counter.get_counters()

        print(f'\r[*][{round(elapsed)}s] {success + failed}/{NUM_CALLS} handshakes were made (success={success}, failed={failed}, alive={active_count() - 1}){" " * 5}', end='')

        # if the first failed packet is found, save the number of successful handshakes and the elapsed time
        if failed > 0 and start_fail == 0.0:
            num_success = success
            start_fail = elapsed

        # if all handshakes have succeded or failed before the timeout, exit the loop
        if success + failed == NUM_CALLS:
            break

        sleep(REFRESH)
        elapsed += REFRESH

    # if a failed packed is found and registered by saving it to the start_fail, print the results
    if start_fail != 0.0:
        print(f'\n[*] Handshakes start failing after {num_success} successful handshakes.')
        print(f'[*] Time elapsed before first failed handshake: {start_fail:.1f} seconds.')
        print(f'[*] Maximum number of handshakes per second: {round(num_success / start_fail)}')
    else:
        print(f'\n[*] No failed handshakes were encountered. Please increase the number of calls and try again.')

if __name__ == '__main__':
    main()
