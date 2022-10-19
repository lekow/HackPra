#!/usr/bin/env python
# encoding: utf-8
"""
"  A pure python ping implementation using raw socket.
"  ICMP messages can only be sent from processes running as root.
"""

import os, sys, socket, struct, select, time, string, argparse
ICMP_ECHO_REQUEST = 8
parser = argparse.ArgumentParser(description='ping')
parser.add_argument('-t','--timeout', type=float, default=2, help= 'timeout in seconds')
parser.add_argument('-c','--count', type=int, default=-1, help='number of pings (-1 = infinity)')
parser.add_argument('-f','--logfile', type=str, default="", help='path to logfile (if not stdout)')
parser.add_argument('-m','--logmsg', type=str, default="PING (icmp_req) 56(84) bytes of data.", help='log title message')
parser.add_argument('host', metavar='<host>', type=str, help='remote host')
args = parser.parse_args()


def checksum(source_string):
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2
    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff
    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receive_one_ping(my_socket, ID, timeout):
    timeLeft = timeout
    while True:
        startedSelect = time.time()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:
            return
        timeReceived = time.time()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader)
        if packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return


def send_one_ping(my_socket, dest_addr, ID):
    dest_addr  =  socket.gethostbyname(dest_addr)
    my_checksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", time.time()) + data
    my_checksum = checksum(header + data)
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1)
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1))


def do_one(dest_addr, timeout):
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error, (errno, msg):
        if errno == 1:
            msg = msg + ( ": You have to be root.")
            raise socket.error(msg)
        raise
    my_ID = os.getpid() & 0xFFFF
    send_one_ping(my_socket, dest_addr, my_ID)
    delay = receive_one_ping(my_socket, my_ID, timeout)
    my_socket.close()
    return delay


def log_it(fd, msg):
    if (fd != 0):
        fd.write(msg)
    else:
        sys.stdout.write(msg)


def verbose_ping(dest_addr, timeout, count, logfile, logmsg):
    fd = 0

    if (logfile != ""):
        # save previous privileges
        euid, egid = os.geteuid(), os.getegid()
        # lower privileges to caller uid/gid
        os.seteuid(os.getuid()); os.setegid(os.getgid());

        # try to open the file
        try:
            fd = open(logfile, "a")
        except Exception:
            pass

        # change privileges to old privileges
        os.seteuid(euid); os.setegid(egid);

    log_it(fd, logmsg); log_it(fd, "\n")
    x = 0
    while (x != count):
        x = x + 1
        try:
           log_it(fd, "ping %s: " % dest_addr)
           try:
               delay  =  do_one(dest_addr, timeout)
           except socket.gaierror, e:
               log_it(fd, "%s\n" % e[1])
               break
           if delay  ==  None:
               log_it(fd, "timeout in %s sec\n" % timeout)
           else:
               delay  =  delay * 1000
               log_it(fd, "time=%0.4f ms\n" % delay)
           time.sleep(1)
        except KeyboardInterrupt:
           break

    # close the file if it was successfully opened
    if (fd != 0):
        fd.close()


if __name__ == '__main__':
    h = args.host
    t = args.timeout
    c = args.count
    f = args.logfile
    m = args.logmsg
    verbose_ping(h, t, c, f, m)
