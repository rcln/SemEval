package fr.lipn.sts;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;

import com.martiansoftware.jsap.FlaggedOption;
import com.martiansoftware.jsap.JSAP;
import com.martiansoftware.jsap.JSAPException;
import com.martiansoftware.jsap.JSAPResult;
import com.martiansoftware.jsap.Switch;

import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import fr.irit.sts.proxygenea.ConceptualComparer;
import fr.lipn.sts.ckpd.NGramComparer;
import fr.lipn.sts.syntax.DepComparer;
import fr.lipn.sts.tools.GoogleTFFactory;
import fr.lipn.sts.tools.WordNet;

public class SemanticComparer {
	public final static int PROXYGENEA1=0;
	public final static int PROXYGENEA2=1;
	public final static int PROXYGENEA3=2;
	public final static int WU_PALMER=3;
	public static int STRUCTURAL_MEASURE=PROXYGENEA3;
	
	public final static int PRODUCT=0;
	public final static int GEO_MEAN=1;
	public final static int SEM_ONLY=2;
	public final static int NGRAM_ONLY=3;
	public static int COMBINATION_MODE=GEO_MEAN;
	
	public static boolean VERBOSE=false;
	/**
	 * @param args
	 * @throws IOException 
	 * @throws ClassNotFoundException 
	 * @throws JSAPException 
	 */
		
	public static void main(String[] args) throws ClassNotFoundException, IOException, JSAPException {

		JSAP jsap = new JSAP();
        
        FlaggedOption opt1 = new FlaggedOption("modelFile")
                                .setStringParser(JSAP.STRING_PARSER)
                                //.setDefault("Z:/tools/stanford-postagger-full-2012-03-09/models/english-bidirectional-distsim.tagger") 
                                .setRequired(true) 
                                .setShortFlag('m') 
                                .setLongFlag("model");

        opt1.setHelp("The location of the Stanford POS tagger model file");
        jsap.registerParameter(opt1);
        
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
        
        Switch sw1 = new Switch("verbose")
                        .setShortFlag('v')
                        .setLongFlag("verbose");
        
        sw1.setHelp("Requests verbose output.");
        jsap.registerParameter(sw1);
        
        FlaggedOption opt3 = new FlaggedOption("similarityMeasure")
        .setStringParser(JSAP.STRING_PARSER)
        .setDefault("pg1") 
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
        		"pr - Product\n");
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
                                + SemanticComparer.class.getName());
            System.err.println("                "
                                + jsap.getUsage());
            System.err.println();
            System.err.println(jsap.getHelp());
            System.exit(1);
        }
        
        String modelfile=config.getString("modelFile");// "Z:/tools/stanford-postagger-full-2012-03-09/models/english-bidirectional-distsim.tagger";
		String inputfile=config.getString("inputFile"); //"Z:/SemEval/train/STS.input.MSRvid.txt";
        VERBOSE=config.getBoolean("verbose");
        String dictFile=config.getString("frequencyFile");
        String wnRoot=config.getString("WordNet");
        
	    String measure=config.getString("similarityMeasure");
	    List<String> availableMeasures = Arrays.asList(new String[]{"pg1", "pg2", "pg3", "wu"});
	    HashSet<String> avms = new HashSet<String>(); avms.addAll(availableMeasures);
	    if(!avms.contains(measure)){
	    	System.err.println("The specified measure does not exists, assuming pg1");
	    	measure="pg1";
	    }
	    System.err.println("setting similarity measure to "+measure);
	    if(measure.equals("pg1")) STRUCTURAL_MEASURE=PROXYGENEA1;
	    else if(measure.equals("pg2")) STRUCTURAL_MEASURE=PROXYGENEA2;
	    else if(measure.equals("pg3")) STRUCTURAL_MEASURE=PROXYGENEA3;
	    else if(measure.equals("wu")) STRUCTURAL_MEASURE=WU_PALMER;
	    
	    String combMode=config.getString("combinationMethod");
	    List<String> availableCombModes = Arrays.asList(new String[]{"gm", "pr", "so", "no"});
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
	    
	    MaxentTagger tagger = new MaxentTagger(modelfile );
	    GoogleTFFactory.init(dictFile);
	    WordNet.init(wnRoot);
	    
	    @SuppressWarnings("unchecked")
	    BufferedReader reader = new BufferedReader(new FileReader(inputfile));
	    String line;
	    
	    DepComparer.parse(inputfile+".lorg.deps.xml");
	    
	    int i=0;
	    while((line=reader.readLine())!=null){
	    	String [] sentences = line.split("\t");
	    	//fix to set when there are points in sentences that may mislead the tagger
	    	//sentences[0] = sentences[0].replace('.', ' ');
	    	//sentences[1] = sentences[1].replace('.', ' ');
	    	sentences[0].concat(".");
	    	sentences[1].concat(".");
	    	StringReader r0 = new StringReader(sentences[0]);
	    	StringReader r1 = new StringReader(sentences[1]);
	    	
		    List<List<HasWord>> tokenizedsentences0 = tagger.tokenizeText(r0);
		    ArrayList<TaggedWord> tSentence= tagger.tagSentence(tokenizedsentences0.get(0));
		   
		    List<List<HasWord>> tokenizedsentences1 = tagger.tokenizeText(r1);
		    ArrayList<TaggedWord> tSentence1=tagger.tagSentence(tokenizedsentences1.get(0));
		    
		    double sim=NGramComparer.compare(tSentence, tSentence1);
		    double conceptsim=ConceptualComparer.compare(tSentence, tSentence1);
		    double depsim = DepComparer.getSimilarity(i, tSentence, tSentence1);
		    
		    if(VERBOSE) {
		    	System.err.println(sentences[0]);
			    System.err.println(sentences[1]);
			    System.err.println(":");
			    System.err.println(sim+" CKPD similarity , ");
			    System.err.println(conceptsim+" conceptual similarity between :");
			    System.err.println("Dependency-based similarity: "+depsim);
			    System.err.println("weight: "+5.0*(Math.sqrt(conceptsim*sim)));
			    System.err.println("--------------");
		    } else {
		    	double res;
		    	if(COMBINATION_MODE==GEO_MEAN) res = 5.0 * Math.sqrt(conceptsim*sim);
		    	else if(COMBINATION_MODE==SEM_ONLY) res = 5.0 * conceptsim;
		    	else if(COMBINATION_MODE==NGRAM_ONLY) res = 5.0 * sim;
		    	else res = 5.0*conceptsim*sim;
		    	double conf_score=100*(1.0-Math.abs(conceptsim-sim)); //TODO: confidence score? this is based on the difference between the separate scores
		    	System.out.println(res+"\t"+conf_score); 
		    }
		    
		    i++;
	    }
	    
		
	}

}
