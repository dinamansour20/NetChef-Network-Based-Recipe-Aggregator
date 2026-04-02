#!/usr/bin/env python3
from scapy.all import *
from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.dns import DNS, DNSQR, DNSRR
import argparse
import datetime
import signal
import sys

# Global variables
packet_count = 0
running = True


def signal_handler(sig, frame):
    global running
    print("\nStopping packet capture...")
    running = False


def get_protocol_name(packet):
    if packet.haslayer(TCP):
        return "TCP"
    elif packet.haslayer(UDP):
        return "UDP"
    elif packet.haslayer(ICMP):
        return "ICMP"
    else:
        return "OTHER"


def process_dns(packet):
    if packet.haslayer(DNSQR):  # DNS Question Record
        dns = packet[DNS]
        query = dns[DNSQR].qname.decode('utf-8')
        return f"DNS Query: {query}"
    elif packet.haslayer(DNSRR):  # DNS Resource Record
        dns = packet[DNS]
        if dns.an and isinstance(dns.an, DNSRR):
            return f"DNS Response: {dns.an.rdata}"
    return None


def process_http(packet):
    if packet.haslayer(HTTPRequest):
        http = packet[HTTPRequest]
        host = http.Host.decode('utf-8') if http.Host else "Unknown Host"
        path = http.Path.decode('utf-8') if http.Path else "/"
        return f"HTTP Request: {host}{path}"
    elif packet.haslayer(HTTPResponse):
        return f"HTTP Response: Status {packet[HTTPResponse].Status_Code.decode('utf-8')}"
    return None


def process_tcp(packet):
    if packet.haslayer(TCP):
        tcp = packet[TCP]
        flags = tcp.sprintf("%flags%")
        return f"TCP {packet[IP].src}:{tcp.sport} -> {packet[IP].dst}:{tcp.dport} [{flags}]"
    return None


def packet_handler(packet):
    global packet_count
    packet_count += 1

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    protocol = get_protocol_name(packet)
    length = len(packet)

    # Basic info
    info = f"{timestamp}  {protocol}  len={length}"

    # Get more specific details based on packet type
    details = []

    if packet.haslayer(DNS):
        dns_info = process_dns(packet)
        if dns_info:
            details.append(dns_info)

    if packet.haslayer(HTTPRequest) or packet.haslayer(HTTPResponse):
        http_info = process_http(packet)
        if http_info:
            details.append(http_info)

    if packet.haslayer(TCP):
        tcp_info = process_tcp(packet)
        if tcp_info:
            details.append(tcp_info)

    if packet.haslayer(IP):
        ip_info = f"IP {packet[IP].src} -> {packet[IP].dst}"
        details.append(ip_info)

    # Combine all details
    if details:
        info += "  " + "  ".join(details)

    print(info)


def start_sniffing(interface=None, filter_exp=None, count=0):
    print("Starting packet capture...")
    print("Press Ctrl+C to stop\n")

    # Column headers
    print(f"{'Time':26}  {'Proto':6}  {'Info':}")
    print("-" * 80)

    try:
        if interface:
            sniff(iface=interface, filter=filter_exp, prn=packet_handler,
                  stop_filter=lambda x: not running, count=count)
        else:
            sniff(filter=filter_exp, prn=packet_handler,
                  stop_filter=lambda x: not running, count=count)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Wireshark-like packet sniffer")
    parser.add_argument("-i", "--interface", help="Network interface to sniff on")
    parser.add_argument("-f", "--filter", help="BPF filter expression")
    parser.add_argument("-c", "--count", type=int, default=0,
                        help="Number of packets to capture (0 for unlimited)")

    args = parser.parse_args()

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    start_sniffing(interface=args.interface, filter_exp=args.filter, count=args.count)

    print(f"\nCaptured {packet_count} packets.")


if __name__ == "__main__":
    main()
