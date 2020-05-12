import os
import json

def process_file(fname):
    with open(f"../CoreNLP/baseline/{fname}.output", 'r') as p_file:
        p_lines = p_file.readlines()
    d_name = p_lines[0].strip().split('=')[-1]
    d_name = '('.join(d_name.split('(')[:-1]).strip()
    print(d_name)

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

    fout = open(f"baseline_json/{fname}.json", 'w')
    d = []
    chain = []
    flag = False
    first = False
    for i, line in enumerate(p_lines):
        if line.startswith("Coreference set:"):
            chain_id = int(line.strip().split(": ")[-1])
            flag = True
            first = True
            if len(chain) > 1:
                d.append(chain[:])
            chain = []
        elif flag:
            m1s, m1c, m1b, m1e, m2s, m2c, m2b, m2e = list(map(lambda x:int(x), line.strip().split(" ")))
            if m1b + 1 == m1e:
                pred_doc[m1s-1][m1b-1][1].append(f"({chain_id})")
                mention = {"startIndex": m1b,
                        "endIndex": m1e,
                        "mention": pred_doc[m1s-1][m1b-1][0],
                        "sentNum": m1s,
                        "headIndex": m1c}
                chain.append(mention.copy())
            else:
                pred_doc[m1s-1][m1b-1][1].append(f"({chain_id}")
                pred_doc[m1s-1][m1e-2][1].append(f"{chain_id})")
                mention = {"startIndex": m1b,
                        "endIndex": m1e,
                        "mention": ' '.join([pred_doc[m1s-1][i][0] for i in range(m1b-1, m1e-2)]).strip(),
                        "sentNum": m1s,
                        "headIndex": m1c}
                chain.append(mention.copy())
            if first:
                if m2b + 1 == m2e:
                    pred_doc[m2s-1][m2b-1][1].append(f"({chain_id})")
                    mention = {"startIndex": m2b,
                        "endIndex": m2e,
                        "mention": pred_doc[m2s-1][m2b-1][0],
                        "sentNum": m2s,
                        "headIndex": m2c}
                    chain.append(mention.copy())
                else:
                    pred_doc[m2s-1][m2b-1][1].append(f"({chain_id}")
                    pred_doc[m2s-1][m2e-2][1].append(f"{chain_id})")
                    mention = {"startIndex": m2b,
                        "endIndex": m2e,
                        "mention": ' '.join([pred_doc[m2s-1][i][0] for i in range(m2b-1, m2e-2)]).strip(),
                        "sentNum": m2s,
                        "headIndex": m2c}
                    chain.append(mention.copy())

                first = False
    json.dump(d, fout, indent=4)
    fout.close()

if __name__ == "__main__":
    fname_list = os.listdir("../CoreNLP/baseline")
    for fname in fname_list:
        print(fname)
        process_file(fname.split(".output")[0])
