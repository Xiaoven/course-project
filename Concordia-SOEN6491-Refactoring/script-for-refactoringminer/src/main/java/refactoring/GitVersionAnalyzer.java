package refactoring;

import org.eclipse.jgit.api.CheckoutCommand;
import org.eclipse.jgit.api.CleanCommand;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.storage.file.FileRepositoryBuilder;
import org.refactoringminer.api.GitHistoryRefactoringMiner;
import org.refactoringminer.rm1.GitHistoryRefactoringMinerImpl;
import utils.Util;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;

public class GitVersionAnalyzer extends BasicVersionAnalyzer{
    private final static String outputPath = "out";

    private final File fileOld;
    private final File fileNew;
    private final Git gitOld;
    private final Git gitNew;
    private final GitHistoryRefactoringMiner miner;
    private final String projectOutputPath;

    public GitVersionAnalyzer(String repoPathOld, String repoPathNew) throws IOException {
        this.fileOld = new File(repoPathOld);
        this.fileNew = new File(repoPathNew);
        Repository repoOld = FileRepositoryBuilder.create(new File(repoPathOld, ".git"));
        Repository repoNew = FileRepositoryBuilder.create(new File(repoPathNew, ".git"));
        this.gitOld = new Git(repoOld);
        this.gitNew = new Git(repoNew);
        this.miner = new GitHistoryRefactoringMinerImpl();
        this.projectOutputPath = outputPath + "/" + this.fileOld.getName();
    }

    private void checkout(Git git, String commitId) throws GitAPIException {
        git.checkout().setName(commitId).call();
        // Clean the working directory: git clean -fd
        git.clean().setForce(true).setCleanDirectories(true);
    }

    public void detectTags(String oldTag, String newTag) {
        Map<String, List<String>> refactoringMap = new ConcurrentHashMap<>();
        try {
            // checkout repos to the target versions
            checkout(gitOld, oldTag);
            checkout(gitNew, newTag);

            // detect refactorings
            miner.detectAtDirectories(this.fileOld, this.fileNew, getHandler(refactoringMap));

            // write refactoringMap
            writeMapToJsonFile(refactoringMap, String.format("%s/%s-%s.json", this.projectOutputPath, oldTag, newTag));
        } catch (Exception e) {
            logger.log(Level.SEVERE, String.format("Failed to detect %s -> %s", oldTag, newTag), e);
        }
    }

    /**
     * Detect two adjacent tags in the tag list
     * @param tags an order list of tags to detect
     */
    public void detectTags(String[] tags) {
        if (tags.length < 2) {
            logger.info("length of tag array < 2");
            return;
        }

        int idxOld = 0;
        int idxNew = 1;

        while (idxNew < tags.length) {
            detectTags(tags[idxOld], tags[idxNew]);
            idxOld++;
            idxNew++;
        }
    }


    public void detect(String tagsFilePath) throws IOException {
        String[] tags = Util.readTagsConfig(tagsFilePath);
        detectTags(tags);
    }

    public static void main(String[] args) throws IOException {
        long startTime = System.currentTimeMillis();
        logger.info("Start Time: " + startTime);

        String path1 = "/Users/xiaowen/Documents/GitHub/gson";
        String path2 = "/Users/xiaowen/Documents/GitHub/tmp/gson";
        GitVersionAnalyzer analyzer = new GitVersionAnalyzer(path1, path2);

        // Option 1
        analyzer.detect("/Users/xiaowen/Documents/GitHub/SOEN6491-project/RQ3/tags/gson.txt");

        // Option 2
//        // some detection failed due to NPE in refactoringMiner. Retry after fix it
//        String[] tags = new String[]{"0.10.0.0", "0.11.0.0"};
//        analyzer.detectTags(tags);


        long endTime =  System.currentTimeMillis();
        logger.info("End Time: " + endTime);
        logger.info("Duration: " + (endTime - startTime) + " milliseconds");
    }
}
