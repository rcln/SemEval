package fr.lipn.sts.syntax;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Vector;

import edu.stanford.nlp.ling.TaggedWord;

public class DepPair {
	Vector<Dependency> d1;
	Vector<Dependency> d2;
	
	HashMap<Dependency, Vector<DepAlignment>> alMap; //maps deps to a list of possible (scored) alignments
	
	public DepPair(Vector<Dependency> d1, Vector<Dependency> d2){
		this.d1=d1; this.d2=d2;
		alMap = new HashMap<Dependency, Vector<DepAlignment>>();
	}

	public void setPOStags(ArrayList<TaggedWord> tSentence,
			ArrayList<TaggedWord> tSentence1) {
		
		for(Dependency d : d1) {
			int hp = d.head.getPosition()-1;
			if(hp >= 0){
				d.head.setPOS(tSentence.get(hp).tag());
			}	
			int tp = d.dependent.getPosition()-1;
			d.dependent.setPOS(tSentence.get(tp).tag());
		}
		
		for(Dependency d : d2) {
			int hp = d.head.getPosition()-1;
			if(hp >= 0){
				d.head.setPOS(tSentence.get(hp).tag());
			}	
			int tp = d.dependent.getPosition()-1;
				
			d.dependent.setPOS(tSentence.get(tp).tag());
		}
		
	}
	
	/**
	 * This method sets the alignments for each dependen
	 */
	public void setAlignments(){
		for(Dependency d : d1) {
			int hp = d.head.getPosition()-1;
			String label = d.label;
			DepWord head = d.head;
			DepWord tail = d.dependent;
			//TODO: scorrere d2 ed assegnare i pesi a: label, head e dependent per ogni dep in d2
			//il vettore di alignments poi si ordina e si prende il miglior risultato
			//bisogna estrarre i synset per head e dependent
			//levenshtein su label
			
			if(hp >= 0){
				d.head.setPOS(tSentence.get(hp).tag());
			}	
			int tp = d.dependent.getPosition()-1;
			d.dependent.setPOS(tSentence.get(tp).tag());
		}
	}
	

}
