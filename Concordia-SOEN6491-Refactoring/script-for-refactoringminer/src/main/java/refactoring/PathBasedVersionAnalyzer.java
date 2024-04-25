package refactoring;

import org.refactoringminer.api.GitHistoryRefactoringMiner;
import org.refactoringminer.rm1.GitHistoryRefactoringMinerImpl;
import utils.Util;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;

public class PathBasedVersionAnalyzer extends BasicVersionAnalyzer{
    private final String rootDir;
    private final String projectOutputPath;
    private final GitHistoryRefactoringMiner miner;

    public PathBasedVersionAnalyzer(String rootDir, String projectOutputPath) {
        this.rootDir = rootDir;
        this.projectOutputPath = projectOutputPath;
        this.miner = new GitHistoryRefactoringMinerImpl();
    }

    public void detectTags(String oldTag, String newTag) {
        Map<String, List<String>> refactoringMap = new ConcurrentHashMap<>();
        try {
            File fileOld = new File(rootDir + "/" + oldTag);
            File fileNew = new File(rootDir + "/" + newTag);

            // detect refactorings
            miner.detectAtDirectories(fileOld, fileNew, getHandler(refactoringMap));

            // write refactoringMap
            writeMapToJsonFile(refactoringMap, String.format("%s/%s-%s.json", this.projectOutputPath, oldTag, newTag));
        } catch (Exception e) {
            logger.log(Level.SEVERE, String.format("Failed to detect %s -> %s", oldTag, newTag), e);
        }
    }

    public void detect(String[] orderedTags) {
        if (orderedTags.length < 2) {
            logger.info("length of tag array < 2");
            return;
        }

        int idxOld = 0;
        int idxNew = 1;

        while (idxNew < orderedTags.length) {
            detectTags(orderedTags[idxOld], orderedTags[idxNew]);
            idxOld++;
            idxNew++;
        }
    }

    public static void main(String[] args) throws IOException {
        long startTime = System.currentTimeMillis();
        logger.info("Start Time: " + startTime);

        PathBasedVersionAnalyzer analyzer = new PathBasedVersionAnalyzer(
                "/Users/xiaowen/Documents/GitHub/jedit-svn-r25713-jEdit-tags",
                "/Users/xiaowen/Documents/GitHub/SOEN6491-project/RQ3/refactorings/jedit");

        String[] tags = Util.readTagsConfig("/Users/xiaowen/Documents/GitHub/SOEN6491-project/RQ3/tags/jedit.txt");
        analyzer.detect(tags);

        long endTime =  System.currentTimeMillis();
        logger.info("End Time: " + endTime);
        logger.info("Duration: " + (endTime - startTime) + " milliseconds");
    }
}
