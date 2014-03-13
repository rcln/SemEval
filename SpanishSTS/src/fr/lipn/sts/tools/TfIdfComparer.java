package fr.lipn.sts.tools;

import java.util.HashMap;
import java.util.HashSet;

import edu.upc.freeling.ListWordIterator;
import edu.upc.freeling.Sentence;
import edu.upc.freeling.Word;

public class TfIdfComparer {

	public static double compare(Sentence tSentence, Sentence tSentence1){
		HashMap<String, Integer> freqs1 = new HashMap<String, Integer>();
		HashMap<String, Integer> freqs2 = new HashMap<String, Integer>();
		
		HashSet<String> shared = new HashSet<String>();
		HashMap<String, Double> idfs = new HashMap<String, Double>();
		
		ListWordIterator wIt = new ListWordIterator(tSentence);
		while(wIt.hasNext()){
			Word tw=wIt.next();
			String w = tw.getForm();
			Integer freq = freqs1.get(w);
			if(freq == null) freq=new Integer(1);
			else freq = new Integer(freq.intValue()+1);
			freqs1.put(w, freq);
			Double idf = idfs.get(w);
			if(idf==null){
				idf = GoogleTFFactory.getIDF(w);
				idfs.put(w, idf);
			}
		}
		
		ListWordIterator wIt1 = new ListWordIterator(tSentence1);
		while(wIt1.hasNext()){
			Word tw=wIt1.next();
			String w = tw.getForm();
			Integer freq = freqs2.get(w);
			if(freq == null) freq=new Integer(1);
			else freq = new Integer(freq.intValue()+1);
			freqs2.put(w, freq);
			Double idf = idfs.get(w);
			if(idf==null){
				idf = GoogleTFFactory.getIDF(w);
				idfs.put(w, idf);
			}
		}
		
		shared.addAll(freqs1.keySet());
		shared.retainAll(freqs2.keySet());
		
		double num = 0.0;
		for(String s : shared){
			double a = freqs1.get(s).doubleValue()*idfs.get(s);
			double b = freqs2.get(s).doubleValue()*idfs.get(s);
			num+=(a*b);
		}
		
		double d1 = 0.0;
		for(String s : freqs1.keySet()){
			double a = freqs1.get(s).doubleValue()*idfs.get(s);
			d1+=Math.pow(a, 2.0d);
		}
		
		double d2 = 0.0;
		for(String s : freqs2.keySet()){
			double a = freqs2.get(s).doubleValue()*idfs.get(s);
			d2+=Math.pow(a, 2.0d);
		}
		
		double den = Math.sqrt(d1)*Math.sqrt(d2);
		
		return (num/den);
	}
}
