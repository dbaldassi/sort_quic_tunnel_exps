
def insert_sort(tab, val):
    i = 1

    while i < len(tab) and tab[i] < val:
        i += 1

    if i == len(tab):
        tab.append(val)
    else:
        tab.insert(i, val)
    
# tab -> array to convert
# ppsec -> points per seconds, ex return for 3 [[a,b,c], [a,b,c] ... ]
def convert_to_fixed_number_of_points(tab_src, ppsec=10):
    tab_dest = []
    
    current_time_sec = 0
    current_tab_src = 0
    current_time_div = 0

    # add first division tab
    tab_dest.append([])

    while(current_tab_src < len(tab_src)):
        time_inf = current_time_sec + (float(current_time_div) / ppsec)
        time_sup = current_time_sec + (float(current_time_div+1) / ppsec)

        # print(current_tab_src, len(tab_src), time_inf, time_sup)

        is_in_division = True

        s = 0
        count = 0
        while(is_in_division and current_tab_src < len(tab_src)):
            time, val = tab_src[current_tab_src]

            if(time >= time_inf and time < time_sup):
                current_tab_src += 1
                s += val
                count += 1
            elif(time < time_inf): # because not sorted, we discard the value
                current_tab_src += 1
            else:
                is_in_division = False

        tab_dest[-1].append(s / count if count > 0 else -1)
            
        current_time_div += 1
        if(len(tab_dest[-1]) == ppsec):
            current_time_div = 0
            current_time_sec += 1
            tab_dest.append([])

    # remove last one if empty
    if(len(tab_dest[-1]) == 0):
        tab_dest.pop(-1)

    return tab_dest
    
def trim_arrays(arrays):
    lengths = [ len(a) for a in arrays ]
    min_len = min(lengths)

    for array in arrays:
        while(len(array) > min_len):
            array.pop()

    # trim nested arrays (if thats the case)
    if(type(arrays[0][0]) is list):
        sub_arrays = [ a[-1] for a in arrays ] # take last array of each
        trim_arrays(sub_arrays)
    
