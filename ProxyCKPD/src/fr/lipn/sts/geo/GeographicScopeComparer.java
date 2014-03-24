package fr.lipn.sts.geo;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;

import edu.mit.jwi.item.ISynsetID;
import edu.mit.jwi.item.POS;
import edu.stanford.nlp.ling.TaggedWord;
import fr.lipn.sts.tools.WordNet;

public class GeographicScopeComparer {
	private static double NORM_DIST=10000; //assume 10000Km as the maximal distance we can found;  we did this to align with GS scores
	
	public static double compare(ArrayList<TaggedWord> tSentence, ArrayList<TaggedWord> tSentence1) {
		
		HashSet<ISynsetID> s1_syns = new HashSet<ISynsetID>();
		for(TaggedWord tw : tSentence){
			String text=tw.word();
			String pos =tw.tag();
			s1_syns.addAll(WordNet.getSynsets(text, pos));
		}
		HashSet<ISynsetID> s2_syns = new HashSet<ISynsetID>();
		for(TaggedWord tw : tSentence1){
			String text=tw.word();
			String pos =tw.tag();
			s2_syns.addAll(WordNet.getSynsets(text, pos));
		}
		
		HashSet<String> off1= new HashSet<String>();
		for(ISynsetID syn : s1_syns){
			int off=syn.getOffset();
			POS p=syn.getPOS();
			String pos="n";
			if(p.equals(POS.VERB)) pos="v";
			if(p.equals(POS.ADJECTIVE)) pos="a";
			if(p.equals(POS.ADVERB)) pos="r";
			String synID=pos+String.format("%08d", off);
			if(BlueMarble.hasLocs(synID)) off1.add(synID);
		}
		
		HashSet<String> off2= new HashSet<String>();
		for(ISynsetID syn : s2_syns){
			int off=syn.getOffset();
			POS p=syn.getPOS();
			String pos="n";
			if(p.equals(POS.VERB)) pos="v";
			if(p.equals(POS.ADJECTIVE)) pos="a";
			if(p.equals(POS.ADVERB)) pos="r";
			String synID=pos+String.format("%08d", off);
			if(BlueMarble.hasLocs(synID)) off2.add(synID);
		}
		
		if(off1.size()==0 && off2.size()==0) {
			//no places available for both sentences: probably they are geographically not constrained
			//they are compatible from a geographical point of view
			return 1d;
		}
		
		if((off1.size() * off2.size()) ==0) {
			//one sentences contain places but the other don't
			//they are not compatible from a geographical point of view
			return 0d;
		}
		
		//in all other cases, try to establish a geographic distance
		double sumMinimalDist=0d;
		int numPairs=0;
		for(String id : off1) {
			double minDist=NORM_DIST;
			for(String id2 : off2) {
				double d =BlueMarble.getMinDistance(id, id2);
				System.err.println("minDistance between: "+id+" and "+id2+" : "+d);
				if (d < minDist) minDist=d;
				numPairs++;
			}
			System.err.println("minDist for: "+id+" : "+minDist);
			sumMinimalDist+=minDist;
		}
		
		double avgSumDist=sumMinimalDist/(double)numPairs;
		
		//System.err.println("sum of minimal distances: "+sumMinimalDist);
		
		double geoSim=1-(Math.log(1+avgSumDist)/Math.log(NORM_DIST));
		
		return geoSim;
	}
}
