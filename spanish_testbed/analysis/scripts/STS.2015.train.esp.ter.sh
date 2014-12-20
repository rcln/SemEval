#!/bin/sh
export SEMEVAL_HOME=/local_home/lipn/SemEval/
./run.semantic.comparer.with.train.es.sh $SEMEVAL_HOME/spanish_testbed/data/train/STS.2014.input.local2.sentences.txt $SEMEVAL_HOME/spanish_testbed/data/train/STS.2014.gs.local2.sentences.txt > $SEMEVAL_HOME/spanish_testbed/analysis/results/STS.2014.input.local2.sentences.2.dat 2>$SEMEVAL_HOME/spanish_testbed/analysis/logs/STS.2014.input.local2.sentences.2.log
./run.semantic.comparer.with.train.es.sh $SEMEVAL_HOME/spanish_testbed/data/train/STS.2014.input.local.sentences.txt $SEMEVAL_HOME/spanish_testbed/data/train/STS.2014.gs.local.sentences.txt > $SEMEVAL_HOME/spanish_testbed/analysis/results/STS.2014.input.local.sentences.2.dat 2>$SEMEVAL_HOME/spanish_testbed/analysis/logs/STS.2014.input.local.sentences.2.log
