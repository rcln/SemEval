#!/bin/bash
path_head=$ENGLISH_TESTBED/analysis
dat_file=$path_head/2015/testing/results/$1.dat
log_file=$path_head/2015/testing/logs/$1.log
echo '---------------------------------------------'
ls -all $log_file
echo 'RESULTS .dat LINE COUNT::'
wc -l $dat_file
echo 'ORIGINAL .txt LINE COUNT::'
if [ -n "$2" ]; then
	txt_file=$ENGLISH_TESTBED/data/2015/test/$2
else
	txt_file=$ENGLISH_TESTBED/data/2015/test/$1
fi
wc -l $txt_file.txt
echo 'FIRST LINE::'
head -n 1 $dat_file 
echo 'LAST LINE::'
tail -n 1 $dat_file
echo 'TOTAL ERRORS::'
grep java.lang $log_file | wc -l
echo 'NullPointerException ERRORS::'
grep Null $log_file | wc -l
echo 'ArrayIndexOutOfBoundsException ERRORS::'
grep Array $log_file | wc -l
echo '---------------------------------------------'

