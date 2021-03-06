Jeu des données pour des test d'amélioration du model d'apprentissage pour semeval 2014
-------------------
BUT: améliiorer la performance du model d'apprentissage pour SEmeval 2014/STS(Semantic Textual Similarity) à partir des données de Semeval.STS 2012 et 2013. 

HYPOTHÈSE: particioner le corpus pour entraîner plusieurs modèles améliore la performance de notre système d'apprentissage


1) Expériences:
Ces données permettent de faire les expériences suivantes:
    + Entraîner des modèles sur les données STS-train-2012 pour expermenter sur STS-test-2012. 
    + Entraîner des modèles sur les donnés de STS-train-2012 et STS-test-2012 pour expérimenter sur STS-test-2013

    + Entraîner des modèles sur les données de STS-train-2012 
					      +STS-test-2012
					      +STS-train-2013
					      +STS-test-2013
							     pour traiter des données inconnues. 

2) Jeux des données
   + Le point de départ sont les données des campagnes d'évaluation Semeval-STS 2012 et 2013. Voici un résumé:

	      	 	     	 	     	     sentences

	STS.2012.train.input.MSRpar.txt			750		Microsoft research paraphrase corpus
	STS.2012.train.input.MSRvid.txt			750		Microsoft research video description corpus
	STS.2012.train.input.SMTeuroparl.txt		734		WMT2008 develoment dataset (Europarl section)
	STS.2012.train.input.ALL			2234	
	
	STS.2012.test.input.MSRpar.txt			750		
	STS.2012.test.input.MSRvid.txt			750
	STS.2012.test.input.SMTeuroparl.txt		459
	STS.2012.test.input.surprise.OnWN.txt		750	
	STS.2012.test.input.surprise.SMTnews.txt	399
	STS.2012.test.input.ALL				3108
	
	STS.2013.test.input.FNWN.txt			189		 definitions from WordNet and FrameNet
	STS.2013.test.input.headlines.txt		750		 headlines mined from several news sources (RSS feed)
	STS.2013.test.input.OnWN.txt			561		 sense definitions from WordNet & OntoNotes
	STS.2013.test.input.SMT.txt			750		 DARPA GALE HTER and HyTER (MR plus human editing)
	STS.2013.test.input.ALL				2250		 
	
	TOTAL						7592


   + J'ai réorganisé les donnés de la façon suivante:

   ./semeval2014/en/jorge.nadi/data
	/2012
	documents pour la campagne STS.2012. 
		  /train
		  données d'entrainement: couples de phrases (fichiers *.input.*.txt)
		  	  		  gold standard (fichiers *.gs.*.txt)
		  /test
		  données de test: couples de phrases (fichiers *.input.*.txt)
		  	     	   gold standard (fichiers *.gs.*.txt)
	          /evaluate
		  scripts pour calculer la correlation Pearson entre un fichiers de résultats et un gold.standard	

	/2013
	documents pour la campagne STS.2012. 
		  /train				"
		  /test					"
		  /evaluate				"

    ./semeval2014/en/jorge.nadi/analysis
       -ce répertoire contient des fichiers .csv avec les features extraits par Davide. Je les ai pris de 

       	   /users/buscaldi/semeval/SemEval2013/libsvm-3.16/data/

       -il contient plusieurs jeux de tests que Davide a fait avec des analyses sémantiques à 9 ou 8 features. 

       -j'ai rennommé et organisé les fichiers d'après la notation décrite dans la section précedente



3) TODO:
   - Analyser avec la dernière version du système d'analyse de Davide (ProxyCKPD) les features pour produire des csv pour:
     	      STS.2012.train
	      STS.2012.test
	      STS.2013.train

   - Entraîner des SVM et des Max-ent pour ces toutes dernières analyses

   - Implementer une stratégie de partitionemment du corpus pour entraîner des modèles avec les partitions suivantes:
     		 Expérience 1): Réproduire STS.2012
		      1a) Tous les sous-corpus de STS.2012.train ensemble
		      1b) Tous les sous-cocpur de STS.2012.train séparés par source (MSRpar, MSRvid, SMT)
		      1c) Des sous-corpus de STS.2012.train séparés par un critère autre que la source
		      1d) Des sous-sous-corpus de STS.2012.train séparés par un critère additionnel à la source
		 
		 Expérience 2) Entrainer avec STS.2012.train et STS.2012.test pour traiter STS.2013.test
		      1a) "
		      1b) "
		      1c) "
		      1d) "

    - Produire des modèles pour chacun de ces partitionnements et évaluer pour trouver le plus performant pour chaque partitionnement

    - Implémenter une méthode pour choisir le modèle aproprié à chaque phrase de test (Expérience 3: entrener )
		 
