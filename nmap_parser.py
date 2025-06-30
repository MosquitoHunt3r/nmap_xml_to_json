from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
import json
import xmltodict
import re
import sys
import argparse

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def xml_to_json(file_path):
    if isinstance(file_path, str):
        with open(file_path, 'r') as xml_file:
            soup = BeautifulSoup(xml_file, 'html.parser')
    else:
        soup = BeautifulSoup(file_path, 'html.parser')
        
    host_elements = soup.find_all('host')

    hosts = []
    for host in host_elements:
        ## // Variables only used for searching
        address_element = host.find('address')
        status_element = host.find('status')
        hostnames_element = host.find('hostnames')
        if hostnames_element:
            hostname_elements = hostnames_element.find_all('hostname')
        else:
            hostname_elements = []
        ports_element = host.find('ports')
        if ports_element:
            port_elements = ports_element.find_all('port')
        else:
            port_elements = []
        hostscripts_element = host.find('hostscript')
        ## \\
        ## // Variables that are returned
        address = {
            "addr": address_element.get('addr'),
            "addrtype": address_element.get('addrtype')
        }
        status = {"state": status_element.get('state')}
        hostnames = []
        ports = []
        hostscripts = []
        ## \\
        for name in hostname_elements:
            hostnames.append({
                "name": name.get('name'),
                "type": name.get('type')
            })
        for port in port_elements:
            service = None
            scripts = []

            state = port.find('state')["state"]
            if state == 'closed':
                continue
            elif state == 'filtered':
                continue
            service_element = port.find('service')
            script_elements = host.find_all('script')
            try:
                service = {
                    "name": service_element.get('name'),
                    "product": service_element.get('product'),
                    "version": service_element.get('version'),
                    "extrainfo": service_element.get('extrainfo'),
                    "ostype": service_element.get('ostype'),
                    "method": service_element.get('method'),
                    "conf": service_element.get('conf'),
                    "cpe": service_element.get('cpe')
                }
                for script in script_elements:
                    json_string = json.dumps(xmltodict.parse(script.prettify()))
                    json_string = re.sub(r'"@(\w+)":', r'"\1":', json_string)
                    json_string = re.sub(r'"#text":', r'"value":', json_string)
                    json_string = re.sub(r'"elem":', r'"element":', json_string)
                    scripts.append(json.loads(str(json_string))['script'])
            except AttributeError:
                pass
            ports.append({
                "protocol": port.get('protocol'),
                "portid": port.get('portid'),
                "service": service,
                "scripts": scripts
            })
        if hostscripts_element:
            for script in hostscripts_element.find_all('script'):
                json_string = json.dumps(xmltodict.parse(script.prettify()))
                json_string = re.sub(r'"@(\w+)":', r'"\1":', json_string)
                json_string = re.sub(r'"#text":', r'"value":', json_string)
                json_string = re.sub(r'"elem":', r'"element":', json_string)
                hostscripts.append(json.loads(str(json_string))['script'])            
        host = {
            "address": address,
            "status": status,
            "hostnames": hostnames,
            "ports": ports,
            "hostscripts": hostscripts
        }
        hosts.append(host)

    return hosts

def output_result(hosts, output_file=None, no_print=None):
    result = json.dumps(hosts, indent=4)

    if not no_print:
        print(result)
    
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(result)
            print(f"Result has been saved to {output_file}", file=sys.stderr)
        except IOError as e:
            print(f"Error writing to file {output_file}: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='Convert Nmap XML output into JSON output')
    parser.add_argument('-f', '--file', help='Input XML file path (If not specified, reads from stdin)')
    parser.add_argument('-o', '--output', help='Output JSON file path (Writes to file specified file)')
    parser.add_argument('--no-print', action='store_true', help="Don't print to screen (Default=print)")
    args = parser.parse_args()
    
    if args.file:
        try:
            result = xml_to_json(args.file)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        if not sys.stdin.isatty():
            result = xml_to_json(sys.stdin)
        else:
            print("No input provided. Use -f FILE or pipe data to stdin.", file=sys.stderr)
            sys.exit(1)

    output_result(result, args.output, args.no_print)

if __name__ == "__main__":
    main()