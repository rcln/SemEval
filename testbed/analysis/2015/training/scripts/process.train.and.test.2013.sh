#!/bin/sh
export SEMEVAL_HOME=/local_home/lipn/SemEval/
./run.semantic.comparer.with.train.sh $SEMEVAL_HOME/testbed//data/2014/train/STS.2013.test.input.FNWN.txt $SEMEVAL_HOME/testbed//data/2014/train/STS.2013.test.gs.FNWN.txt
./run.semantic.comparer.with.train.sh $SEMEVAL_HOME/testbed//data/2014/train/STS.2013.test.input.headlines.txt $SEMEVAL_HOME/testbed//data/2014/train/STS.2013.test.gs.headlines.txt
./run.semantic.comparer.with.train.sh $SEMEVAL_HOME/testbed//data/2014/train/STS.2013.test.input.OnWN.txt $SEMEVAL_HOME/testbed//data/2014/train/STS.2013.test.gs.OnWN.txt
./run.semantic.comparer.with.train.sh $SEMEVAL_HOME/testbed//data/2014/train/STS.2013.test.input.SMT.txt $SEMEVAL_HOME/testbed//data/2014/train/STS.2013.test.gs.SMT.txt
