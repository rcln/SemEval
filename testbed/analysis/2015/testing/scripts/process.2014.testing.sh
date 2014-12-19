#!/bin/sh
export SEMEVAL_HOME=/home/jgflores/experimentos/SemEval/sopa.2015/SemEval/
./run.semantic.comparer.sh $SEMEVAL_HOME/testbed/data/2014/test/STS.2014.input.tweet-news.txt> $SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.results/STS.2014.input.tweet-news.dat 2>$SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.logs/STS.2014.input.tweet-news.log
./run.semantic.comparer.sh $SEMEVAL_HOME/testbed/data/2014/test/STS.2014.test.input.deft-forum.txt> $SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.results/STS.2014.test.input.deft-forum.dat 2>$SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.logs/STS.2014.test.input.deft-forum.log
./run.semantic.comparer.sh $SEMEVAL_HOME/testbed/data/2014/test/STS.2014.test.input.deft-news.txt> $SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.results/STS.2014.test.input.deft-news.dat 2>$SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.logs/STS.2014.test.input.deft-news.log
./run.semantic.comparer.sh $SEMEVAL_HOME/testbed/data/2014/test/STS.2014.test.input.headlines.txt> $SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.results/STS.2014.test.input.headlines.dat 2>$SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.logs/STS.2014.test.input.headlines.log
./run.semantic.comparer.sh $SEMEVAL_HOME/testbed/data/2014/test/STS.2014.test.input.images.txt> $SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.results/STS.2014.test.input.images.dat 2>$SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.logs/STS.2014.test.input.images.log
./run.semantic.comparer.sh $SEMEVAL_HOME/testbed/data/2014/test/STS.2014.test.input.OnWN.txt> $SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.results/STS.2014.test.input.OnWN.dat 2>$SEMEVAL_HOME/testbed/analysis/2015/testing/2014.test.logs/STS.2014.test.input.OnWN.log
