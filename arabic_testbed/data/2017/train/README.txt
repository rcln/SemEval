			 SEMEVAL-2017 TASK 1 - Track 1

				 STS

	       Semantic Textual Similarity for Arabic

			    Training DATASET
				   


This file describes the training dataset released for the SEMEVAL 2017
Multilingual Semantic Textual Similarity: Arabic subtask (Track 1). 

The Training dataset contains the following:

  README.txt 		  this file
  ar.STS.MSRpar.txt		  tab separated input file with ids and sentence pairs
  ar.STS.MSRvid.txt		   "
  ar.STS.SMTeuroparl.txt	   "
  
Introduction
------------

Given two sentences, participating systems are asked to return a continuous valued similarity score on a scale from 0 to 5, with 0 indicating that the semantics of the sentences are completely independent and 5 signifying semantic equivalence. Performance is assessed by computing the Pearson correlation between machine assigned semantic similarity scores and human judgements.

The dataset comprises pairs of sentences drawn from publicly
available datasets:

- MSR-Paraphrase, Microsoft Research Paraphrase Corpus
  http://research.microsoft.com/en-us/downloads/607d14d9-20cd-47e3-85bc-a2f65cd28042/
  510 pairs

- MSR-Video, Microsoft Research Video Description Corpus
  http://research.microsoft.com/en-us/downloads/38cf15fd-b8df-477e-a4e4-a4680caa75af/
  368 pairs of sentences.

- SMTeuroparl: WMT2008 develoment dataset (Europarl section)
  http://www.statmt.org/wmt08/shared-evaluation-task.html
  203 pairs of sentences.


The datasets have been derived as follows:


The original sentence pairs (English) have been manually tagged with a number from 0 to 5. This is a subset of the data used in previous years for English STS. The data have been manually translated into Arabic for this task. 


Input format
------------

The input file consist of four fields separated by tabs:

- ID (Unique identifier for each pair)
- STS score (gold standard)
- first sentence (does not contain tabs)
- second sentence (does not contain tabs)


Acknowledgements:
-------------
The manual translations to Arabic have been provided by CMU-Qatar. 
This project was made possible by the Qatar National Research Fund (QNRF) Award to CMU-Qatar and GWU OPTDIAC project. 


Other
-----

Please check http://alt.qcri.org/semeval2017/task1/ for more details.



Authors
-------




