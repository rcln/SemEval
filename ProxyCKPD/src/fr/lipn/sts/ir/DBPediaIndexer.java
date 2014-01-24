package fr.lipn.sts.ir;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;
import org.grep4j.core.model.Profile;
import org.grep4j.core.model.ProfileBuilder;
import org.grep4j.core.result.GrepResult;
import org.grep4j.core.result.GrepResults;

import static org.grep4j.core.Grep4j.grep;
import static org.grep4j.core.Grep4j.constantExpression;
import static org.grep4j.core.fluent.Dictionary.on;


public class DBPediaIndexer {
	
	public static void main(String[] args) throws IOException {
		String indexPath = "/tempo/corpora/DBPedia/indexed";
		String fileName = "/tempo/corpora/DBPedia/abstracts/long_abstracts_en.nt";
		
		Directory dir = FSDirectory.open(new File(indexPath));
	    Analyzer analyzer = new EnglishAnalyzer(Version.LUCENE_44);
	    IndexWriterConfig iwc = new IndexWriterConfig(Version.LUCENE_44, analyzer);
		iwc.setSimilarity(new BM25Similarity());
	    iwc.setOpenMode(OpenMode.CREATE);
	    
	    IndexWriter writer = new IndexWriter(dir, iwc);
	    
	    FileInputStream in = new FileInputStream(fileName);
	    //BZip2CompressorInputStream bzIn = new BZip2CompressorInputStream(in);
	    BufferedReader reader = new BufferedReader(new InputStreamReader(in));
	    
	    String line="";
	    
	    int i=0;
	    
	    Profile localProfile = ProfileBuilder.newBuilder()
                .name("Category file")
                .filePath("/tempo/corpora/DBPedia/categories/article_categories_en.nt")
                .onLocalhost()
                .build();

	    
	    Document currentDoc;
	    
	    while( (line = reader.readLine()) != null) {
	    	if(line.startsWith("#")) continue;
	    	String [] elems = line.split("> ");
	    	String id = elems[0].concat(">");
	    	
	    	//System.err.println(id+" -> grepping: ");
	    	GrepResults results = grep(constantExpression(id), on(localProfile));
	    	StringBuffer categ = new StringBuffer();
	    	
	    	for(GrepResult gr : results){
	    		String rawText=gr.getText().replace('*', '.');
	    		String cat = rawText.replaceAll(id+" <http://purl.org/dc/terms/subject> ", "");
	    		cat= cat.replaceAll(" \\.", "");
	    		categ.append(cat+" ");
	    		//System.err.println(cat);
	    	}
	    	//System.err.println("Total categories found : " + results.totalLines());
	    	
	    	String head = elems[0].replaceAll("<http://dbpedia.org/resource/", "");
	    	head=head.replaceAll("_", " ");
	    	String tail = elems[2].replaceAll("@en..", "");
	    	
	    	if(!tail.startsWith("\"\"")) {
	    		currentDoc= new Document();
	    		currentDoc.add(new Field("id", id, Field.Store.YES, Field.Index.NOT_ANALYZED));
	    		currentDoc.add(new Field("title", head, Field.Store.YES, Field.Index.ANALYZED));
		    	currentDoc.add(new Field("abstract", tail, Field.Store.YES, Field.Index.ANALYZED));
		    	currentDoc.add(new Field("categories", categ.toString(), Field.Store.YES, Field.Index.ANALYZED));
		    	writer.addDocument(currentDoc);
		    	System.err.print(".");
	    		//System.err.println(head+" -> "+tail);
	    	}
	    	
	    	if (i % 81 == 0) {
	    		System.err.println();
	    	}
	    	i++;
	    	//if (i> 10) break;
	    }
	    
	    
	    System.out.println("Read "+i+" lines.");
	    
	    reader.close();
	    writer.close();


	}

}
