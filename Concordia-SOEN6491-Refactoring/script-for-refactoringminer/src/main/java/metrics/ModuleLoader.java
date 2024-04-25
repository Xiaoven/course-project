package metrics;

import java.util.List;

/**
 * Load the modules according to different config files, e.g., settings.gradle
 */
public abstract class ModuleLoader {
    protected String projectPath;
    protected List<String> excludePaths;

    public ModuleLoader(String projectPath) {
        this.projectPath = projectPath;
    }

    public abstract void loadModules(MetricsCalculator metricsCalculator);
    public void setProjectPath(String projectPath) {
        this.projectPath = projectPath;
    }

    public void setExcludePaths(List<String> list) {
        excludePaths = list;
    }
}
