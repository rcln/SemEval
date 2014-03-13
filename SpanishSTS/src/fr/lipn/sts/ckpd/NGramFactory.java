package fr.lipn.sts.ckpd;

import java.util.ArrayList;
import java.util.HashSet;

import edu.upc.freeling.ListSentence;
import edu.upc.freeling.ListSentenceIterator;
import edu.upc.freeling.ListWordIterator;
import edu.upc.freeling.Sentence;
import edu.upc.freeling.VectorWord;
import edu.upc.freeling.Word;

public class NGramFactory {
	
	public static HashSet<NGram> getNGramSet(Sentence sentence){
		HashSet<NGram> ngramSet = new HashSet<NGram>();
		
		VectorWord vecw = sentence.getWords();
		long maxN=vecw.size();
		for(int i=0; i< maxN; i++){
			for(int j=0; j<vecw.size(); j++) {
				NGram ng = new NGram();
				for(int k=j; k<=(j+i) && k < vecw.size(); k++){
					ng.add(new Term(vecw.get(k)));
				}
				ngramSet.add(ng);
			}
		}
		
		return ngramSet;
	}

	public static NGram getNGram(Sentence tSentence) {
		NGram ng= new NGram();
		ListWordIterator wIt = new ListWordIterator(tSentence);
		while(wIt.hasNext()){
			ng.add(new Term(wIt.next()));
		}
		return ng;
	}

}
