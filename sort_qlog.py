import csv
import json
import os

from sort_util import *

def parse_qlog_json(file_name):
    loss = 0
    sent = 0

    qlog_stats = { "rtt" : [], "cwnd": [], "sent": 0, "loss": 0, "bif" : [] }

    with open(file_name) as json_file:        
        try:
            data = json.load(json_file)
        except:
            return qlog_stats

        time_0 = -1

        for trace in data["traces"]:
            for event in trace["events"]:
                if event["name"] == "recovery:metrics_updated":
                    if(time_0 == -1):
                        time_0 = event['time']
                        
                    time = event['time'] - time_0
                    time = time / 1000000 # convert usec into sec
                    d = event["data"]

                    try:
                        qlog_stats["cwnd"].append([time, d['congestion_window']])
                        qlog_stats["bif"].append([time, d['bytes_in_flight']])
                    except:
                        pass

                    try:
                        qlog_stats["rtt"].append([time, d['latest_rtt']])
                    except:
                        pass

                elif event["name"] == "loss:packets_lost":
                    qlog_stats["loss"] += event["data"]["lost_packets"]
                elif event["name"] == "transport:packet_sent":
                    qlog_stats["sent"] += 1

    return qlog_stats

def parse_qlog_ndjson(file_name):
    loss = 0
    sent = 0
    
    qlog_stats = { "rtt" : [], "cwnd": [], "sent": 0, "loss": 0, "bif" : [] }
    
    with open(file_name) as json_file:
        for line in json_file.readlines():
            try:
                json_line = json.loads(line)
            except Exception as error:
                print("JSON line not valid ", error)
                return qlog_stats
            
            try:
                name = json_line['name']
                if name == "recovery:metrics_updated":
                    time = float(json_line['time']) / 1000
                    data = json_line['data']

                    if "latest_rtt" in data:
                        qlog_stats["rtt"].append([time, data['latest_rtt']])
                    elif "smoothed_rtt" in data:
                        qlog_stats["rtt"].append([time, data['smoothed_rtt']])

                    if "congestion_window"  in data:
                        qlog_stats["cwnd"].append([time, data['congestion_window']])

                    if "bytes_in_flight"  in data:
                        qlog_stats["bif"].append([time, data['bytes_in_flight']])
                        
                    if "lost_packets" in data:
                        qlog_stats["loss"] = data['lost_packets']
                    if "total_send_packets" in data:
                        qlog_stats["sent"] = data['total_send_packets']
                        
                elif name == "transport:packet_lost" or name == "recovery:packet_lost":
                    qlog_stats["loss"] += 1
                elif name == "transport:packet_sent":
                    qlog_stats["sent"] += 1
            except:
                pass

    return qlog_stats
    
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

    print("Parsing qlog")
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

def stats_line_qlog(av_dir, rep_dir, n):
    qlog_stats = {}
    print("stats line qlog")

    for f in os.listdir(rep_dir):
        if ".qlog" in f:
            if "mvfst" in f:
                qlog_stats = parse_qlog_json(rep_dir + '/mvfst.qlog')
                break
            else:
                qlog_stats = parse_qlog_ndjson(rep_dir + '/' + f)
                break

    stats_line_qlog = []
    cat = [ "cwnd", "bif", "rtt" ]
    current = 0

    PPSEC = 10

    print("Convert qlog to fixed points")
    qlog_stats["cwnd"] = convert_to_fixed_number_of_points(qlog_stats["cwnd"], PPSEC)
    qlog_stats["bif"]  = convert_to_fixed_number_of_points(qlog_stats["bif"], PPSEC)
    qlog_stats["rtt"]  = convert_to_fixed_number_of_points(qlog_stats["rtt"], PPSEC)        

    trim_arrays([qlog_stats["cwnd"], qlog_stats["bif"], qlog_stats["rtt"]])
    
    try:
        print("Adding stats to stats line qlog")
        average_qlog = open(av_dir + '/stats_line_qlog.csv', 'r')
        stats_line_qlog = [row for row in csv.reader(average_qlog, delimiter=',')]
        average_qlog.close()

        current_div = 0
        current_cat = 0
        for line in stats_line_qlog:
            stats_tab = qlog_stats[cat[current_cat]]

            if(len(stats_tab) == 0):
                break
            
            stats_tab_current = stats_tab[0]

            val = stats_tab_current[current_div]
            line.append(val)

            current_cat += 1
            if(current_cat >= len(cat)):
                current_div += 1

                if(current_div >= len(stats_tab_current)):
                    current_div = 0

                    for i in range(len(cat)):
                        qlog_stats[cat[i]].pop(0)

                current_cat = 0
        
    except OSError:
        print("stats_line_qlog.csv not found (maybe first time running it)")
        for i in range(len(qlog_stats["cwnd"])):            
            for j in range(len(qlog_stats["cwnd"][i])):
                time = i + (j / float(PPSEC))
                
                cwnd = qlog_stats["cwnd"][i][j]
                bif = qlog_stats["bif"][i][j]
                rtt = qlog_stats["rtt"][i][j]
                
                stats_line_qlog.append([time, cwnd])
                stats_line_qlog.append([time, bif])
                stats_line_qlog.append([time, rtt])

    print("Write qlog stats")
    stats_line_qlog_csv = open(av_dir + '/stats_line_qlog.csv', 'w')

    writer = csv.writer(stats_line_qlog_csv, delimiter=',')
    for row in stats_line_qlog:
        writer.writerow(row)

    stats_line_qlog_csv.close()
