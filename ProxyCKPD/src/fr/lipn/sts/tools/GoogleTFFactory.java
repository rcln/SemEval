package fr.lipn.sts.tools;

import java.io.File;
import java.io.IOException;

import jweb1t.FileSearch;

public class GoogleTFFactory {
	private static String dictFile="Z:/SemEval/vocab/vocab"; //Google 1-grams frequency file
	private static FileSearch fileSearcher;
	public static long MAX_FREQ=30578667846L;//95119665584L;
	
	public static void init(String dictionary){
		dictFile=dictionary;
		init();
	}
	
	public static void init(){
		System.err.println("Init Google1T frequency counter...");
		File file = new File(dictFile);
		try {
			fileSearcher= new FileSearch(file);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public static long getFrequency(String term){
		try {
			return fileSearcher.getFreq(term)+1; //+1 added for smoothing of unseen terms
		} catch (IOException e) {
			e.printStackTrace();
			return 1; //1 added for smoothing of unseen terms
		}
	}
	
}
