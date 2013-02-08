package fr.lipn.sts.syntax;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Vector;

import edu.stanford.nlp.ling.TaggedWord;
import fr.irit.sts.proxygenea.ConceptualComparer;
import fr.lipn.sts.tools.GoogleTFFactory;
import fr.lipn.sts.tools.LevenshteinDistance;

public class DepPair {
	Vector<Dependency> d1;
	Vector<Dependency> d2;
	
	HashMap<Dependency, Vector<DepAlignment>> alMap; //maps deps to a list of possible (scored) alignments
	
	public DepPair(Vector<Dependency> d1, Vector<Dependency> d2){
		this.d1=d1; this.d2=d2;
		alMap = new HashMap<Dependency, Vector<DepAlignment>>();
	}
	
	private String findPOS(ArrayList<TaggedWord> tSentence, int position, String word){
		if(word.equals("ROOT")) return "NN";
		try {
			TaggedWord tw = tSentence.get(position);
			if(word.startsWith(tw.word())){
				return tw.tag();
			} else {
				int lp=position-1;
				tw = tSentence.get(lp);
				if(word.startsWith(tw.word())){
					return tw.tag();
				} else {
					int rp=position+1;
					tw = tSentence.get(rp);
					if(word.startsWith(tw.word())){
						return tw.tag();
					}
				}
			}
		} catch (Exception e){
			if(position < 0){
				int i=0;
				TaggedWord tw = tSentence.get(i);
				while(!word.startsWith(tw.word()) && i < tSentence.size()-1){
					i++;
					tw=tSentence.get(i);
				}
				if(i< tSentence.size()) return tw.tag();
				else return "NN";
			}
			
			if(position >= tSentence.size()) {
				int i=tSentence.size()-1;
				TaggedWord tw = tSentence.get(i);
				while(!word.startsWith(tw.word()) && i > 0){
					i--;
					tw=tSentence.get(i);
				}
				if(i >= 0) return tw.tag();
				else return "NN";
			}
		}
		//if everything else fails, return NN
		return "NN";
	}
	
	public void setPOStags(ArrayList<TaggedWord> tSentence,
			ArrayList<TaggedWord> tSentence1) {
		
		for(Dependency d : d1) {
			int hp = d.head.getPosition()-1;
			d.head.setPOS(findPOS(tSentence, hp, d.head.getWord()));
			int tp = d.dependent.getPosition()-1;
			d.dependent.setPOS(findPOS(tSentence, tp, d.dependent.getWord()));
			
			//System.err.println(d.toString());
		}
		//System.err.println("-----");
		for(Dependency d : d2) {
			int hp = d.head.getPosition()-1;
			d.head.setPOS(findPOS(tSentence1, hp, d.head.getWord()));
			int tp = d.dependent.getPosition()-1;
			d.dependent.setPOS(findPOS(tSentence1, tp, d.dependent.getWord()));
			
			//System.err.println(d.toString());
		}
		
	}
	
	private DepAlignment getBestDep(Dependency d, Vector<Dependency> d2){
		Vector<DepAlignment> tmpVA = new Vector<DepAlignment>();
		String label = d.label;
		DepWord head = d.head;
		DepWord tail = d.dependent;
		
		double headW=GoogleTFFactory.getIC(head.getWord());
		double tailW=GoogleTFFactory.getIC(tail.getWord());
		
		for(Dependency dd : d2){
			String dlabel = dd.label;
			DepWord dhead = dd.head;
			DepWord dtail = dd.dependent;
			
			double dheadW=GoogleTFFactory.getIC(dhead.getWord());
			double dtailW=GoogleTFFactory.getIC(dtail.getWord());
			
			double hw = Math.max(headW, dheadW);
			double dw = Math.max(tailW, dtailW);
			
			Double ld = new Double(LevenshteinDistance.levenshteinSimilarity(label, dlabel));
			Double hsim = new Double(hw*ConceptualComparer.compare(head, dhead));
			Double tailsim = new Double(dw*ConceptualComparer.compare(tail, dtail));
			
			Double score = ld * ((hsim + tailsim)/2); //other possible formulations: hsim*tailsim ; Math.sqrt(hsim+tailsim);
			
			tmpVA.add(new DepAlignment(dd, score.doubleValue()));
		}
		
		Collections.sort(tmpVA);
		if(tmpVA.get(0).getScoreValue() > 0.5) alMap.put(d, tmpVA); //TODO: threshold > 0.5 ??
		
		return tmpVA.get(0);
		
		/*System.err.println("Dep1: "+d.toString()+" aligned: ");
		for(DepAlignment da : tmpVA){
			System.err.println(da.getDependency().toString()+" : score "+da.getScoreValue());
		}
		System.err.println("--------------");*/
		
		//TODO: antonimi + sim holos
		//TODO: Named Entities???

	}
	
	/**
	 * This method sets the alignments for each dependency
	 */
	public void setAlignments(){
		
		HashSet<Dependency> d2unaligned = new HashSet<Dependency>();
		d2unaligned.addAll(d2);
		for(Dependency d : d1) {
			DepAlignment match = getBestDep(d, this.d2);
			
			System.err.println("Dep1: "+d.toString()+" aligned: "+match.getDependency().toString()+" score: "+match.getScoreValue());
			
		}
		
		d2unaligned.removeAll(alMap.keySet()); //set aligned dependencies
		
		//now try to align deps in d2 who haven't been aligned
		for(Dependency u : d2unaligned){
			DepAlignment match = getBestDep(u, this.d1);
			
			System.err.println("Dep2: "+u.toString()+" aligned: "+match.getDependency().toString()+" score: "+match.getScoreValue());
		}
	}
	
	/**
	 * Calculates the score of the dependencies
	 * @return
	 */
	public double getDepScore(){
		double sum=0d;
		double N = (double)alMap.keySet().size();
		for(Dependency k : alMap.keySet()){
			sum+=alMap.get(k).elementAt(0).getScoreValue();
		}
		return sum/N;
	}
	

}
