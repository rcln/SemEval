package fr.lipn.sts.ner;

import java.io.BufferedReader;
import java.io.File;
import java.io.Reader;
import java.io.StringReader;
import java.util.List;
import java.util.Vector;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.trees.Tree;

public class DBPediaChunkBasedAnnotator {
	private String termIndexPath;
	private LexicalizedParser parser;
	
	private static int MAX_ANNOTS=5; //take only the first?

	public DBPediaChunkBasedAnnotator(String termIndexPath) {
		this.termIndexPath=termIndexPath;
		 parser = LexicalizedParser.loadModel("lib/englishPCFG.ser.gz");
	}
	
	public Vector<String> annotate(String document) {
		Vector<String> ret = new Vector<String>();
		
		try {
			IndexReader reader = IndexReader.open(FSDirectory.open(new File(termIndexPath)));
			IndexSearcher searcher = new IndexSearcher(reader);
			searcher.setSimilarity(new BM25Similarity());
			
			Analyzer analyzer = new EnglishAnalyzer(Version.LUCENE_44);
			
			Reader r = new BufferedReader(new StringReader(document));
			Vector<String> fragments = new Vector<String>();
			
			for(List<HasWord> sentence : new DocumentPreprocessor(r)) {
				Tree parse = parser.apply(sentence);
				for(Tree p : parse){
					if(p.label().value().equals("NP") && p.isPrePreTerminal()) {
						//p.pennPrint();
						StringBuffer tmpstr = new StringBuffer();
						for(Tree l : p.getLeaves()){
							
							tmpstr.append(l.label().toString());
							tmpstr.append(" ");
						}
						fragments.add(tmpstr.toString().trim());
						System.err.println("Chunk found: "+tmpstr);
					}
					
				}
			}
			
			
			for(String fragment :  fragments) {
				
				if(fragment.length()==0) continue;
				System.err.println("Annotating: "+fragment);
						
				QueryParser parser = new QueryParser(Version.LUCENE_44, "title", analyzer);
				Query query = parser.parse(fragment);
				
				TopDocs results = searcher.search(query, 20);
			    ScoreDoc[] hits = results.scoreDocs;
			    
			    int numTotalHits = results.totalHits;
			    System.err.println(numTotalHits + " total matching articles");
			    
			    if(numTotalHits > 0) {
				    hits = searcher.search(query, numTotalHits).scoreDocs;
				    for(int i=0; i< Math.min(numTotalHits, MAX_ANNOTS); i++){
				    	Document doc = searcher.doc(hits[i].doc);
				    	String id = doc.get("id");
				    	String categories = doc.get("categories");
				    	ret.add(id);
				    	System.err.println(id);
				    }
			    }
								 
			}
			
			reader.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return ret;
	}
}
