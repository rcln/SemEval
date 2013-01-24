package fr.irit.sts.proxygenea;

public class PathNode {
	String id;
	int depth;
	
	public PathNode(String id, int depth){
		this.id=id;
		this.depth=depth;
	}
	
	public int depth(){
		return depth;
	}
	
	public String name(){
		return id;
	}
}
