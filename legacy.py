
def setup_exp_name():
    os.mkdir('sorted')

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
            
            # for loss_dir in loss:
            #     print('\t', loss_dir)
            #     for delay_dir in latency:
            #         print("\t\t", delay_dir)
            #         new_path = loss_dir + '/' + delay_dir + '/' + r
            #         os.mkdir(new_path)
            #         move_files(r + '/' + lssort.pop(0), new_path)

            new_path = 'sorted/' + r
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
