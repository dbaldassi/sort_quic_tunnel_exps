#!/usr/bin/python3

import os
import csv
import shutil
import json

latency = [ "0ms", "25ms", "50ms", "100ms" ]
loss = [ "0%", "0.1%", "0.5%", "1%" ]
# cat = [ "bitrate", "quic", "qlog", "medooze" ]

def setup_exp_name():
    for l in loss:
        os.mkdir(l)
        os.chdir(l)
        for d in latency:
            os.mkdir(d)
        os.chdir('..')

def average_bitrate(av_dir, rep_dir, n):
    nmoinsun = n - 1
    
    bitrate_csv = open(rep_dir + '/bitrate.csv', 'r')
    bitrate_lines = [ line for line in csv.reader(bitrate_csv, delimiter=',') ]

    try:
        average_bitrate_csv = open(av_dir + '/bitrate.csv', 'r')
        av_lines = [line for line in csv.reader(average_bitrate_csv, delimiter=',')]

        for row in range(len(av_lines)):
            for col in range(len(av_lines[row])):
                if row < len(bitrate_lines) and col < len(bitrate_lines[row]):
                    av_lines[row][col] = (float(av_lines[row][col]) * nmoinsun + float(bitrate_lines[row][col])) / n

        average_bitrate_csv.close()
    except OSError:
        av_lines = bitrate_lines

    bitrate_csv.close()

    average_bitrate_csv = open(av_dir + '/bitrate.csv', 'w')

    writer = csv.writer(average_bitrate_csv, delimiter=',')

    for row in av_lines:
        writer.writerow(row)

    average_bitrate_csv.close()

def average_quic_sent(av_dir, rep_dir, n):
    nmoinsun = n - 1

    bitrate_csv = open(rep_dir +'/quic.csv')
    bitrate_lines = [line for line in csv.reader(bitrate_csv, delimitier=',')]
    
    try:
        average_bitrate_csv = open(av_dir + '/quic.csv', 'r')
        av_lines = [line for line in csv.reader(average_bitrate_csv, delimitier=',')]

        for row in range(av_lines):
            for col in range(row):
                if row < len(bitrate_lines) and col < len(bitrate_lines[row]):
                    av_lines[row][col] = (float(av_lines[row][col]) * nmoinsun + float(bitrate_lines[row][col])) / n

        average_bitrate_csv.close()
    except OSError:
        av_lines = bitrate_lines

    bitrate_csv.close()

    average_bitrate_csv = open(av_dir + '/quic.csv', 'w')

    writer = csv.writer(average_bitrate_csv, delimiter=',')

    for row in av_lines:
        writer.writerow(row)

    average_bitrate_csv.close()


def parse_qlog_json(file_name):
    rtt = []
    loss = 0
    sent = 0

    with open(file_name) as json_file:        
        try:
            data = json.load(json_file)
        except:
            return rtt

        time_0 = -1

        for trace in data["traces"]:
            for event in trace["events"]:
                try:
                    if event["name"] == "recovery:metrics_updated":
                        if(time_0 == -1):
                            time_0 = event['time']
                        
                        time = event['time'] - time_0
                        d = event["data"]
                        rtt.append([time, d['latest_rtt']])

                        if "lost_packets" in d:
                            loss = d['lost_packets']
                        
                    elif event["name"] == "loss:packets_lost":
                        loss += event["data"]["lost_packets"]
                    elif event["name"] == "transport:packet_sent":
                        sent += 1
                except:
                    pass

    for it in rtt:
        it.append(loss)
        it.append(sent)
                
    return rtt

def parse_qlog_ndjson(file_name):
    rtt = []
    loss = 0
    sent = 0
    
    with open(file_name) as json_file:
        for line in json_file.readlines():
            try:
                json_line = json.loads(line)
            except Exception as error:
                print("JSON line not valid ", error)
                return rtt
            
            try:
                name = json_line['name']
                if name == "recovery:metrics_updated":
                    time = float(json_line['time']) / 1000
                    data = json_line['data']

                    if "latest_rtt" in data:
                        rtt.append([time, data['latest_rtt']])
                    elif "smoothed_rtt" in data:
                        rtt.append([time, data['smoothed_rtt']])
                    elif name == "transport:packet_lost" or name == "recovery:packet_lost":
                        loss += 1
                    elif name == "transport:packet_sent":
                        sent += 1
            except:
                pass

    for it in rtt:
        it.append(loss)
        it.append(sent)

    return rtt
    
def average_qlog(av_dir, rep_dir, n):
    nmoinsun = n - 1

    rtt = []
    
    for f in os.listdir(rep_dir):
        if ".qlog" in f:
            if "mvfst" in f:
                rtt = parse_qlog_json(rep_dir + '/mvfst.qlog')
            else:
                rtt = parse_qlog_ndjson(rep_dir + '/' + f)
            break
        
    if len(rtt) == 0:
        return

    try:
        average_qlog = open(av_dir + '/qlog.csv', 'r')

        lines = csv.reader(average_qlog, delimiter=',')

        count = 0
        for row in lines:
            for col in range(len(row)):
                if count < len(rtt) and col < len(rtt[count]):
                    rtt[count][col] = (float(row[col]) * nmoinsun + rtt[count][col]) / n
            count += 1
    
        average_qlog.close()
    except OSError:
        pass

    average_qlog = open(av_dir + '/qlog.csv', 'w')

    writer = csv.writer(average_qlog, delimiter=',')

    for row in rtt:
        writer.writerow(row)

    average_qlog.close()

def add_value(tab, time, cat, value=1):
    while(time >= len(tab)):
        tab.append([0,0,0,0,0,0,0,0])

    tab[time][cat] += value

class Point:

    def __init__(self, t, v):
        self.time = t
        self.val = v

class Accumulator:

    base = 1000000
    window = 200000
    factor = base / window

    def __init__(self):
        self.accumulated = 0
        self.points = []
    
    def accumulate(self, time, value):
        while not len(self.points) == 0 and self.points[0].time < (time - Accumulator.window):
            self.accumulated -= self.points.pop(0).val

        self.accumulated += value
        self.points.append(Point(time, value))
        
        return self.accumulated * Accumulator.factor
    
def average_medooze(av_dir, rep_dir, n):
    nmoinsun = n - 1
    
    fb=0
    transportSeqNum=1
    feedbackNum=2
    size=3
    sent=4
    recv=5
    deltaSent=6
    deltaRecv=7
    delta=8
    bwe=9
    targetBitrate=10
    availableBitrate=1
    rtt=12
    minrtt=13
    mark=14
    rtx=15
    probing=16
    
    medooze = rep_dir + '/medooze.csv'

    result = []

    media_acc = Accumulator()
    probing_acc = Accumulator()
    rtx_acc = Accumulator()
    target_acc = Accumulator()
    recv_acc = Accumulator()
    loss = 0
    
    with open(medooze, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter='|')

        for row in lines:
            r = []
            time = int(row[4])
            
            r.append(time)
            # r.append(int(row[size]) * 8 if row[rtx] == "0" and row[probing] == "0" else 0)
            # r.append(int(row[size]) * 8 if row[rtx] == "1" else 0)
            # r.append(int(row[size]) * 8 if row[probing] == "1" else 0)
            # r.append(int(row[size]) * 8 if row[sent] != "0" and row[recv] != "0" else 0)
            # r.append((float(row[fb]) - float(row[sent])) / 1000.)
            # r.append(float(row[targetBitrate]))
            # r.append(float(row[minrtt]))
            # r.append(float(row[rtt]))

            r.append(media_acc.accumulate(time, int(row[size]) * 8 if row[rtx] == "0" and row[probing] == "0" else 0))
            r.append(rtx_acc.accumulate(time, int(row[size]) * 8 if row[rtx] == "1" and row[probing] == "0" else 0))
            r.append(probing_acc.accumulate(time, int(row[size]) * 8 if row[rtx] == "0" and row[probing] == "1" else 0))
            r.append(recv_acc.accumulate(time, 0 if int(row[sent]) > 0 and int(row[recv] == 0) else int(row[size]) * 8))
            r.append((float(row[fb]) - float(row[sent])) / 1000.)
            r.append(float(row[targetBitrate]))
            r.append(float(row[rtt]) if float(row[minrtt]) == 0 or float(row[rtt]) < float(row[minrtt]) else float(row[minrtt]))
            r.append(float(row[rtt]))

            loss += (1 if int(row[sent]) > 0 and int(row[recv]) == 0 else 0)
            # print(loss)
            r.append(loss)
            
            result.append(r)

        result.sort()
    try:
        average_medooze = open(av_dir + '/medooze.csv', 'r')
        av_lines = csv.reader(average_medooze, delimiter=',')
        count = 0

        for row in av_lines:
            for col in range(len(row)):
                if count < len(result) and col < len(result[count]):
                    result[count][col] = (float(row[col]) * nmoinsun + result[count][col]) / n

            count += 1

        average_medooze.close()

    except OSError:
        pass
    
            
    average_medooze = open(av_dir + '/medooze.csv', 'w')
    writer = csv.writer(average_medooze, delimiter=',')

    for row in result:
        writer.writerow(row)

    average_medooze.close()
        
def update_average(rep):
    parent = rep + "/.."
    average_name = "average"
    average_dir = parent + "/" + average_name
    
    if not average_name in os.listdir(parent):
        os.mkdir(parent + "/average")

    #     for f in os.listdir(rep):
    #         shutil.copyfile(rep + '/' + f, average_dir + '/' + f)
            
    #     return None

    n = len(os.listdir()) - 1 # - average
    average_bitrate(average_dir, rep, n)
    average_qlog(average_dir, rep, n)
    average_medooze(average_dir, rep, n)
    
        
def move_files(exp_dir, dst):
    # bitrate
    shutil.copyfile(exp_dir + '/bitrate.csv', dst + '/bitrate.csv')
    
    # quic.csv
    shutil.copyfile(exp_dir + '/quic.csv', dst + '/quic.csv')

    # qlog and medooze
    for f in os.listdir(exp_dir):
        if ".qlog" in f:
            name = exp_dir.split("_")[0].split("/")[1]
            # print(s, exp_dir, s[0], dst)
            shutil.copyfile(exp_dir + '/' + f, dst + "/" + name + ".qlog")
        if "quic-relay" in f and ".csv" in f:
            shutil.copyfile(exp_dir + '/' + f, dst + "/medooze.csv")

    update_average(dst)

def iterate_repet():
    for r in os.listdir():
        if "repet" in r:
            print(r)
            
            lssort = sorted(os.listdir(r))
            
            for loss_dir in loss:
                print('\t', loss_dir)
                for delay_dir in latency:
                    print("\t\t", delay_dir)
                    new_path = loss_dir + '/' + delay_dir + '/' + r
                    os.mkdir(new_path)
                    move_files(r + '/' + lssort.pop(0), new_path)

def search_repet():    
    for impl in os.listdir():
        if not os.path.isdir(impl):
            continue

        os.chdir(impl)

        if "repet1" in os.listdir():
            print(os.getcwd())

            setup_exp_name()
            iterate_repet()
        else:
            search_repet()
        
        os.chdir('..')

if __name__ == "__main__":
    search_repet()
