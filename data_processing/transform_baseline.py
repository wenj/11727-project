import os
import json

def print_to_file(filename, doc, title):
    title = '_'.join(title.split(' '))
    with open(filename, 'a') as f:
        f.write(f"#begin document {title}\n")
        for i, label in enumerate(doc):
            f.write(f"{title}\t0\t{i}\t{label[0]}\t{'|'.join(label[1])}\n")
        f.write(f"#end document\n")

def process_file(fname):
    with open(f"../CoreNLP/baseline/{fname}.output", 'r') as p_file:
        p_lines = p_file.readlines()
    d_name = p_lines[0].strip().split('=')[-1]
    d_name = '('.join(d_name.split('(')[:-1]).strip()
    print(d_name)

    with open("key-OntoNotesScheme", 'r') as k_file:
        k_lines = k_file.readlines()
    seg_begin = -1
    for i, line in enumerate(k_lines):
        if line.strip() == f"#begin document {d_name}":
            seg_begin = i
        if line.strip() == "#end document" and seg_begin != -1:
            seg_end = i
            break
    raw_doc = k_lines[seg_begin + 1: seg_end]
    doc = []
    sen = []
    for i, line in enumerate(raw_doc):
        col = line.strip().split('\t')
        if len(col) > 1:
            if col[-2] == "``" or col[-2] == "''":
                sen.append(('"', []))
            elif col[-2] == "`":
                sen.append(("'", []))
            elif col[-2] == "-LRB-":
                sen.append(('(', []))
            elif col[-2] == "-RRB-":
                sen.append((')', []))
            elif col[-2] == "--":
                sen.append(('-', []))
            else:
                sen.append((col[-2], []))
            if col[-1] != '-':
                label = col[-1].split('|')
                for l in label:
                    sen[-1][1].append(l)
        else:
            doc.append(sen[:])
            sen = []

    pred_doc = []
    sen = []
    flag = False
    for i, line in enumerate(p_lines):
        if line.startswith('Coreference set:'):
            pred_doc.append(sen[:])
            break
        if line.startswith('Sentence #'):
            flag = False
            if len(sen) > 1:
                pred_doc.append(sen[:-1])
            sen = []
        if flag:
            sen.append((line.strip()
                .replace("’”", "'''")
                .replace('’', "'")
                .replace('“', '"')
                .replace('”', '"')
                .replace('‘', "'")
                .replace('£', "#")
                .replace("&ndash;", '-')
                .replace("&mdash;", '-'), []))
        if line.strip() == "Tokens:":
            flag = True

    flag = False
    first = False
    for i, line in enumerate(p_lines):
        if line.startswith("Coreference set:"):
            chain_id = int(line.strip().split(": ")[-1])
            flag = True
            first = True
        elif flag:
            m1s, m1c, m1b, m1e, m2s, m2c, m2b, m2e = list(map(lambda x:int(x), line.strip().split(" ")))
            if m1b + 1 == m1e:
                pred_doc[m1s-1][m1b-1][1].append(f"({chain_id})")
            else:
                pred_doc[m1s-1][m1b-1][1].append(f"({chain_id}")
                pred_doc[m1s-1][m1e-2][1].append(f"{chain_id})")
            if first:
                if m2b + 1 == m2e:
                    pred_doc[m2s-1][m2b-1][1].append(f"({chain_id})")
                else:
                    pred_doc[m2s-1][m2b-1][1].append(f"({chain_id}")
                    pred_doc[m2s-1][m2e-2][1].append(f"{chain_id})")
                first = False

    print(len(doc))
    print(len(pred_doc))

    def merge(l):
        ret = []
        for sub_l in l:
            for item in sub_l:
                ret.append(item)
        return ret

    doc = merge(doc)
    pred_doc = merge(pred_doc)
    print(len(doc))
    print(len(pred_doc))

    pos_k = 0
    pos_p = 0
    new_doc = []
    new_pred_doc = []

    def subs(l, be, en):
        return ''.join(list(map(lambda x:x[0], l[be:en])))

    while pos_k < len(doc):
        if doc[pos_k][0] == pred_doc[pos_p][0]:
            new_doc.append(doc[pos_k])
            new_pred_doc.append(pred_doc[pos_p])
            pos_k += 1
            pos_p += 1
        else:
            k_begin = pos_k
            k_end = pos_k + 1
            p_begin = pos_p
            p_end = pos_p + 1
            while subs(doc, k_begin, k_end) != subs(pred_doc, p_begin, p_end):
                if len(subs(pred_doc, p_begin, p_end)) > 50 or len(subs(doc, k_begin, k_end)) > 50:
                    raise Exception("Error occured")
                print(subs(doc, k_begin, k_end))
                print(subs(pred_doc, p_begin, p_end))
                if subs(doc, k_begin, k_end) < subs(pred_doc, p_begin, p_end):
                    k_end += 1
                else:
                    p_end += 1
            # solve(k_begin, k_end, p_begin, p_end)
            if k_end == k_begin + 1:
                for i in range(p_begin, p_end):
                    new_doc.append((pred_doc[i][0], []))
                    new_pred_doc.append(pred_doc[i])
                for label in doc[k_begin][1]:
                    if '(' in label and ')' in label:
                        chain_id = label[1:-1]
                        new_doc[-(p_end - p_begin)][1].append(f"({chain_id}")
                        new_doc[-1][1].append(f"{chain_id})")
                    elif '(' in label:
                        chain_id = label[1:]
                        new_doc[-(p_end - p_begin)][1].append(f"({chain_id}")
                    elif ')' in label:
                        chain_id = label[:-1]
                        new_doc[-1][1].append(f"{chain_id})")
            elif p_end == p_begin + 1:
                for i in range(k_begin, k_end):
                    new_doc.append(doc[i])
                    new_pred_doc.append((doc[i][0], []))
                for label in pred_doc[p_begin][1]:
                    if '(' in label and ')' in label:
                        chain_id = label[1:-1]
                        new_pred_doc[-(k_end - k_begin)][1].append(f"({chain_id}")
                        new_pred_doc[-1][1].append(f"{chain_id})")
                    elif '(' in label:
                        chain_id = label[1:]
                        new_pred_doc[-(k_end - k_begin)][1].append(f"({chain_id}")
                    elif ')' in label:
                        chain_id = label[:-1]
                        new_pred_doc[-1][1].append(f"{chain_id})")
            else:
                print("unexpected")
            pos_k = k_end
            pos_p = p_end

    doc = new_doc
    pred_doc = new_pred_doc
    print(len(doc))
    print(len(pred_doc))
    print_to_file("baseline.key", doc, d_name)
    print_to_file("baseline.pred", pred_doc, d_name)

if __name__ == "__main__":
    fname_list = os.listdir("../CoreNLP/baseline")
    for fname in fname_list:
        print(fname)
        process_file(fname.split(".output")[0])
