package metrics;

import com.github.mauricioaniche.ck.CK;
import utils.Util;

import java.io.File;
import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

public class MetricsCalculator {
    protected static final Logger logger = Logger.getLogger(MetricsCalculator.class.getSimpleName());
    // Initialize the logger and file handler
    static {
        try {
            String logFilePath = String.format("out/%s.log", MetricsCalculator.class.getSimpleName());
            Files.createDirectories(FileSystems.getDefault().getPath(logFilePath).getParent());
            FileHandler fileHandler = new FileHandler(logFilePath);
            fileHandler.setFormatter(new SimpleFormatter());
            logger.addHandler(fileHandler);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    protected String projectPath;
    protected ModuleLoader moduleLoader;
    protected List<String> compileSourceRoots;
    protected List<String> testCompileSourceRoots;
    protected String outputDir;
    protected List<String> excludePaths;

    public MetricsCalculator(String projectPath) {
        this.projectPath = projectPath;
        this.outputDir  = projectPath + "/out-metrics";
    }

    public void setExcludePaths(List<String> list) {
        excludePaths = list;
    }

    public void setCompileSourceRoots(List<String> compileSourceRoots) {
        this.compileSourceRoots = compileSourceRoots;
    }

    public void setTestCompileSourceRoots(List<String> testCompileSourceRoots) {
        this.testCompileSourceRoots = testCompileSourceRoots;
    }

    public void setOutputDir(String outDir) {
        this.outputDir = outDir;
    }

    public void compute() {
        for (String dirName : this.compileSourceRoots) {
            processSourceDirectory(dirName);
        }

        for (String dirName : this.testCompileSourceRoots) {
            processSourceDirectory(dirName);
        }
    }

    protected void processSourceDirectory(String dirName) {
        try {
//            logger.info("Processing " + dirName);
            if (new File(dirName).exists()) {
                // set output
                String outDir = this.outputDir + "/" + dirName.substring(this.projectPath.length());
                Files.createDirectories(Paths.get(outDir));
                MetricsWriter writer = new MetricsCSVWriter(outDir);

                new CK().calculate(dirName, writer);
                writer.finish();
            }
        } catch (Exception e) {
            logger.log(Level.SEVERE, e.getMessage(), e);
        }
    }

    protected void initModuleLoader() throws Exception {
        if (Util.checkExistence(projectPath + "/pom.xml")) {
            this.moduleLoader = new MavenModuleLoader(this.projectPath, logger);
        }
        else if (Util.checkExistence(projectPath + "/build.gradle") || Util.checkExistence(projectPath + "/build.gradle.kts")) {
            this.moduleLoader = new GradleModuleLoader(this.projectPath, logger);
        }
        else {
            throw new Exception("Not a maven or gradle project");
        }
    }
}
