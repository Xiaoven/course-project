package metrics;

import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.storage.file.FileRepositoryBuilder;
import utils.Util;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Level;

public class GitBasedMetricsCalculator extends MetricsCalculator{

    protected final Git git;

    private boolean hackModuleLoader(String tag) throws IOException {
        this.compileSourceRoots = new ArrayList<>();
        this.testCompileSourceRoots = new ArrayList<>();

        // some old versions does not use gradle or maven
        if (projectPath.endsWith("/kafka") && tag.equals("0.8.0")
                || projectPath.endsWith("/gson") && tag.equals("gson-2.4")) {
            String[] compilePatterns = {"src/main/java", "src/main/scala", "src/generated/java"};
            String[] testPatterns = {"src/test/java", "src/test/scala"};

            for (String pattern : compilePatterns) {
                List<String> paths = Util.findDirectories(this.projectPath, pattern);
                if (!paths.isEmpty())
                    this.compileSourceRoots.addAll(paths);
            }

            for (String pattern : testPatterns) {
                List<String> paths = Util.findDirectories(this.projectPath, pattern);
                if (!paths.isEmpty())
                    this.testCompileSourceRoots.addAll(paths);
            }

            return true;
        }

        return false;
    }

    public GitBasedMetricsCalculator(String projectPath) throws IOException {
        super(projectPath);

        Repository repo = FileRepositoryBuilder.create(new File(this.projectPath, ".git"));
        this.git = new Git(repo);
    }


    protected void checkout(String tag) throws Exception {
        // `git checkout .` to remove a auto-generated file
        // docs/modules/ROOT/assets/images/servlet/architecture/filterchain.gif which prevents checkout to another tag
        git.checkout().setAllPaths(true).call();
        git.checkout().setName(tag).call();
        git.clean().setForce(true).setCleanDirectories(true);

        if (!hackModuleLoader(tag)) {
            initModuleLoader();
            this.moduleLoader.loadModules(this);
        }
    }

    public void compute(String[] tags, String outputRoot) {
        for (String tag: tags) {
            logger.info("Processing tag " + tag);
            setOutputDir(outputRoot + "/" + tag);
            try {
                checkout(tag);
                compute();
            } catch (Exception e) {
                logger.log(Level.SEVERE, "Fail for tag " + tag + "\t" + e.getMessage(), e);
            }
        }
    }

    public static void main(String[] args) throws IOException {
        List<String> excludedPaths = null;

//        String projectPath = "/Users/xiaowen/Documents/GitHub/kafka";
//        String[] tags = Util.readTagsConfig("/Users/xiaowen/Documents/GitHub/SOEN6491-project/RQ3/tags/kafka.txt");
//        String outputPath = "/Users/xiaowen/Documents/GitHub/SOEN6491-project/RQ3/metrics/kafka";


//        String projectPath = "/Users/xiaowen/Documents/GitHub/gson";
//        String[] tags = Util.readTagsConfig("/Users/xiaowen/Documents/GitHub/SOEN6491-project/RQ3/tags/gson.txt");
//        String outputPath = "/Users/xiaowen/Documents/GitHub/SOEN6491-project/RQ3/metrics/gson";


        String projectPath = "/Users/xiaowen/Documents/GitHub/spring-security";
        excludedPaths = Arrays.asList(
                "/build/", "/gradle/", "/settings.gradle", "/buildSrc/", "/build.gradle", "/.", "/out/", "/grails3/");
        String[] tags = Util.readTagsConfig("/Users/xiaowen/Documents/GitHub/SOEN6491-project/RQ3/tags/spring-security.txt");
        String outputPath = "/Users/xiaowen/Documents/GitHub/SOEN6491-project/RQ3/metrics/spring-security";


        GitBasedMetricsCalculator metricsCalculator = new GitBasedMetricsCalculator(projectPath);
        metricsCalculator.setExcludePaths(excludedPaths);
        metricsCalculator.compute(tags, outputPath);
    }
}
