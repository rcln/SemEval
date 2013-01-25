package fr.lipn.sts.syntax;

import edu.stanford.nlp.ling.TaggedWord;

public class DepWord {
	private String word;
	private int position;
	private String POS;
	
	public DepWord(String seq){
		String [] items = seq.split("-");
		try{
			this.word=items[0];
			this.position=Integer.parseInt(items[1]);
		} catch (Exception e) {
			//format error
			this.word="";
			this.position=-1;
		}
		
		POS=null;
	}
	
	public boolean isRoot(){
		return (position==0) && word.equals("ROOT");
	}
	
	public String getWord(){
		return word;
	}
	
	public int getPosition(){
		return position;
	}
	
	public void setPOS(String pos){
		this.POS=pos;
	}
}
