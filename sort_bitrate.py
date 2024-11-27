import csv

from sort_util import *

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

def stats_line_bitrate(av_dir, rep_dir, n):
    TIME = 0
    BITRATE = 1
    LINK = 2
    FPS = 3
    
    bitrate_csv = open(rep_dir + '/bitrate.csv', 'r')
    bitrate_lines = [ line for line in csv.reader(bitrate_csv, delimiter=',') ]

    try:
        average_bitrate_csv = open(av_dir + '/bitrate_line.csv', 'r')
        av_lines = [line for line in csv.reader(average_bitrate_csv, delimiter=',')]
        average_bitrate_csv.close()
    except:
        av_lines = []
        
    for i in range(len(bitrate_lines)):
        j = i*3
        if j >= len(av_lines):
            av_lines.append([bitrate_lines[i][TIME], bitrate_lines[i][LINK]])
            av_lines.append([bitrate_lines[i][TIME], bitrate_lines[i][BITRATE]])
            av_lines.append([bitrate_lines[i][TIME], bitrate_lines[i][FPS]])
        else:
            if int(av_lines[j][1]) != int(bitrate_lines[i][LINK]):
                print("Link does not match, that is not the same exp parameter")
                return
            
            insert_sort(av_lines[j+1], bitrate_lines[i][BITRATE])
            insert_sort(av_lines[j+2], bitrate_lines[i][FPS])

    bitrate_csv.close()

    average_bitrate_csv = open(av_dir + '/bitrate_line.csv', 'w')

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
 
