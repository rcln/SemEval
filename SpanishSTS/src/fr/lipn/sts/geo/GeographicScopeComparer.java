package fr.lipn.sts.geo;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.HashSet;


import edu.upc.freeling.ListWordIterator;
import edu.upc.freeling.Sentence;
import edu.upc.freeling.Word;
import fr.lipn.sts.SpanishSTSComparer;

public class GeographicScopeComparer {
	private static double NORM_DIST=10000; //assume 10000Km as the maximal distance we can found;  we did this to align with GS scores
	
	public static HashSet<String> getLocsforNE(String ne){
		Connection c = null;
	    Statement stmt = null;
	    HashSet<String> locs = new HashSet<String>();
	    try {
	      Class.forName("org.sqlite.JDBC");
	      c = DriverManager.getConnection("jdbc:sqlite:res/yagoLeaders.db");
	      c.setAutoCommit(false);
	      
	      stmt = c.createStatement();
	      ResultSet rs = stmt.executeQuery( "SELECT * FROM leaders WHERE fullname=\""+ne+"\" OR lastname =\""+ne+"\" ;" );
	      while ( rs.next() ) {
	         String  off = rs.getString("offset");
	         locs.add("n"+off);
	      }
	      rs.close();
	      stmt.close();
	      c.close();
	    } catch ( Exception e ) {
	      System.err.println( e.getClass().getName() + ": " + e.getMessage() );
	      System.exit(-1);
	    }
	    return locs;
	}
	
	public static double compare(Sentence cSentence, Sentence cSentence1) {
		HashSet<String> off1= new HashSet<String>();
		HashSet<String> off2= new HashSet<String>();
		
		/** find person names **/
        ListWordIterator wIt = new ListWordIterator(cSentence);
        while (wIt.hasNext()) {
          Word w = wIt.next();
          String tag = w.getTag();
          if(tag.startsWith("NP00SP0")) {
        	  off1.addAll(getLocsforNE(w.getForm()));
			  if(SpanishSTSComparer.VERBOSE) System.err.println("got geoinfo for leader "+w.getForm());
          }
          //System.out.print(w.getForm() + " " + w.getLemma() + " " + w.getTag() );
        }

	    ListWordIterator wIt1 = new ListWordIterator(cSentence1);
        while (wIt1.hasNext()) {
          Word w = wIt1.next();
          String tag = w.getTag();
          if(tag.startsWith("NP00SP0")) {
        	  if(tag.startsWith("NP00SP0")) {
            	  off2.addAll(getLocsforNE(w.getForm()));
    			  if(SpanishSTSComparer.VERBOSE) System.err.println("got geoinfo for leader "+w.getForm());
              }
          }
        }				          
	    
		wIt = new ListWordIterator(cSentence);
		while(wIt.hasNext()){
			Word tw=wIt.next();
			String ppos =tw.getTag();
			if (ppos.matches("(N|V|A|R).+")) {
				String[] elems= tw.getSensesString(0).split("/");
				String[] tmpWgt= elems[0].split(":");
				String[] offPOS= tmpWgt[0].split("\\-");
				if(offPOS.length > 1) {
					String pos="n";
					if(ppos.startsWith("V")) pos="v";
					if(ppos.startsWith("A")) pos="a";
					if(ppos.startsWith("R")) pos="r";
					
					String synID=pos+String.format("%08d", Integer.parseInt(offPOS[0]));
					if(BlueMarble.hasLocs(synID)) {
						if(SpanishSTSComparer.VERBOSE) System.err.println("Found geoinfo for : "+tw.getLemma());
						off1.add(synID);
					}
					
				}
			}
		}
		
		wIt1 = new ListWordIterator(cSentence1);
		while(wIt1.hasNext()){
			Word tw=wIt1.next();
			String ppos =tw.getTag();
			if (ppos.matches("(N|V|A|R).+")) {
				String[] elems= tw.getSensesString(0).split("/");
				String[] tmpWgt= elems[0].split(":");
				String[] offPOS= tmpWgt[0].split("\\-");
				if(offPOS.length > 1) {
					String pos="n";
					if(ppos.startsWith("V")) pos="v";
					if(ppos.startsWith("A")) pos="a";
					if(ppos.startsWith("R")) pos="r";
					
					String synID=pos+String.format("%08d", Integer.parseInt(offPOS[0]));
					if(BlueMarble.hasLocs(synID)) {
						if(SpanishSTSComparer.VERBOSE) System.err.println("Found geoinfo for : "+tw.getLemma());
						off2.add(synID);
					}
					
				}
			}
		}

		/*** now compute weights **/
		
		if(off1.size()==0 && off2.size()==0) {
			//no places available for both sentences: probably they are geographically not constrained
			//they are compatible from a geographical point of view
			return 1d;
		}
		
		if((off1.size() * off2.size()) ==0) {
			//one sentences contain places but the other don't
			//they are not compatible from a geographical point of view
			return 0d;
		}
		
		//in all other cases, try to establish a geographic distance
		double sumMinimalDist=0d;
		int numPairs=0;
		for(String id : off1) {
			double minDist=NORM_DIST;
			for(String id2 : off2) {
				double d =BlueMarble.getMinDistance(id, id2);
				//if(SemanticComparer.VERBOSE) System.err.println("minDistance between: "+id+" and "+id2+" : "+d);
				if (d < minDist) minDist=d;
				numPairs++;
			}
			//if(SemanticComparer.VERBOSE) System.err.println("minDist for: "+id+" : "+minDist);
			sumMinimalDist+=minDist;
		}
		
		double avgSumDist=sumMinimalDist/(double)numPairs;
		
		//System.err.println("sum of minimal distances: "+sumMinimalDist);
		
		double geoSim=1-(Math.log(1+avgSumDist)/Math.log(NORM_DIST));
		
		return geoSim;
	}
}
