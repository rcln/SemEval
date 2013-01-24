package fr.lipn.sts.syntax;

import java.util.Vector;

public class DepPair {
	Vector<Dependency> d1;
	Vector<Dependency> d2;
	
	public DepPair(Vector<Dependency> d1, Vector<Dependency> d2){
		this.d1=d1; this.d2=d2;
	}

}
