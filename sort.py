#!/usr/bin/python3

import os
import shutil
import http.server 
import socketserver
import cgi
import time
import zipfile

from multiprocessing import Process, Lock

from sort_medooze import *
from sort_qlog import *
from sort_bitrate import *

mutex = Lock()

def update_average(rep, parse_qlog):
    parent = rep + "/.."
    average_name = "average"
    average_dir = parent + "/" + average_name
    
    if not average_name in os.listdir(parent):
        os.mkdir(parent + "/average")

    #     for f in os.listdir(rep):
    #         shutil.copyfile(rep + '/' + f, average_dir + '/' + f)
            
    #     return None

    n = len(os.listdir()) - 1 # - average

    p_bitrate = Process(target = stats_line_bitrate, args=(average_dir, rep, n))
    p_bitrate.start()
    # stats_line_bitrate(average_dir, rep, n)
    
    p_medooze = Process(target = stats_line_medooze, args=(average_dir, rep, n))
    p_medooze.start()
    # stats_line_medooze(average_dir, rep, n)

    if parse_qlog:
        p_qlog = Process(target = stats_line_qlog, args=(average_dir, rep, n))
        p_qlog.start()
        p_qlog.join()
        # stats_line_qlog(average_dir, rep, n)
    
    p_bitrate.join()
    p_medooze.join()

    print("Finish")

def handle_new_exp(exp, impl, cc, reliability, zip_file):
    with mutex:
        print("Sorting :", exp, impl, cc, reliability)
        print(zip_file, os.getcwd())

        path = 'exps/' + exp + '/' + impl + '/' + reliability + '/' + cc

        parse_qlog = impl != 'udp' and cc != 'none' and (not 'dgram' in reliability)
    
        if not os.path.exists(path):
            os.makedirs(path)

        shutil.move(zip_file, path)

        cwd = os.getcwd()
        os.chdir(path)
    
        repet_num = len([r for r in os.listdir() if 'repet' in r]) + 1
        repet_dir = 'repet%d' % repet_num

        os.mkdir(repet_dir)

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(repet_dir)

        os.remove(zip_file)
        os.chdir(repet_dir);

        for f in os.listdir():
            if ".qlog" in f:
                os.rename(f, impl + '.qlog')
            if "quic-relay" in f and ".csv" in f:
                os.rename(f, 'medooze.csv')

        os.chdir('..')
        update_average(repet_dir, parse_qlog)
        os.chdir(cwd)
        print("update done")
        
class Handler(http.server.SimpleHTTPRequestHandler):
        
    def do_POST(self):
        print("post")
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     }
        )

        exp = form.getvalue("exp")
        impl = form.getvalue("impl")
        cc = form.getvalue("cc")
        reliability = form.getvalue("reliability")
        file_content = form.getvalue("file")

        filename = 'exp_%s.zip' % str(time.time()).replace('.', '_')
        with open(filename, 'wb') as output_file:
            output_file.write(file_content)
        
        self.send_response(201, 'Created')
        self.end_headers()
        reply_body = 'Saved "%s"\n' % filename
        self.wfile.write(reply_body.encode('utf-8'))

        p = Process(target = handle_new_exp, args = (exp, impl, cc, reliability, filename))
        p.start()
            # handle_new_exp(exp, impl, cc, reliability, filename)
            # exit()        
        
def run_http_server():
    print("run server")
    server_address = ('', 4455)
    handler = Handler # http.server.BaseHTTPRequestHandler
    httpd = http.server.HTTPServer(server_address, handler)
    httpd.serve_forever()
    

if __name__ == "__main__":
    run_http_server()

    # tab = [(0,1), (0.01, 2), (0.1, 3), (1, 2), (1.02, 3), (1.04, 5)]
    # print(convert_to_fixed_number_of_points(tab))
    # tab = [[0,1,2], [3,4,5], [6,7,8], [9]]
    # tab2 = [[0,1,2], [3,4,5], [6,7,8], [9,10,11]]
    # tab3 = [[0,1,2], [3,4,5], [6,7,8], [9,10]]

    # print(tab, tab2, tab3, sep='\n')
    # trim_arrays([tab, tab2, tab3])
    # print(tab, tab2, tab3, sep='\n')
