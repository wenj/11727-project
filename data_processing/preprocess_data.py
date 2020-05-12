import os
def run_file(fname):
    with open(f"Documents/{fname}") as fin:
        with open(f"Documents_processed/{fname}", 'w') as fout:
            for line in fin:
                pro_line = line.replace('–','-').replace('—', '-').replace('."', '".')
                fout.write(pro_line)

if __name__ == "__main__":
    fname_list = os.listdir("../WikiCoref/Documents")
    fout = open("filelist.txt", 'w')
    for fname in fname_list:
        print("Processing document:", fname)
        fout.write(f"Documents_processed/{fname}\n")
        run_file(fname)
