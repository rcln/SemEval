#!/bin/bash
path_head=$ENGLISH_TESTBED
dat_file=$path_head/analysis/2015/training/results/$1.dat
log_file=$path_head/analysis/2015/training/logs/$1.log
echo '---------------------------------------------'
echo '---------------------------------------------'
ls -all $log_file
echo 'RESULTS .dat LINE COUNT::'
wc -l $dat_file
echo 'ORIGINAL .txt LINE COUNT::'
if [ -n "$2" ]; then
	txt_file=$ENGLISH_TESTBED/data/2014/train/$2
else
	txt_file=$ENGLISH_TESTBED/data/2014/train/$1
fi
wc -l $txt_file.txt
echo 'TOTAL ERRORS::'
grep java.lang $log_file | wc -l
echo 'NullPointerException ERRORS::'
grep Null $log_file | wc -l
echo 'ArrayIndexOutOfBoundsException ERRORS::'
grep Array $log_file | wc -l
echo '.gs FILE HEAD'
gs_file=${txt_file//input/gs}.txt
head $gs_file
echo '.dat FILE HEAD'
head $dat_file
echo '.gs FILE TAIL'
tail $gs_file
echo '.dat FILE TAIL'
tail $dat_file
echo '---------------------------------------------'
echo '---------------------------------------------'
