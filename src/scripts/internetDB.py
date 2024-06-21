# scripts/internetdb.py
import requests
import socket

def format_list(list2format):
    formated_text = "  "
    counter = 0
    if len(list2format) == 0:
        formated_text = "  Nothing here..."
        return formated_text
    elif len(str(list2format[0])) < 6:
        row_length = 5
    else:
        row_length = 3
    for list_item in list2format:
        counter += 1
        formated_text += f"{list_item}, "
        if counter == row_length:
            counter = 0
            formated_text += "\n  "
    return formated_text

def resolve_domain(domain):
    try:
        ip_addresses = socket.gethostbyname_ex(domain)[2]
        return ip_addresses
    except socket.gaierror as e:
        print(f"Error resolving domain {domain}: {str(e)}")
        return []

def internetdb_query(ip_addresses):
    result_txt = f"\nQuery results\n"
    for ip in ip_addresses:
        print(f"[+] Checking IP address: {ip} on InternetDB.")
        url = f"https://internetdb.shodan.io/{ip}"
        query_results = requests.get(url).json()
        if "detail" in query_results:
            result_txt += f"\nValidation Error:\n  {query_results['detail']}\n"
        else:
            result_txt += f"\nTarget IP:\n  {query_results['ip']}\n"
            result_txt += f"\nTarget Ports:\n{format_list(query_results['ports'])}\n"
            result_txt += f"\nTarget Tags:\n{format_list(query_results['tags'])}\n"
            result_txt += f"\nTarget Hostnames:\n{format_list(query_results['hostnames'])}\n"
            result_txt += f"\nTarget Vulns:\n{format_list(query_results['vulns'])}\n"
    return result_txt
