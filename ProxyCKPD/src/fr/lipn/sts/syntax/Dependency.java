package fr.lipn.sts.syntax;

public class Dependency {
	String label;
	DepWord head;
	DepWord dependent;
	
	public Dependency(String label, String head, String dependent){
		this.label=label;
		this.head=new DepWord(head);
		this.dependent=new DepWord(dependent);
	}
	
	
}
