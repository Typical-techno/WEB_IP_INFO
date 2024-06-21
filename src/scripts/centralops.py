# scripts/centralops.py
import re
import sys
import time
import requests
from bs4 import BeautifulSoup

def is_ipv4(ip_str):
    # Regular expression for IPv4 address
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    return bool(re.match(ipv4_pattern, ip_str))

def is_ipv6(ip_str):
    # Regular expression for IPv6 address
    ipv6_pattern = r'^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,6}:|:[0-9a-fA-F]{1,4}|:)$'
    return bool(re.match(ipv6_pattern, ip_str))

def remove_image_links(text):
    # Function to remove image links (<img> tags) from text
    soup = BeautifulSoup(text, 'html.parser')
    for img in soup.find_all('img'):
        img.extract()
    return soup.get_text()

def address_lookup(soup):
    addresses_list = []
    addresses_lookup_txt = ""

    canonical_name = soup.find('td', string='canonical name')
    if canonical_name:
        canonical_name = canonical_name.find_next('td').find('a').text.strip()
        addresses_lookup_txt += f"\n{'='*80}\n\nAddress Lookup\n{'-'*15}\nCanonical Name: {canonical_name}"

    addresses = soup.find('td', string='addresses')
    if addresses:
        addresses = addresses.find_next('td').find_all('span', class_='ipaddr')
        addresses_list = [ip.text.strip() for ip in addresses]

        for ip in addresses_list:
            if is_ipv4(ip):
                addresses_lookup_txt += f"\nIPv4 Address: {ip}"
            elif is_ipv6(ip):
                addresses_lookup_txt += f"\nIPv6 Address: {ip}"

    # Remove image links from the generated text
    addresses_lookup_txt = remove_image_links(addresses_lookup_txt)

    return addresses_list, addresses_lookup_txt

def domain_whois_record(soup):
    domain_whois_txt = "\n" + "="*80 + "\n\nDomain Whois Record\n" + "-"*19
    domain_whois = soup.find('h3', string='Domain Whois record')
    if domain_whois:
        domain_whois = domain_whois.find_next('pre').text.strip()
        domain_whois = domain_whois.replace('   ', "- ")
        domain_whois_txt += "\n" + domain_whois
    return domain_whois_txt

def network_whois_record(soup):
    net_whois_txt = "\n" + "="*80 + "\n\nNetwork Whois Record\n" + "-"*20
    network_whois = soup.find('h3', string='Network Whois record')
    if network_whois:
        network_whois = network_whois.find_next('pre').text.strip()
        net_whois_txt += "\n" + network_whois
    return net_whois_txt

def service_scan(soup):
    scan_results = "\n" + "=" * 80 + "\n\nService/Port Scan\n" + "-"*17
    service_scan_table = soup.find('h3', string='Service scan')
    if service_scan_table:
        for _ in range(6):
            service_scan_table = service_scan_table.find_next('table')
            scan_results += f"\n{'* '*40}\n{service_scan_table.text.strip().replace('<br/>', '')}"
        scan_results += f"\n\n{'='*80}"
    return scan_results

def generate_txt_report(html_report):
    soup = BeautifulSoup(html_report, 'html.parser')
    
    txt_report = ""  # Initialize txt_report here
    
    addresses_list, addresses_lookup_txt = address_lookup(soup)
    txt_report += addresses_lookup_txt

    domain_whois_txt = domain_whois_record(soup)
    txt_report += domain_whois_txt
    
    net_whois_txt = network_whois_record(soup)
    txt_report += net_whois_txt
    
    service_scan_txt = service_scan(soup)
    txt_report += service_scan_txt + "\n"
    
    return txt_report, addresses_list

def centralops_query(target, get_request):
    loading_message = "[+] Checking on CentralOps, please wait..."
    print(loading_message)

    opts = "&dom_whois=true&dom_dns=true&traceroute=true&net_whois=true&svc_scan=true"
    cops = f"https://centralops.net/co/DomainDossier.aspx?addr={target}{opts}"
    c_headers = {
        'Host': 'centralops.net',
        'Cookie': 'tool-settings=DD-dd=1&DD-dw=1&DD-nw=1&DD-ss=0&DD-tr=0&dn=google.com',    
        'Sec-Ch-Ua': '"Not A(Brand";v="24", "Chromium";v="110"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': "Windows",
        'Upgrade-Insecure-Requests': '1',      
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'close'
    }

    html_report = get_request(cops, headers=c_headers).text
    print("Waiting for response...")

    if "Could not find an IP address for this domain name." in html_report:
        error_message = f"[-] There was a problem with: {target} while using CentralOps. Exiting..."
        print(error_message)
        return error_message, []
    else:
        txt_report, addresses_list = generate_txt_report(html_report)
        return txt_report, addresses_list


# Example usage:
if __name__ == "__main__":
    target_domain = "example.com"
    report, addresses = centralops_query(target_domain, requests.get)
    print(report)  # Example: Output the report
