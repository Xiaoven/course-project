package metrics;

import utils.Util;

import java.io.IOException;
import java.util.Collections;
import java.util.logging.Level;

public class PathBasedMetricsCalculator extends MetricsCalculator{
    private String rootDir;
    public PathBasedMetricsCalculator(String rootDir) throws IOException {
        super(rootDir);
        this.rootDir = rootDir;
    }

    public void compute(String[] tags, String outputRoot) {
        for (String tag: tags) {
            logger.info("Processing tag " + tag);
            setOutputDir(outputRoot + "/" + tag);
            try {
                this.projectPath = this.rootDir + "/" + tag;
                initModuleLoader();
                moduleLoader.loadModules(this);

                compute();
            } catch (Exception e) {
                logger.log(Level.SEVERE, "Fail for tag " + tag + "\t" + e.getMessage(), e);
            }
        }
    }

    public static void main(String[] args) throws IOException {
        String root = "/Users/xiaowen/Documents/GitHub/jedit-svn-r25713-jEdit-tags";
        ModuleLoader loader = new ConstantModuleLoader(
                Collections.singletonList("org"), Collections.singletonList("test"));
        PathBasedMetricsCalculator calculator = new PathBasedMetricsCalculator(root);

        String[] tags = Util.readTagsConfig("/Users/xiaowen/Documents/GitHub/SOEN6491-project/RQ3/tags/jedit.txt");
        calculator.compute(tags, "/Users/xiaowen/Documents/GitHub/SOEN6491-project/RQ3/metrics/jedit");
    }
}
