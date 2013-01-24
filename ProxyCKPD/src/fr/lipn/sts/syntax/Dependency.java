package fr.lipn.sts.syntax;

public class Dependency {
	String label;
	String head;
	String dependent;
	
	public Dependency(String label, String head, String dependent){
		this.label=label;
		this.head=head;
		this.dependent=dependent;
	}
	
	
}
