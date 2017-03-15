import datetime
import os
import requests
from subprocess import check_output
import pyshark
import datetime
import sys


def get_interfaces():
    tsharkCall = '"' +os.environ["ProgramFiles"]+'/Wireshark/tshark.exe"' +" -D "+os.getcwd()
    proc = check_output(tsharkCall, shell=True)  # Note tshark must be in $PATH
    decoded = proc.decode('ascii')
    interfaces = decoded.splitlines()
    for interface in interfaces:
        print(interface)
    return interfaces


def get_ip_version(packet):
    for layer in packet.layers:
        if layer._layer_name == 'ip':
            return 4
        elif layer._layer_name == 'ipv6':
            return 6


def table_packets(capture):
    col_dict = []
    for packet in capture:
        if packet.transport_layer == 'TCP':
            ip = None
            ip_version = get_ip_version(packet)
            if ip_version == 4:
                ip = packet.ip
            elif ip_version == 6:
                ip = packet.ipv6

            time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           # print("\n--------- COL INFO ---------")
            tcp_dict = [{'Time': time_stamp, 'Source IP': ip.src, 'Dest. IP': ip.dst, 'Protocol': packet.transport_layer,
                        'Source MAC': packet.eth.src, 'Dest. MAC': packet.eth.dst,
                        'Source Port': packet.tcp.srcport, 'Dest. Port': packet.tcp.dstport
                        }]
            col_dict.append(tcp_dict)

        elif packet.transport_layer == 'UDP':
            #udp = parse_udp(packet)
            #print(udp)
            ip = None
            ip_version = get_ip_version(packet)
            if ip_version == 4:
                ip = packet.ip
            elif ip_version == 6:
                ip = packet.ipv6
            time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           # print("\n--------- COL INFO ---------")
            udp_dict = [{'Time': time_stamp, 'Source IP': ip.src, 'Dest. IP': ip.dst, 'Protocol': packet.transport_layer,
                        'Source MAC': packet.eth.src, 'Dest. MAC': packet.eth.dst,
                        'Source Port': packet.udp.srcport, 'Dest. Port': packet.udp.dstport
                        }]
            col_dict.append(udp_dict)
    return col_dict


def packet_dump(capture):
    try:
        all_ip, all_eth, all_tcp, all_udp, all_http = ([] for i in range(5))
        merged_list = []
        for packet in capture:
            print("\n************ PACKET ***************")
            eth_info = parse_eth(packet)
            print(eth_info)

            ip_version = get_ip_version(packet)
            if ip_version == 4:
               # ip = packet.ip
                ip_info = parse_ip(packet, ip_version)
                print(ip_info)
                #icmp_info = parse_icmp(packet)
                #print(icmp_info)

            elif ip_version == 6:
                #ip = packet.ip
                ip_info = parse_ip(packet, ip_version)
                print(ip_info)

            if packet.transport_layer == 'TCP':
                tcp_info = parse_tcp(packet)
                print(tcp_info)
                table_info = (parse_table(packet, ip_version))
                print(table_info)
                if packet.highest_layer == 'HTTP':
                    http_info = parse_http(packet)
                    print(http_info)
                    return (eth_info, ip_info, table_info, tcp_info, http_info)

            elif packet.transport_layer == 'UDP':
                udp_info = parse_udp(packet)
                print(udp_info)
                table_info = (parse_table(packet, ip_version))
                print(table_info)

                if packet.highest_layer == 'HTTP':
                    http_info = parse_http(packet)
                   # print(http_info)
                    return (eth_info, ip_info, table_info, udp_info, http_info)

            elif packet.transport_layer == None:
                #table_info = parse_table(packet, ip_version)
                print('Transport Layer = None')
                #print(table_info)
            print("\n***************  ***************")
            merged_list += table_info
            print("MERGED LIST", merged_list)

        return (eth_info, ip_info, table_info)

    except OSError as error:
        print("OS Error: {0}".format(error))
    except ValueError:
        print("TABLE INFO CAPTURE ERROR")
    except:
        print("Unexpected Error", sys.exc_info()[0])
        raise


def parse_table(packet, ip_version):
    try:
        col_dict = []
        print("\n---------TABLE INFO ----------")
        if ip_version == 4:
            if packet.transport_layer == 'TCP':
                time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                table_dict = {
                    'Time': time_stamp, 'Source IP': packet.ip.src, 'Dest. IP': packet.ip.dst, 'Protocol': packet.transport_layer,
                     'Source MAC': packet.eth.src, 'Dest. MAC': packet.eth.dst,
                     'Source Port': packet.tcp.srcport, 'Dest. Port': packet.tcp.dstport
                }
                col_dict.append(table_dict)
            elif packet.transport_layer == 'UDP':
                time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                table_dict = {
                    'Time': time_stamp, 'Source IP': packet.ip.src, 'Dest. IP': packet.ip.dst,
                    'Protocol': packet.transport_layer,
                    'Source MAC': packet.eth.src, 'Dest. MAC': packet.eth.dst,
                    'Source Port': packet.udp.srcport, 'Dest. Port': packet.udp.dstport
                }
                col_dict.append(table_dict)
        elif ip_version == 6:
            if packet.transport_layer == 'TCP':
                time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                table_dict = {
                    'Time': time_stamp, 'Source IP': packet.ipv6.src.upper(), 'Dest. IP': packet.ipv6.dst.upper(),
                    'Protocol': packet.transport_layer,
                    'Source MAC': packet.eth.src, 'Dest. MAC': packet.eth.dst,
                    'Source Port': packet.tcp.srcport, 'Dest. Port': packet.tcp.dstport
                }
                col_dict.append(table_dict)
            elif packet.transport_layer == 'UDP':
                time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                table_dict = {
                    'Time': time_stamp, 'Source IP': packet.ipv6.src.upper(), 'Dest. IP': packet.ipv6.dst.upper(),
                    'Protocol': packet.transport_layer,
                    'Source MAC': packet.eth.src, 'Dest. MAC': packet.eth.dst,
                    'Source Port': packet.udp.srcport, 'Dest. Port': packet.udp.dstport
                }
                col_dict.append(table_dict)
        return col_dict

    except OSError as error:
        print("OS Error: {0}".format(error))
    except ValueError:
        print("TABLE INFO CAPTURE ERROR")
    except:
        print("Unexpected Error", sys.exc_info()[0])
        raise


def parse_eth(packet):
    try:
        print("\n---------ETH INFO ----------")
        eth_type = {
            '0x0800': 'Internet Protocol version 4', '0x0806': 'Address Resolution Protocol (ARP)', '0x0842': 'Wake-on-LAN',
            '0x8035': 'Reverse Address Resolution Protocol (RARP)',
            '0x8100': 'VLAN-tagged frame (IEEE 802.1Q) & Shortest Path Bridging IEEE 802.1aq',
            '0x86DD': 'Internet Protocol version 6',
            '0x8808': 'Ethernet flow control', '0x8809': 'Slow Protocols (IEEE 802.3)',
            '0x8863': 'PPPoE Discovery Stage',
            '0x8864': 'PPPoE Session Stage', '0x8870': 'Jumbo Frames',
            '0x888E': 'EAP over LAN (IEEE 802.1X)',
            '0x889A': 'HyperSCSI (SCSI over Ethernet)', '0x88A8': 'Provider Bridging (IEEE 802.1ad)'
                                                                  '& Shortest Path Bridging IEEE 802.1aq',
            '0x88CC': 'Link Layer Discovery Protocol (LLDP)', '0x88E5': 'MAC Security (IEEE 802.1ae)',
            '0x88F7': 'Precision Time Protocol (IEEE 1558)', '0x8906': 'Fiber Channel over Ethernet(FCOE)',
            '0x8914': 'FCoE Initialization Protocol'
        }

        eth_info = {
            'Address': packet.eth.addr.upper(),
            'Source Address': packet.eth.src.upper(),
            'Destination Address': packet.eth.dst.upper(),
            'Protocol': packet.eth.layer_name.upper(),
            #'Padding': packet.eth.padding,
            'Type': packet.eth.type
        }
        return eth_info
    except OSError as error:
        print("OS Error: {0}".format(error))
    except ValueError:
        print("ETH CAPTURE ERROR")
    except:
        print("Unexpected Error", sys.exc_info()[0])
        raise


def parse_ip(packet, ip_version):
    try:
        if ip_version == 4:
            print("\n---------IPv4 INFO ----------")
            ip_info = {
                'Version': packet.ip.version, 'Header Length': packet.ip.hdr_len, 'Type of Service': 'N/A',
                'Total Length': packet.ip.len, 'Identification': packet.ip.id, 'Protocol' : packet.ip.layer_name,
                'Flags': {'RB': packet.ip.flags_rb, 'D': packet.ip.flags_df, 'M': packet.ip.flags_mf},
                'Fragment Offset': packet.ip.frag_offset, 'Time To Live': packet.ip.ttl, 'Protocol used': packet.ip.proto,
                'Header Checksum': packet.ip.checksum, 'Checksum Status': packet.ip.checksum_status,
                'Source Address': packet.ip.src, 'Destination Address': packet.ip.dst
            }
            return ip_info
        elif ip_version == 6:
            print("\n---------IPv6 INFO ----------")
            ip_info = {
                'Version': ip_version,
                'Traffic Class': packet.ipv6.tclass,
                'Traffic Class DSCP': packet.ipv6.tclass_dscp,
                'Traffic Class ECN': packet.ipv6.tclass_ecn,
                'Flow Label': packet.ipv6.flow,
                'Payload Length': packet.ipv6.plen,
                'Next Header': packet.ipv6.nxt,
                'Hop Limit': packet.ipv6.hlim,
                'Source Address': packet.ipv6.src.upper(),
                'Destination Address': packet.ipv6.dst.upper()
            }
            return ip_info
    except OSError as error:
        print("OS Error: {0}".format(error))
    except ValueError:
        print("IPV4/6 CAPTURE ERROR")
    except:
        print("Unexpected Error", sys.exc_info()[0])
        raise


def parse_tcp(packet):
    try:
        print("\n---------TCP INFO ----------")
        tcp_info = {'Source Port': packet.tcp.srcport, 'Dest. Port': packet.tcp.dstport, 'Sequence Number': packet.tcp.seq,
                    'Acknowledgement': packet.tcp.ack, 'Data Offset': 'N/A', 'Reserve': 'N/A',
                    'Flags': {'CWR': packet.tcp.flags_cwr, 'ECN': packet.tcp.flags_ecn, 'URG': packet.tcp.flags_urg,
                              'ACK': packet.tcp.flags_ack, 'PSH': packet.tcp.flags_push, 'RST': packet.tcp.flags_reset,
                              'SYN': packet.tcp.flags_syn, 'FIN': packet.tcp.flags_fin
                              },
                    'Window Size': packet.tcp.window_size, 'Window Size Value': packet.tcp.window_size_value,
                    'Header Length': packet.tcp.hdr_len, 'Protocol': packet.tcp.layer_name.upper()
                    , 'Checksum': packet.tcp.checksum, 'Checksum Status': packet.tcp.checksum_status, 'Urgent Pointer': packet.tcp.urgent_pointer
                    #, 'Segment Data': packet.tcp.segment_data
                    }  # tcp_dict
        return tcp_info
    except OSError as error:
        print("OS Error: {0}".format(error))
    except ValueError:
        print("TCP CAPTURE ERROR")
    except:
        print("Unexpected Error", sys.exc_info()[0])
        raise


def parse_udp(packet):
    try:
        print("\n---------UDP INFO ----------")
        udp_info = {
            'Source Port': packet.udp.srcport,
            'Dest. Port': packet.udp.dstport,
            'Protocol': packet.udp.layer_name.upper(),
            'Length': packet.udp.length,
            'Checksum': packet.udp.checksum,
            'Checksum Status': packet.udp.checksum_status
        }
        return udp_info
    except OSError as error:
        print("OS Error: {0}".format(error))
    except ValueError:
        print("UDP CAPTURE ERROR")
    except:
        print("Unexpected Error", sys.exc_info()[0])
        raise


def parse_http(packet):
    try:
        print("\n---------HTTP INFO ----------")
        http_info = {
            'Connection': packet.http.connection,
            'Protocol': packet.http.layer_name.upper(),
            'Request Version': packet.http.request_version,
            'Request Method': packet.http.request_method,
            'Request Number': packet.http.request_number
        }
        return http_info
    except OSError as error:
        print("OS Error: {0}".format(error))
    except ValueError:
        print("HTTP CAPTURE ERROR")
    except:
        print("Unexpected Error", sys.exc_info()[0])
        raise


def parse_icmp(packet):
    try:
        # TODO CHECK FOR ICMPV6
    #if icmp_version == None:
        print("\n---------ICMP INFO ----------")
        icmp_info = {
            #'Type': packet.icmp.checksum
            #'Code': packet.icmp.code,
            #'Checksum': packet.icmp.checksum,
        }
        return icmp_info

    except OSError as error:
        print("OS Error: {0}".format(error))
    except ValueError:
        print("ICMP CAPTURE ERROR")
    except:
        print("Unexpected Error", sys.exc_info()[0])
        raise

'''
def main(file):
    capture = pyshark.FileCapture(file)
    (eth_info, ip_info, table_info, tcp_info, udp_info) = packet_dump(capture)
    # TODO NEED TO RETURN MERGED LIST, TO BE USED TABLE INFO
    print("IN MAIN")
    print(len(table_info))
    print(table_info)
   # print(merged_list)
    

if __name__== '__main__':
    main(file="test_http.pcap")
    '''


