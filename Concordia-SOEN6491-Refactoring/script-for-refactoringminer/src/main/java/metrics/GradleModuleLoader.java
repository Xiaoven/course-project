package metrics;

import utils.Util;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.FileVisitOption;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class GradleModuleLoader extends ModuleLoader {
    private final Logger logger;

    public GradleModuleLoader(String projectPath, Logger logger) {
        super(projectPath);
        this.logger = logger;
    }

    private boolean isInExcludePaths(String path) {
        if (excludePaths != null)
            for (String p : excludePaths)
                if (path.contains(p))
                    return true;
        return false;
    }

    public List<String> findGradleFiles(){
        Path startDir = Paths.get(projectPath);

        List<String> result = new ArrayList<>();

        try {
            Files.walk(startDir, Integer.MAX_VALUE, FileVisitOption.FOLLOW_LINKS)
                    .filter(path -> !Files.isDirectory(path) &&
                            (path.toString().endsWith(".gradle.kts") || path.toString().endsWith(".gradle")) &&
                            !isInExcludePaths(path.toString()))
                    .map(Path::getParent)
                    .map(Path::toString)
                    .forEach(result::add);
        } catch (IOException e) {
            logger.log(Level.SEVERE, e.getMessage(), e);
        }

        return result;
    }

    private List<String> getModules(String settingsGradlePath) {
        List<String> modules = new ArrayList<>();

        if (Util.checkExistence(settingsGradlePath))
            return modules;

        try (BufferedReader reader = new BufferedReader(new FileReader(settingsGradlePath))) {
            // Read the entire settings.gradle file
            StringBuilder sb = new StringBuilder();
            String line;

            while ((line = reader.readLine()) != null) {
                sb.append(line).append("\n");
            }
            String content = sb.toString();

            // Define regex pattern to match include statements
            Pattern pattern = Pattern.compile("include\\s*((?:'[\\w:-]+'\\s*,\\s*)*\\s*'[\\w:-]+')", Pattern.MULTILINE);

            // Find all matches of include statements
            Matcher matcher = pattern.matcher(content);
            while (matcher.find()) {
                String[] modulesArray = matcher.group(1).split(",");
                for (String module : modulesArray) {
                    // Remove surrounding whitespace and quotes
                    String moduleName = module.trim().replaceAll("[\"']", "");
                    moduleName = moduleName.replace(":", "/");
                    modules.add(moduleName);
                }
            }
        } catch (IOException e) {
            logger.log(Level.SEVERE, e.getMessage(), e);
        }

        return modules;
    }

    @Override
    public void loadModules(MetricsCalculator metricsCalculator) {
        List<String> modules = getModules(projectPath + "/settings.gradle");

        List<String> compileSourceRoots = new LinkedList<>();
        List<String> testCompileSourceRoots = new LinkedList<>();

        if (modules.isEmpty()) {
            modules = findGradleFiles();
            for (String module : modules)
                Util.fillSourceRoots(module, compileSourceRoots, testCompileSourceRoots);
        } else {
            for (String module : modules)
                Util.fillSourceRoots(this.projectPath + "/" + module, compileSourceRoots, testCompileSourceRoots);
        }

        logger.info("Modules: " + String.join(", ", modules));

        metricsCalculator.setCompileSourceRoots(compileSourceRoots);
        metricsCalculator.setTestCompileSourceRoots(testCompileSourceRoots);
    }

}
