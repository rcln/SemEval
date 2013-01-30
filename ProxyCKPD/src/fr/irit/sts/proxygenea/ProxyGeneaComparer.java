package fr.irit.sts.proxygenea;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Vector;

import edu.mit.jwi.item.ISynsetID;
import edu.stanford.nlp.ling.TaggedWord;
import fr.lipn.sts.SemanticComparer;
import fr.lipn.sts.tools.WordNet;

public class ProxyGeneaComparer {

	public static double compare(ArrayList<TaggedWord> tSentence,
			ArrayList<TaggedWord> tSentence1) {
		
		HashMap<String, HashSet<SynsetPath>> aSenses = new HashMap<String, HashSet<SynsetPath>>();
		for(TaggedWord tw : tSentence){
			HashSet<ISynsetID> s1_syns = new HashSet<ISynsetID>();
			String text=tw.word();
			String pos =tw.tag();
			s1_syns.addAll(WordNet.getSynsets(text, pos));
			HashSet<SynsetPath> paths_1= new HashSet<SynsetPath>();
			for(ISynsetID syn : s1_syns){
				SynsetPath sp = new SynsetPath(syn);
				paths_1.add(sp);
			}
			aSenses.put(text, paths_1);
		}
		
		HashMap<String, HashSet<SynsetPath>> bSenses = new HashMap<String, HashSet<SynsetPath>>();
		for(TaggedWord tw : tSentence1){
			HashSet<ISynsetID> s2_syns = new HashSet<ISynsetID>();
			String text=tw.word();
			String pos =tw.tag();
			s2_syns.addAll(WordNet.getSynsets(text, pos));
			HashSet<SynsetPath> paths_2= new HashSet<SynsetPath>();
			for(ISynsetID syn : s2_syns){
				SynsetPath sp = new SynsetPath(syn);
				paths_2.add(sp);
			}
			bSenses.put(text, paths_2);
		}
		
		//retain maximum similarity for each word
		float sumWeight=0;
		int cnt=0;
		String targetSim="";
		for(String w : aSenses.keySet()){
			float maxSim=0f;
			for(SynsetPath p1 : aSenses.get(w)) {
				for(String target : bSenses.keySet()){
					HashSet<SynsetPath> paths2 = bSenses.get(target);
					for(SynsetPath p2 : paths2){
						if(p1.comparableTo(p2)){
							float w0 = compare(p1,p2);
							if (w0 > maxSim) {
								maxSim=w0;
								targetSim=target;
							}
						}	
					}
				}
			}
			
			sumWeight+=maxSim;
			if(maxSim > 0) {
				if(SemanticComparer.VERBOSE) System.err.println("best weight for "+w+" : "+maxSim+" <-> ("+targetSim+")");
					cnt++;
			}
		}
		sumWeight=sumWeight/(float)cnt;
		
		/*
		for(SynsetPath p1 : paths_1){
			for(SynsetPath p2 : paths_2){
				if(p1.comparableTo(p2)){
					float w = compare(p1,p2);
					System.out.println("comparing concepts: ");
					p1.print();
					p2.print();
					System.out.println("value: "+w);
					sumWeight+=w;
					cnt+=1;
				}
			}
		}
		if(cnt>0) sumWeight=sumWeight/(float)cnt; //normalized in size
		*/
		return sumWeight;
	}
	
	
	public static PathNode leastCommonSubsumer(SynsetPath a, SynsetPath b){
		PathNode cur=null;
		Vector<String> ra = a.reversePath();
		Vector<String> rb = b.reversePath();
		for(int i=0; i< Math.min(ra.size(), rb.size()); i++){
			if(ra.get(i).equals(rb.get(i))) {
				cur=new PathNode(ra.get(i), (i+1));
			}
			else break;
		}
		return cur;
	}
	
	
	private static float compare(SynsetPath p1, SynsetPath p2){
		float ret =0f;
		PathNode lcs = leastCommonSubsumer(p1, p2);
		if(lcs==null) {
			if(SemanticComparer.VERBOSE) {
				System.err.println("LCS error");
				p1.print(System.err);
				p2.print(System.err);
			}
			return 0f; //FIXME: it happened once but it's not clear why since we already checked the comparability
		}
		float cd = (float)lcs.depth();
		float l1 = (float)p1.size();
		float l2 = (float)p2.size();
		
		switch(SemanticComparer.STRUCTURAL_MEASURE){
			case SemanticComparer.PROXYGENEA1:
				ret= (cd*cd)/(l1*l2); break; 
			case SemanticComparer.PROXYGENEA2:
				ret = cd/(l1+l2-cd); break;
			case SemanticComparer.PROXYGENEA3:
				ret = 1f/(1f+l1+l2-2*cd); break;
			case SemanticComparer.WU_PALMER:
				ret= (2*cd)/(l1+l2); break;
		}
		return ret;
	}
	

}
