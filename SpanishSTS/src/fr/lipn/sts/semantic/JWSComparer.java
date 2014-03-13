package fr.lipn.sts.semantic;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

import edu.mit.jwi.item.ISynsetID;
import edu.upc.freeling.ListWordIterator;
import edu.upc.freeling.Sentence;
import edu.upc.freeling.Word;
import fr.irit.sts.proxygenea.ConceptualComparer;
import fr.irit.sts.proxygenea.HyperPath;
import fr.irit.sts.proxygenea.PathNode;
import fr.irit.sts.proxygenea.SynsetPath;
import fr.lipn.sts.SpanishSTSComparer;
import fr.lipn.sts.tools.GoogleTFFactory;
import fr.lipn.sts.tools.WordNet;

public class JWSComparer {
	
	public static double compare(Sentence tSentence, Sentence tSentence1) {
		HashMap<String, HashSet<HyperPath>> aSenses = new HashMap<String, HashSet<HyperPath>>();
		ListWordIterator wIt = new ListWordIterator(tSentence);
		while(wIt.hasNext()){
			Word tw=wIt.next();
			String pos =tw.getTag();
			String text=tw.getLemma();
			if (pos.matches("(N|V|A|R).+")) {
				HashSet<ISynsetID> s1_syns = new HashSet<ISynsetID>();
				String[] elems= tw.getSensesString(0).split("/");
				String[] tmpWgt= elems[0].split(":");
				String[] offPOS= tmpWgt[0].split("\\-");
				if(offPOS.length > 1) {
					s1_syns.add(WordNet.getSynsetFromOffsetPOS(offPOS[0], offPOS[1]));
					//s1_syns.addAll(WordNet.getSynsets(text, pos)); //not available for Spanish
					HashSet<HyperPath> paths_1= new HashSet<HyperPath>();
					for(ISynsetID syn : s1_syns){
						HyperPath sp = new HyperPath(syn);
						paths_1.add(sp);
					}
					aSenses.put(text, paths_1);
				}
			}
		}
		
		HashMap<String, HashSet<HyperPath>> bSenses = new HashMap<String, HashSet<HyperPath>>();
		ListWordIterator wIt1 = new ListWordIterator(tSentence1);
		while(wIt1.hasNext()){
			Word tw=wIt1.next();
			String pos =tw.getTag();
			String text=tw.getLemma();
			if (pos.matches("(N|V|A|R).+")) {
				HashSet<ISynsetID> s2_syns = new HashSet<ISynsetID>();
				String[] elems= tw.getSensesString(0).split("/");
				String[] tmpWgt= elems[0].split(":");
				String[] offPOS= tmpWgt[0].split("\\-");
				if(offPOS.length > 1) {
					s2_syns.add(WordNet.getSynsetFromOffsetPOS(offPOS[0], offPOS[1]));
					//s1_syns.addAll(WordNet.getSynsets(text, pos)); //not available for Spanish
					HashSet<HyperPath> paths_2= new HashSet<HyperPath>();
					for(ISynsetID syn : s2_syns){
						HyperPath sp = new HyperPath(syn);
						paths_2.add(sp);
					}
					bSenses.put(text, paths_2);
				}
			}
		}
		
		double m1Sim = maxSim(aSenses, bSenses);
		double m2Sim = maxSim(bSenses, aSenses);
		
		if(SpanishSTSComparer.VERBOSE) System.err.println("JWS weight: "+(0.5d * (m1Sim+m2Sim)));
		
		return 0.5d * (m1Sim+m2Sim);
	}

	private static double maxSim(HashMap<String, HashSet<HyperPath>> aSenses,
			HashMap<String, HashSet<HyperPath>> bSenses) {
		//retain maximum similarity for each word in S1
		double sumWeight=0d;
		double den=0d;
		
		String targetSim="";
		for(String w : aSenses.keySet()){
			double maxSim=0d;
			for(HyperPath p1 : aSenses.get(w)) {
				for(String target : bSenses.keySet()){
					HashSet<HyperPath> paths2 = bSenses.get(target);
					for(HyperPath p2 : paths2){
						if(p1.comparableTo(p2)){
							double w0 = compareIC(p1,p2);
							if (w0 > maxSim) {
								maxSim=w0;
								targetSim=target;
							}
						}	
					}
				}
			}
			
			double w_idf = GoogleTFFactory.getIDF(w);
			sumWeight+=maxSim*w_idf; //Mihalcea et al.
			den+=w_idf;
			if(maxSim > 0) {
				if(SpanishSTSComparer.VERBOSE) System.err.println("JWS: best weight for "+w+" : "+maxSim+" <-> ("+targetSim+")");
			}
		}
		//Mihalcea et al.
		
		sumWeight=sumWeight/den;
		
		return sumWeight;
	}
	
	private static double compareIC(SynsetPath p1, SynsetPath p2){
		//TODO: integrate all in Conceptual Comparer?
		double ret =0d;
		PathNode lcs = ConceptualComparer.leastCommonSubsumer(p1, p2);
		if(lcs==null) {
			if(SpanishSTSComparer.VERBOSE) {
				System.err.println("LCS error");
				p1.print(System.err);
				p2.print(System.err);
			}
			return 0d; 
		}

		double cd = WordNet.getIC(lcs.getSyn());
		double l1 = WordNet.getIC(p1.getSyn());
		double l2 = WordNet.getIC(p2.getSyn());
		/*System.err.println(lcs.getSyn()+" : "+cd);
		System.err.println(p1.getSyn()+" : "+l1);
		System.err.println(p2.getSyn()+" : "+l2);*/
		switch(SpanishSTSComparer.IC_MEASURE){
			case SpanishSTSComparer.LIN:
				ret= ((cd*cd)/(l1+l2)); break; 
			case SpanishSTSComparer.JIANG_CONRATH:
				ret = (1.0d/Math.abs(1+l1+l2-2*cd)); break;
		}
		//System.err.println("JWS score: "+ret);
		return ret;
	}
}
