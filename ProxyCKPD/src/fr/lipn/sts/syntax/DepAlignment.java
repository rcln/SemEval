package fr.lipn.sts.syntax;

public class DepAlignment implements Comparable<DepAlignment> {
	Dependency d1;
	Dependency d2;
	Double score;
	
	public DepAlignment(Dependency d1, Dependency d2, double score){
		this.d1=d1;
		this.d2=d2;
		this.score = new Double(score);
	}

	@Override
	public int compareTo(DepAlignment o) {
		return this.score.compareTo(o.score);
	}
	
	
}
