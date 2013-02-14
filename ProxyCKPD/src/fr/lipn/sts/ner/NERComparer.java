package fr.lipn.sts.ner;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Vector;

import edu.stanford.nlp.ling.CoreAnnotations.AnswerAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import fr.lipn.sts.SemanticComparer;

public class NERComparer {

	public static double compare(List<List<CoreLabel>> cSentence, List<List<CoreLabel>> cSentence1) {
		HashMap<String, HashSet<String>> s1Map = new HashMap<String, HashSet<String>>();
		HashMap<String, HashSet<String>> s2Map = new HashMap<String, HashSet<String>>();
		for (List<CoreLabel> lcl : cSentence) {
			for (CoreLabel word : lcl) {
				String tag = word.getString(AnswerAnnotation.class);
				if(!tag.equals("O")){
					HashSet<String> tv = s1Map.get(tag);
					if(tv==null) tv=new HashSet<String>();
					tv.add(word.word());
					s1Map.put(tag, tv);
				}
	     	}
        }
		
		for (List<CoreLabel> lcl : cSentence1) {
			for (CoreLabel word : lcl) {
				String tag = word.getString(AnswerAnnotation.class);
				if(!tag.equals("O")){
					HashSet<String> tv = s2Map.get(tag);
					if(tv==null) tv=new HashSet<String>();
					tv.add(word.word());
					s2Map.put(tag, tv);
				}
	     	}
        }
		
		if(s1Map.size()==0 && s1Map.size()==0) return 1.0d;
		
		int overlap_A=0;
		int totalsize_A=0;
		//now calculate overlap (for each category)
		for(String k : s1Map.keySet()){
			HashSet<String> v1 = s1Map.get(k);
			totalsize_A+=v1.size();
			HashSet<String> v2 = s2Map.get(k);
			if(v2==null) v1.clear();
			else v1.retainAll(v2);
			overlap_A+=v1.size();
			if(SemanticComparer.VERBOSE) System.err.println("Shared NERs for category "+k+" : "+v1.toString());
		}
		double score_A= (double)overlap_A/(double)totalsize_A;
		
		int overlap_B=0;
		int totalsize_B=0;
		for(String k : s2Map.keySet()){
			HashSet<String> v1 = s2Map.get(k);
			totalsize_B+=v1.size();
			HashSet<String> v2 = s1Map.get(k);
			if(v2==null) v1.clear();
			else v1.retainAll(v2);
			v1.retainAll(v2);
			overlap_B+=v1.size();
		}
		double score_B= (double)overlap_B/(double)totalsize_B;
		
		if(totalsize_A > 0 && totalsize_B > 0) return (double)(2*overlap_A)/(double)(totalsize_A+totalsize_B); //Math.max(score_A, score_B);
		else return 0d;
	}

}
