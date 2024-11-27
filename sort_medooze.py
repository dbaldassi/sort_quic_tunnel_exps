import csv

from sort_util import *

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

def stats_line_medooze(av_dir, rep_dir, n):
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
    loss_value = 0

    medooze_stats_tab = [[], [], [], [], [], [], []] # media, rtx, probing, target, recv, rtt, loss

    print("Parsing medooze csv")
    with open(medooze, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter='|')

        count = 0
        for row in lines:
            count += 1
            r = []
            time = int(row[4])
            time_sec = float(time) / 1000000

            media_value = media_acc.accumulate(time, int(row[size]) * 8 if row[rtx] == "0" and row[probing] == "0" else 0)
            probing_value = rtx_acc.accumulate(time, int(row[size]) * 8 if row[rtx] == "1" and row[probing] == "0" else 0)
            rtx_value = rtx_acc.accumulate(time, int(row[size]) * 8 if row[rtx] == "1" and row[probing] == "0" else 0)
            recv_value = recv_acc.accumulate(time, 0 if int(row[sent]) > 0 and int(row[recv] == 0) else int(row[size]) * 8)
            loss_value += (1 if int(row[sent]) > 0 and int(row[recv]) == 0 else 0)

            # insert_sort(medooze_stats_tab[0], (time_sec, media_value))
            # insert_sort(medooze_stats_tab[1], (time_sec, probing_value))
            # insert_sort(medooze_stats_tab[2], (time_sec, rtx_value))
            # insert_sort(medooze_stats_tab[3], (time_sec, float(row[targetBitrate])))
            # insert_sort(medooze_stats_tab[4], (time_sec, recv_value))
            # insert_sort(medooze_stats_tab[5], (time_sec, float(row[rtt])))
            # insert_sort(medooze_stats_tab[6], (time_sec, loss_value))
            medooze_stats_tab[0].append((time_sec, media_value))
            medooze_stats_tab[1].append((time_sec, probing_value))
            medooze_stats_tab[2].append((time_sec, rtx_value))
            medooze_stats_tab[3].append((time_sec, float(row[targetBitrate])))
            medooze_stats_tab[4].append((time_sec, recv_value))
            medooze_stats_tab[5].append((time_sec, float(row[rtt])))
            medooze_stats_tab[6].append((time_sec, loss_value))

    print("Convert medooze to fixed point")
    PPSEC = 10
    for array in medooze_stats_tab:
        convert_to_fixed_number_of_points(array, PPSEC)

    trim_arrays(array)
    stats_line_medooze = []
    
    try:
        print("Adding stats to stats line medooze")
        stats_line_csv = open(av_dir + '/stats_line_medooze.csv', 'r')
        stats_line_medooze = [row for row in csv.reader(stats_line_csv, delimiter=',')]
        stats_line_csv.close()

        current_div = 0
        current_cat = 0
        for line in stats_line_medooze:
            stats_tab = medooze_stats_tab[current_cat]

            if(len(stats_tab) == 0):
                break
            
            stats_tab_current = stats_tab[0]

            val = stats_tab_current[current_div]
            line.append(val)

            current_cat += 1
            if(current_cat >= len(medooze_stats_tab)):
                current_div += 1

                if(current_div >= len(stats_tab_current)):
                    current_div = 0

                    for i in range(len(medooze_stats_tab)):
                        medooze_stats_tab[i].pop(0)

                current_cat = 0

    except OSError:
        print("stats_line_medooze.csv not found (maybe first time running it)")
        for i in range(len(medooze_stats_tab[0])):
            for j in range(len(medooze_stats_tab[0][i])):
                time = i + (j / float(PPSEC))

                for stat in medooze_stats_tab:
                    stats_line_medooze.append([time, stat[i][j]])

    print("Write medooze")
    stats_line_csv = open(av_dir + '/stats_line_medooze.csv', 'w')
    writer = csv.writer(stats_line_csv, delimiter=',')

    for row in stats_line_medooze:
        writer.writerow(row)

    stats_line_csv.close()
    
