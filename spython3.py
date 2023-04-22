import os
import ssl
import time
import textwrap
import argparse
from tabulate import tabulate
from OpenSSL import crypto, SSL
from prettytable import PrettyTable
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler

cert_path = "/tmp/selfsigned.crt"
key_path = "/tmp/selfsigned.key"
headers = ["IP Address", "Response Code", "Request Method", "Path", "Query Parameters", "Timestamp"]
table = PrettyTable(headers)
table.align["Response Code"]  = "c"
table.align["Request Method"]  = "c"
table.align = "l"

def createCerts():
    print("[!] Certificate or key file not found. Generating new ones...")
    context = SSL.Context(SSL.TLSv1_2_METHOD)
    pkey = crypto.PKey()
    pkey.generate_key(crypto.TYPE_RSA, 2048)
    cert = crypto.X509()
    cert.get_subject().CN = "h4rithd.com"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(31536000)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(pkey)
    cert.sign(pkey, "sha256")
    with open(cert_path, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(key_path, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))
    os.chmod(cert_path, 0o600)
    os.chmod(key_path, 0o600)

if not os.path.exists(cert_path) and not os.path.exists(key_path):
    createCerts()

parser = argparse.ArgumentParser(
    prog='SPʏᴛʜᴏɴ3.py',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    -------------------------------------------------------------
    -------------- | SPʏᴛʜᴏɴ3 Demon Web Server|------------------
    -------------------------------------------------------------
             _____ ____        __  __               _____
            / ___// __ \__  __/ /_/ /_  ____  ____ |__  /
            \__ \/ /_/ / / / / __/ __ \/ __ \/ __ \ /_ < 
           ___/ / ____/ /_/ / /_/ / / / /_/ / / / /__/ / 
          /____/_/    \__, /\__/_/ /_/\____/_/ /_/____/  
                     /____/                              
                        simple https server using python3
    ______________________________________________________________'''),
    usage='python3 %(prog)s',
    epilog='___________________________________  by h4rithd.com ________'
)
parser.add_argument("-p", "--port", type=int, default=443, help="Port to listen on (default: 443)")
parser.add_argument("-i", "--ip", type=str, default='0.0.0.0', help="IP address to listen on (default: 0.0.0.0)")
args = parser.parse_args()

class HTTPHandler(SimpleHTTPRequestHandler):
    def do_METHOD(self):
        ip_address = self.client_address[0]
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_dict = parse_qs(parsed_path.query)
        query = '&'.join([f"{k}={v[0]}" for k, v in query_dict.items()])

        if self.command in ['POST', 'PUT', 'DELETE']:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            query_dict = parse_qs(post_data.decode())
            query = '&'.join([f"{k}={v[0]}" for k, v in query_dict.items()])

        f = self.send_head()
        if f:
            self.send_response(200)
            self.copyfile(f, self.wfile)
            f.close()
            row = [ip_address, '200', self.command, path, query, time.strftime('%d/%b/%Y %H:%M:%S')]
        else:
            self.send_error(404, "File not found")
            row = [ip_address, '404', self.command, path, query, time.strftime('%d/%b/%Y %H:%M:%S')]

        table.add_row(row)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(table)

    def do_GET(self):
        self.do_METHOD()

    def do_POST(self):
        self.do_METHOD()

    def do_PUT(self):
        self.do_METHOD()

    def do_DELETE(self):
        self.do_METHOD()

httpd = HTTPServer((args.ip, args.port), HTTPHandler)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=cert_path, keyfile=key_path)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("-" * 50)
print(f"\033[92m[+] Server started on https://{args.ip}:{args.port}\033[0m")
httpd.serve_forever()
