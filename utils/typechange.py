

def chg_type(nodetype:list):
    new_list = []
    for i in nodetype:
        if i == 'ss':
            new_list.append('shodowsocks')
        if i == 'ssr':
            new_list.append('shodowsocksR')
        elif i == 'vmess':
            new_list.append('VMess')
        elif i == 'trojan':
            new_list.append('Trojan')
        elif i == 'http':
            new_list.append('Http')
        elif i == 'socks5':
            new_list.append('Socks5')
        elif i == 'hysteria':
            new_list.append('Hysteria')
        else:
            new_list.append('unknown')
    return new_list


