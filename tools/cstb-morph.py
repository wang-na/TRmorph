#!/usr/bin/python3
""" This script was used during code-swithcing treebank effort to
create alternative morphological analyses of files in the UD-IMST
treebank.
"""

import sys, re, copy
from logging import debug, info, warning, basicConfig
basicConfig(level="INFO", format='%(asctime)s %(message)s')
import argparse
from trmorph import Trmorph
from udtools.conllu import conllu_sentences

trmorph = Trmorph()

def get_analyses(form):
    analyses = trmorph.analyze(form)
    outstr = [form]
    for a in set(analyses):
        igs = trmorph.igs_to_ud(trmorph.to_igs(a, form))
        a_out = ""
        for i, ig in enumerate(igs):
            if i == len(igs) - 1:
                sep = ""
            else:
                sep = " -- "
            feat_val = dict()
            for ff in ig[3]:
                f, v  = ff.split('=')
                feat_val[f] = sorted(feat_val.get(f, []) + [v])
            feat_val = '|'.join(sorted(['='.join((f, ''.join(v))) for f,v in feat_val.items()]))
            if not feat_val:
                feat_val = "_"
            a_out += "{}+{}+{}+{}{}".format(ig[0], ig[1], ig[2], feat_val, sep)
        outstr.append(a_out)
    return list(set(outstr[1:]))

ap = argparse.ArgumentParser()
ap.add_argument('filename', type=argparse.FileType('r'),
        help="Input treebank in CoNLL-U format")
opt = ap.parse_args()

tb = conllu_sentences(opt.filename)

for sent in tb:
    print('\n'.join(sent.comment))
    a_multi = []
    for token in sent.nodes[1:]:
        m = sent.multi.get(token.index, None)
        if m:
            a_multi = []
            aa = get_analyses(m.form)
            tmp = []
            for a in aa:
                if 'Mood=Cnd' in a:
                    tmp.append(a.replace('Mood=Cnd', 'Mood=Des'))
                if a.endswith('+ADJ+Case=Nom|Number=Sing'):
                    tmp.append(a.replace('+ADJ+Case=Nom|Number=Sing', '+ADJ+_'))
            aa = aa + tmp
            if not aa:
                aa = ['{}+_+_+_'.format(m.form)]
#            print("{}-{}\t{}\t{}".format(m.index, m.multi, m.form,
            print("{}\t{}".format(m.form,
                "\t".join(aa)))
            nparts = m.multi - m.index + 1
            for a in aa:
                a_parts = a.split(" -- ")
                if len(a_parts) == nparts:
                    a_multi.append(a_parts)
            a_multi = [set(x) for x in zip(*a_multi)]
            if not a_multi:
                a_multi = ['__NO_ANALYSIS__'] * nparts

        if a_multi:
            a = "\t".join(a_multi.pop(0))
            continue
        else:
            a = get_analyses(token.form)
            tmp = []
            for aa in a:
                if 'Mood=Cnd' in aa:
                    tmp.append(aa.replace('Mood=Cnd', 'Mood=Des'))
                if aa.endswith('+ADJ+Case=Nom|Number=Sing'):
                    tmp.append(aa.replace('+ADJ+Case=Nom|Number=Sing', '+ADJ+_'))
            a = a + tmp
            if a:
                a = "\t".join(a)
            else:
                a = ['{}+_+_+_'.format(token.form)]
#        print("{}\t{}\t{}".format(token.index, token.form, a))
        print("{}\t{}".format(token.form, a))
    print()

trmorph = Trmorph()
