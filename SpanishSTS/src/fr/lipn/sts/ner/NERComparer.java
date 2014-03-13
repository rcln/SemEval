package fr.lipn.sts.ner;

import java.util.HashMap;
import java.util.HashSet;

import edu.upc.freeling.ListSentence;
import edu.upc.freeling.ListSentenceIterator;
import edu.upc.freeling.ListWordIterator;
import edu.upc.freeling.Sentence;
import edu.upc.freeling.Word;
import fr.lipn.sts.SpanishSTSComparer;
import fr.lipn.sts.tools.LevenshteinDistance;

public class NERComparer {
	private static boolean FUZZY=true; //if FUZZY, the NEs are compared even if they are not the same using edit distance
	
	public static double compare(ListSentence cSentences, ListSentence cSentences1) {
		HashMap<String, HashSet<String>> s1Map = new HashMap<String, HashSet<String>>();
		HashMap<String, HashSet<String>> s2Map = new HashMap<String, HashSet<String>>();
		
		ListSentenceIterator sIt = new ListSentenceIterator(cSentences);
		ListSentenceIterator sIt1 = new ListSentenceIterator(cSentences1);
		
		while (sIt.hasNext()) {
	        Sentence s = sIt.next();
	        ListWordIterator wIt = new ListWordIterator(s);
	        while (wIt.hasNext()) {
	          Word w = wIt.next();
	          String tag = w.getTag();
	          if(tag.startsWith("NP") || tag.startsWith("W")) {
		          HashSet<String> tv = s1Map.get(tag);
		          if(tv==null) tv=new HashSet<String>();
				  tv.add(w.getLemma());
				  s1Map.put(tag, tv);
	          }
	          //System.out.print(w.getForm() + " " + w.getLemma() + " " + w.getTag() );
	        }
	    }
	        
        while (sIt1.hasNext()) {
	        Sentence s = sIt1.next();
	        ListWordIterator wIt = new ListWordIterator(s);
	        while (wIt.hasNext()) {
	          Word w = wIt.next();
	          String tag = w.getTag();
	          if(tag.startsWith("NP") || tag.startsWith("W")) {
		          HashSet<String> tv = s2Map.get(tag);
		          if(tv==null) tv=new HashSet<String>();
				  tv.add(w.getLemma());
				  s2Map.put(tag, tv);
	          }
	        }				          
	    }
		
		if(s1Map.size()==0 && s1Map.size()==0) return 1.0d; //NOTE: should return 0 instead? TEST IT
		
		float overlap_A=0;
		float totalsize_A=0;
		//now calculate overlap (for each category)
		for(String k : s1Map.keySet()){
			HashSet<String> v1 = s1Map.get(k);
			totalsize_A+=v1.size();
			HashSet<String> v2 = s2Map.get(k);
			if(!FUZZY) {
				if(v2==null) v1.clear();	
				else v1.retainAll(v2);
				overlap_A+=(float)v1.size();
			} else {
				if(v2==null) overlap_A+=0.0;
				else {
					float fuzzysize = calcFuzzyOverlap(v1, v2);
					overlap_A+=fuzzysize;
				}
			}
			if(SpanishSTSComparer.VERBOSE) System.err.println("Shared NERs for category "+k+" : "+v1.toString());
		}
		double score_A= (double)overlap_A/(double)totalsize_A;
		
		int overlap_B=0;
		int totalsize_B=0;
		for(String k : s2Map.keySet()){
			HashSet<String> v1 = s2Map.get(k);
			totalsize_B+=v1.size();
			HashSet<String> v2 = s1Map.get(k);
			if(!FUZZY) {
				if(v2==null) v1.clear();
				else v1.retainAll(v2);
				v1.retainAll(v2);
				overlap_B+=(float)v1.size();
			} else {
				if(v2==null) overlap_B+=0.0;
				else {
					float fuzzysize = calcFuzzyOverlap(v1, v2);
					overlap_B+=fuzzysize;
				}
			}
		}
		double score_B= (double)overlap_B/(double)totalsize_B;
		
		if(totalsize_A > 0 && totalsize_B > 0) return (double)(2*overlap_A*overlap_B)/(double)(totalsize_A+totalsize_B);
		else return 0d;
	}

	private static float calcFuzzyOverlap(HashSet<String> v1, HashSet<String> v2) {
		float sum=0;
		for(String s : v1) {
			float maxSim=0;
			for(String s2 : v2) {
				float sim = LevenshteinDistance.levenshteinSimilarity(s, s2);
				if (sim > maxSim) maxSim=sim;
			}
			sum+=maxSim;
		}
		return sum;
	}

}
