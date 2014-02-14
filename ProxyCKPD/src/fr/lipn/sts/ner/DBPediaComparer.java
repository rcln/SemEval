package fr.lipn.sts.ner;

import java.util.HashSet;
import fr.lipn.sts.SemanticComparer;

public class DBPediaComparer {

	public static double compare(String t1, String t2, DBPediaChunkBasedAnnotator annotator) {
		HashSet<String> s1=new HashSet<String>();
		HashSet<String> s2=new HashSet<String>();
		
		s1.addAll(annotator.annotate(t1));
		s2.addAll(annotator.annotate(t2));
		
		int overlap_A=0;
		int totalsize_A=0;
		//now calculate overlap (for each category)
		HashSet<String> v1 = new HashSet<String>();
		v1.addAll(s1);
		totalsize_A+=v1.size();
		v1.retainAll(s2);
		overlap_A+=v1.size();
		if(SemanticComparer.VERBOSE) System.err.println("Shared DBPedia entities : "+v1.toString());
		
		double score_A= (double)overlap_A/(double)totalsize_A;
		
		int overlap_B=0;
		int totalsize_B=0;
		v1.clear();
		v1.addAll(s2);
		totalsize_B+=v1.size();
		v1.retainAll(s1);
		overlap_B+=v1.size();
		
		double score_B= (double)overlap_B/(double)totalsize_B;
		
		if(totalsize_A > 0 && totalsize_B > 0) return (double)(2*overlap_A)/(double)(totalsize_A+totalsize_B); //Math.max(score_A, score_B);
		else return 0d;
	}

}
