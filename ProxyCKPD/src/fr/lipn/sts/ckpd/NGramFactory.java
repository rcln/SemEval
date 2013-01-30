package fr.lipn.sts.ckpd;

import java.util.ArrayList;
import java.util.HashSet;

import edu.stanford.nlp.ling.TaggedWord;

public class NGramFactory {
	
	public static HashSet<NGram> getNGramSet(ArrayList<TaggedWord> sentence){
		HashSet<NGram> ngramSet = new HashSet<NGram>();
		int maxN=sentence.size();
		for(int i=0; i< maxN; i++){
			for(int j=0; j<sentence.size(); j++) {
				NGram ng = new NGram();
				for(int k=j; k<=(j+i) && k < sentence.size(); k++){
					ng.add(new Term(sentence.get(k)));
				}
				ngramSet.add(ng);
			}
		}
		return ngramSet;
	}

	public static NGram getNGram(ArrayList<TaggedWord> tSentence) {
		NGram ng= new NGram();
		for(TaggedWord tw : tSentence){
			ng.add(new Term(tw));
		}
		return ng;
	}

}
