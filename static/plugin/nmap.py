import nmap3

nmap = nmap3.NmapScanTechniques()


def tcp_scan(target):
    try:
        # output = nmap.run_command(['nmap', '-oX', '-', target])
        # xml_root = nmap.get_xml_et(output)
        # return nmap.filter_top_ports(xml_root)
        return nmap.nmap_tcp_scan(target)
    except Exception as e:
        print(e)
        return []


def os_scan(target):
    return nmap.nmap_os_detection(target)


if __name__ == '__main__':
    print(os_scan('172.22.147.138'))

