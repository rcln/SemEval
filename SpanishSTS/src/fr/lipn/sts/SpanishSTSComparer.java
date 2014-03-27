package fr.lipn.sts;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Vector;

import com.martiansoftware.jsap.FlaggedOption;
import com.martiansoftware.jsap.JSAP;
import com.martiansoftware.jsap.JSAPException;
import com.martiansoftware.jsap.JSAPResult;
import com.martiansoftware.jsap.Switch;

import edu.upc.freeling.ChartParser;
import edu.upc.freeling.DepTxala;
import edu.upc.freeling.HmmTagger;
import edu.upc.freeling.ListSentence;
import edu.upc.freeling.ListSentenceIterator;
import edu.upc.freeling.ListWord;
import edu.upc.freeling.Maco;
import edu.upc.freeling.MacoOptions;
import edu.upc.freeling.Nec;
import edu.upc.freeling.Senses;
import edu.upc.freeling.Sentence;
import edu.upc.freeling.Splitter;
import edu.upc.freeling.Tokenizer;
import edu.upc.freeling.Ukb;
import edu.upc.freeling.Util;
import fr.irit.sts.proxygenea.ConceptualComparer;
import fr.lipn.sts.ckpd.NGramComparer;
import fr.lipn.sts.geo.BlueMarble;
import fr.lipn.sts.geo.GeographicScopeComparer;
import fr.lipn.sts.ir.IRComparer;
import fr.lipn.sts.ir.RBOComparer;
import fr.lipn.sts.ner.DBPediaChunkBasedAnnotator;
import fr.lipn.sts.ner.DBPediaComparer;
import fr.lipn.sts.ner.NERComparer;
import fr.lipn.sts.semantic.JWSComparer;
import fr.lipn.sts.syntax.DepComparer;
import fr.lipn.sts.tools.GoogleTFFactory;
import fr.lipn.sts.tools.LevenshteinDistance;
import fr.lipn.sts.tools.TfIdfComparer;
import fr.lipn.sts.tools.WordNet;

public class SpanishSTSComparer {
	public final static int PROXYGENEA1=0;
	public final static int PROXYGENEA2=1;
	public final static int PROXYGENEA3=2;
	public final static int WU_PALMER=3;
	public final static int LIN=4;
	public final static int JIANG_CONRATH=5;
	public static int STRUCTURAL_MEASURE=PROXYGENEA3;
	public static int IC_MEASURE=JIANG_CONRATH; //measure used for IC-weighted comparison (Lin or Jiang-Conrath)
	
	public final static int PRODUCT=0;
	public final static int GEO_MEAN=1;
	public final static int SEM_ONLY=2;
	public final static int NGRAM_ONLY=3;
	public static int COMBINATION_MODE=GEO_MEAN;
	
	public static boolean LIBSVM_OUTPUT=false;
	public static boolean TRAIN_MODE=false;
	
	public static boolean VERBOSE=false;
	
	private static final String FREELINGDIR = "/tempo/shared/freeling";
	private static final String DATA = FREELINGDIR + "/share/freeling/";
	private static final String LANG = "es";
	
	/**
	 * @param args
	 * @throws IOException 
	 * @throws ClassNotFoundException 
	 * @throws JSAPException 
	 */
		
	public static void main(String[] args) throws ClassNotFoundException, IOException, JSAPException {
		System.loadLibrary( "freeling_javaAPI" );

	    Util.initLocale( "default" );

	    // Create options set for maco analyzer.
	    // Default values are Ok, except for data files.
	    MacoOptions op = new MacoOptions( LANG );

	    op.setActiveModules(false, true, true, true, 
	                               true, true, true, 
	                               true, true, true);

	    op.setDataFiles(
	      "", 
	      DATA+LANG+"/locucions.dat", 
	      DATA + LANG + "/quantities.dat",
	      DATA + LANG + "/afixos.dat",
	      DATA + LANG + "/probabilitats.dat",
	      DATA + LANG + "/dicc.src",
	      DATA + LANG + "/np.dat",
	      DATA + "common/punct.dat");
	    
		JSAP jsap = new JSAP();
        
        
        FlaggedOption opt2 = new FlaggedOption("inputFile")
        .setStringParser(JSAP.STRING_PARSER)
        //.setDefault("Z:/SemEval/train/STS.input.MSRvid.txt") 
        .setRequired(true) 
        .setShortFlag('f') 
        .setLongFlag("file");
        
        opt2.setHelp("The SemEval file containing the sentence pairs");
        jsap.registerParameter(opt2);
        
        FlaggedOption opt4 = new FlaggedOption("frequencyFile")
        .setStringParser(JSAP.STRING_PARSER)
        //.setDefault("Z:/SemEval/vocab/vocab") 
        .setRequired(true) 
        .setShortFlag('d') 
        .setLongFlag("dict");

        opt4.setHelp("The Google Web1T Dictionary file");
        jsap.registerParameter(opt4);
        
        FlaggedOption opt5 = new FlaggedOption("WordNet")
        .setStringParser(JSAP.STRING_PARSER)
        //.setDefault("Z:/tools/WN3.0") 
        .setRequired(true) 
        .setShortFlag('w') 
        .setLongFlag("wn");

        opt5.setHelp("The WordNet installation directory");
        jsap.registerParameter(opt5);
        
        FlaggedOption opt7 = new FlaggedOption("gsFile")
        .setStringParser(JSAP.STRING_PARSER)
        .setRequired(false) 
        .setShortFlag('g') 
        .setLongFlag("gs");

        opt7.setHelp("Gold Standard file (if specified, enables train mode)");
        jsap.registerParameter(opt7);
        
        Switch sw1 = new Switch("verbose")
        .setShortFlag('v')
        .setLongFlag("verbose");

        sw1.setHelp("Requests verbose output.");
        jsap.registerParameter(sw1);
        
        FlaggedOption opt3 = new FlaggedOption("similarityMeasure")
        .setStringParser(JSAP.STRING_PARSER)
        .setDefault("pg3") 
        .setRequired(false) 
        .setShortFlag('s') 
        .setLongFlag("sim");
        
        opt3.setHelp("Similarity measure: one from\n" +
        		"pg1 - ProxyGenea1\n" +
        		"pg2 - ProxyGenea2\n" +
        		"pg3 - ProxyGenea3\n" +
        		"wu - Wu/Palmer\n");
        jsap.registerParameter(opt3);
        
        FlaggedOption opt6 = new FlaggedOption("combinationMethod")
        .setStringParser(JSAP.STRING_PARSER)
        .setDefault("gm") 
        .setRequired(false) 
        .setShortFlag('c') 
        .setLongFlag("comb");
        
        opt6.setHelp("Combination Method: one from\n" +
        		"gm - Geometric Mean\n" +
        		"so - Semantic Only\n" +
        		"no - N-grams Only\n" +
        		"pr - Product" +
        		"svr - no combination: LIBSVM-formatted output for linear regression\n");
        jsap.registerParameter(opt6);
        
        JSAPResult config = jsap.parse(args);    

        if (!config.success()) {
            
            System.err.println();

            // print out specific error messages describing the problems
            // with the command line, THEN print usage, THEN print full
            // help.  This is called "beating the user with a clue stick."
            for (java.util.Iterator errs = config.getErrorMessageIterator();
                    errs.hasNext();) {
                System.err.println("Error: " + errs.next());
            }
            
            System.err.println();
            System.err.println("Usage: java "
                                + SpanishSTSComparer.class.getName());
            System.err.println("                "
                                + jsap.getUsage());
            System.err.println();
            System.err.println(jsap.getHelp());
            System.exit(1);
        }
        
        String inputfile=config.getString("inputFile"); //"Z:/SemEval/train/STS.input.MSRvid.txt";
        
        VERBOSE=config.getBoolean("verbose");
        String dictFile=config.getString("frequencyFile");
        String wnRoot=config.getString("WordNet");
        
        String gsFile = config.getString("gsFile");
        if(gsFile != null) TRAIN_MODE=true;
        
	    String measure=config.getString("similarityMeasure");
	    List<String> availableMeasures = Arrays.asList(new String[]{"pg1", "pg2", "pg3", "wu"});
	    HashSet<String> avms = new HashSet<String>(); avms.addAll(availableMeasures);
	    if(!avms.contains(measure)){
	    	System.err.println("The specified measure does not exists, assuming pg3");
	    	measure="pg3";
	    }
	    System.err.println("setting similarity measure to "+measure);
	    if(measure.equals("pg1")) STRUCTURAL_MEASURE=PROXYGENEA1;
	    else if(measure.equals("pg2")) STRUCTURAL_MEASURE=PROXYGENEA2;
	    else if(measure.equals("pg3")) STRUCTURAL_MEASURE=PROXYGENEA3;
	    else if(measure.equals("wu")) STRUCTURAL_MEASURE=WU_PALMER;
	    
	    String combMode=config.getString("combinationMethod");
	    List<String> availableCombModes = Arrays.asList(new String[]{"gm", "pr", "so", "no", "svr"});
	    HashSet<String> avcm = new HashSet<String>(); avcm.addAll(availableCombModes);
	    if(!avcm.contains(combMode)){
	    	System.err.println("The specified combination method does not exists, assuming geometric mean");
	    	combMode="gm";
	    }
	    System.err.println("setting combination method to "+combMode);
	    if(combMode.equals("gm")) COMBINATION_MODE=GEO_MEAN;
	    else if(combMode.equals("pr")) COMBINATION_MODE=PRODUCT;
	    else if(combMode.endsWith("so")) COMBINATION_MODE=SEM_ONLY;
	    else if(combMode.endsWith("no")) COMBINATION_MODE=NGRAM_ONLY;
	    else if(combMode.endsWith("svr")) LIBSVM_OUTPUT=true;
	    
	    GoogleTFFactory.init(dictFile);
	    WordNet.init(wnRoot);
	    BlueMarble.init();
	    
	    Vector<String> gsLabels = new Vector<String>();
	    if(TRAIN_MODE){
	    	BufferedReader gsReader = new BufferedReader(new FileReader(gsFile));
	    	String str;
	    	while((str=gsReader.readLine())!=null){
	    		gsLabels.add(str.trim());
	    	}
	    	gsReader.close();
	    }
	   
	    BufferedReader reader = new BufferedReader(new FileReader(inputfile));
	    String line;
	    
	    //DepComparer.parse(inputfile+".lorg.deps.xml");
	    
	    /* FreeLing analyzers */
	    System.err.println("Init FreeLing analyzers...");
	    System.err.println("--Tokenizer...");
    	Tokenizer tk = new Tokenizer( DATA + LANG + "/tokenizer.dat" );
    	System.err.println("--Splitter...");
        Splitter sp = new Splitter( DATA + LANG + "/splitter.dat" );
        System.err.println("--Maco...");
        Maco mf = new Maco( op );
        System.err.println("--HMM Tagger...");
        HmmTagger tg = new HmmTagger( DATA + LANG + "/tagger.dat", true, 2 );
        System.err.println("--Parser...");
        ChartParser parser = new ChartParser(DATA + LANG + "/chunker/grammar-chunk.dat" );
        //DepTxala dep = new DepTxala( DATA + LANG + "/dep/dependences.dat", parser.getStartSymbol() );
        System.err.println("--NERC...");
        Nec neclass = new Nec( DATA + LANG + "/nerc/nec/nec-ab-poor1.dat" );
        System.err.println("--WSD...");
        Senses sen = new Senses(DATA + LANG + "/senses.dat" ); // sense dictionary
        Ukb dis = new Ukb( DATA + LANG + "/ukb.dat" ); // sense disambiguator
        System.err.println("Done.");
                
        int i=0;
	    while((line=reader.readLine())!=null){
	    	String [] sentences = line.split("\t");

	    	sentences[0]=sentences[0].concat(" .");
	    	sentences[1]=sentences[1].concat(" .");
	    	
	    	sentences[0]=sentences[0].replaceAll("\"", "");
	    	sentences[1]=sentences[1].replaceAll("\"", "");
	        
	    	//Extract the tokens from the line of text.
	        ListWord l1 = tk.tokenize( sentences[0] );
	        ListWord l2 = tk.tokenize( sentences[1] );
	        
	        // Split the tokens into distinct sentences.
	        ListSentence ls1 = sp.split( l1, false );
	        ListSentence ls2 = sp.split( l2, false );
	        
	        
	        // Perform morphological analysis
	        mf.analyze( ls1 );
	        mf.analyze( ls2 );
	        
	        
	        // Perform part-of-speech tagging.
	        tg.analyze( ls1 );
	        tg.analyze( ls2 );
	        
	        
	        // Perform named entity (NE) classificiation.
	        neclass.analyze( ls1 );
	        neclass.analyze( ls2 );
	        
	        
	        sen.analyze( ls1 );
	        sen.analyze( ls2 );
	        dis.analyze( ls1 );
	        dis.analyze( ls2 );
	        
	        
	        // Chunk parser
	        parser.analyze( ls1 );
	        parser.analyze( ls2 );
	        
	        
	        //DBPediaChunkBasedAnnotator chunkannotator = new DBPediaChunkBasedAnnotator("/tempo/indexes/DBPedia/indexed_es", parser);
		    
		    //double DBPsim=DBPediaComparer.compare(sentences[0], sentences[1], chunkannotator);
	        System.err.println(sentences[0]);
	        System.err.println(sentences[1]);
	        System.err.println();
	        
	        Sentence s1=null;
		    Sentence s2=null;
		    ListSentenceIterator li1 = new ListSentenceIterator(ls1);
		    ListSentenceIterator li2 = new ListSentenceIterator(ls2);
		    if(li1.hasNext()) s1=li1.next();
		    else {
		    	if(VERBOSE) System.err.println("---unable to find sentence limits for "+sentences[0]);
		    	if(TRAIN_MODE){
	    			System.out.print(gsLabels.elementAt(i)+" ");
	    		} else {
	    			System.out.print("0.0 ");
	    		}
		    	if(!VERBOSE) System.out.println("1:0.0 2:0.0 3:0.0 4:0.0 5:0.0 6:0.0 7:0.0 8:0.0");
	    		continue;
		    }
		    if(li2.hasNext()) s2=li2.next();
		    else {
		    	if(VERBOSE) System.err.println("---unable to find sentence limits for "+sentences[1]);
		    	if(TRAIN_MODE){
	    			System.out.print(gsLabels.elementAt(i)+" ");
	    		} else {
	    			System.out.print("0.0 ");
	    		}
		    	if(!VERBOSE) System.out.println("1:0.0 2:0.0 3:0.0 4:0.0 5:0.0 6:0.0 7:0.0 8:0.0");
	    		continue;
		    }
		    
		    
		    double NERsim=NERComparer.compare(ls1, ls2);
		    double sim=NGramComparer.compare(s1, s2);
		    
		    double conceptsim=ConceptualComparer.compare(s1, s2);
		    double wnsim=JWSComparer.compare(s1, s2);
		    double geosim=GeographicScopeComparer.compare(s1, s2);
		    
		    //double depsim = DepComparer.getSimilarity(i, tSentence, tSentence1);
		    double editsim = LevenshteinDistance.levenshteinSimilarity(sentences[0], sentences[1]);
		    double IRsim = IRComparer.compare(sentences[0], sentences[1]);
		    double cosinesim = TfIdfComparer.compare(s1, s2);
		    
		    if(VERBOSE) {
		    	System.err.println("Pair # "+(i+1));
		    	System.err.println(sentences[0]);
			    System.err.println(sentences[1]);
			    if(gsLabels.size()> 0) System.err.println("GS score: "+gsLabels.elementAt(i));
			    System.err.println(":");
			    System.err.println("Geosim score: "+5.0*geosim);
			    System.err.println("CKPD (n-gram) similarity: "+5.0 *sim);
			    System.err.println("Conceptual (WordNet) similarity: "+5.0 *conceptsim);
			    System.err.println("Conceptual (Jiang-Conrath) similarity: "+5.0 *wnsim);
			    //System.err.println("Dependency-based (syntactic) similarity: "+5.0 *depsim);
			    System.err.println("Edit distance similarity: "+5.0 *editsim);
			    System.err.println("Cosine distance (tf.idf) similarity: "+5.0 *cosinesim);
			    System.err.println("NER overlap : "+5.0 *NERsim);
			    System.err.println("IR-based similarity : "+5.0 *IRsim);
			    //System.err.println("DBPedia similarity : "+5.0 *DBPsim);
			    System.err.println("--------------");
			    
		    } else {
		    	if(!LIBSVM_OUTPUT){
		    		
		    		double res;
			    	if(COMBINATION_MODE==GEO_MEAN) res = 5.0 * Math.sqrt(conceptsim*sim);
			    	else if(COMBINATION_MODE==SEM_ONLY) res = 5.0 * conceptsim;
			    	else if(COMBINATION_MODE==NGRAM_ONLY) res = 5.0 * sim;
			    	else res = 5.0*conceptsim*sim;
			    	double conf_score=100*(1.0-Math.abs(conceptsim-sim)); //TODO: confidence score? this is based on the difference between the separate scores
			    	System.out.println(res+"\t"+conf_score);
			    	
		    	} else {
		    		if(TRAIN_MODE){
		    			System.out.print(gsLabels.elementAt(i)+" ");
		    		} else {
		    			System.out.print("0.0 ");
		    		}
		    		//System.out.println("1:"+sim+" 2:"+conceptsim+" 3:"+depsim+" 4:"+editsim+" 5:"+cosinesim+" 6:"+NERsim+" 7:"+wnsim+" 8:"+IRsim+" 9:"+DBPsim);
		    		System.out.println("1:"+sim+" 2:"+conceptsim+" 3:"+editsim+" 4:"+cosinesim+" 5:"+NERsim+" 6:"+wnsim+" 7:"+IRsim+" 8:"+geosim);
		    	}
		    	
		    }
		    
		    i++;
	    }
	    reader.close();
	}

}
