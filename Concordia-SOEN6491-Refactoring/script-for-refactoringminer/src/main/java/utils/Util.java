package utils;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.List;
import java.nio.file.attribute.BasicFileAttributes;

public class Util {
    public static String[] readTagsConfig(String tagsFilePath) throws IOException {
        List<String> lines = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(tagsFilePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String stripLine = line.strip();
                if (!stripLine.isEmpty())
                    lines.add(stripLine); // Strip newline characters
            }
        }
        return lines.toArray(new String[0]);
    }

    /**
     * Equivalent to shell command: `find startPath -type d -path pattern`
     * @param pattern e.g., src/main/java
     */
    public static List<String> findDirectories(String startPath, String pattern) throws IOException {
        List<String> javaDirs = new ArrayList<>();
        Files.walkFileTree(Path.of(startPath), new SimpleFileVisitor<Path>() {
            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
                return FileVisitResult.CONTINUE;
            }

            @Override
            public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) throws IOException {
                if (dir.endsWith(pattern)) {
                    javaDirs.add(dir.toString());
                }
                return FileVisitResult.CONTINUE;
            }
        });

        return javaDirs;
    }

    public static boolean checkExistence(String filePath) {
        Path path = Paths.get(filePath);
        return Files.exists(path);
    }

    public static void fillSourceRoots(String parentPath, List<String> compileSourceRoots, List<String> testCompileSourceRoots) {
        String p1 = parentPath + "/src/main/java";
        String p2 = parentPath + "/src/test/java";
        String p3 = parentPath + "/src/generated/java";

        if (Util.checkExistence(p1)) compileSourceRoots.add(p1);
        if (Util.checkExistence(p3)) compileSourceRoots.add(p3);
        if (Util.checkExistence(p2)) testCompileSourceRoots.add(p3);
    }

}
