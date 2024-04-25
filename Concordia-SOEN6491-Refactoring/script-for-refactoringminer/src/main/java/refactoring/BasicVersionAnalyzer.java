package refactoring;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.apache.commons.io.FileUtils;
import org.refactoringminer.api.Refactoring;
import org.refactoringminer.api.RefactoringHandler;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

public class BasicVersionAnalyzer {
    protected static final Logger logger = Logger.getLogger(BasicVersionAnalyzer.class.getSimpleName());
    // Initialize the logger and file handler
    static {
        try {
            String logFilePath = String.format("out/%s.log", BasicVersionAnalyzer.class.getName());
            Files.createDirectories(FileSystems.getDefault().getPath(logFilePath).getParent());
            FileHandler fileHandler = new FileHandler(logFilePath);
            fileHandler.setFormatter(new SimpleFormatter());
            logger.addHandler(fileHandler);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    protected static RefactoringHandler getHandler(Map<String, List<String>> refactoringMap) {
        return new RefactoringHandler() {
            @Override
            public void handle(String commitId, List<Refactoring> refactorings) {
                if (!refactorings.isEmpty()) {
                    List<String> refactoringJsonList = refactoringMap.computeIfAbsent(commitId,
                            key -> new LinkedList<>());

                    for (Refactoring ref : refactorings) {
                        refactoringJsonList.add(ref.toJSON());
                    }
                }
            }

            @Override
            public void handleException(String commitId, Exception e) {
                // Log commit ID and exception information
                logger.log(Level.SEVERE, "Commit ID: " + commitId, e);
            }
        };
    }

    protected static void writeMapToJsonFile(Map<String, List<String>> map, String filePath) {
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            // set pretty output format
            objectMapper.enable(SerializationFeature.INDENT_OUTPUT);

            // convert map to string
            String json = objectMapper.writeValueAsString(map);

            // create files and missing parent directories
            File file = new File(filePath);
            file.getParentFile().mkdirs();

            // write json to file
            FileUtils.writeStringToFile(file, json, StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new RuntimeException("Error writing JSON file", e);
        }
    }
}
