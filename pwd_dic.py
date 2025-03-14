def low_pwd():
    low_path = 'wifi_passwd.txt'

    with open(low_path,"r",encoding='utf-8') as f:
        low_list = [i.strip() for i in f]
    return low_list
