package metrics;

import java.util.LinkedList;
import java.util.List;

public class ConstantModuleLoader extends ModuleLoader{
    private final List<String> compileSourceRoots;
    private final List<String> testCompileSourceRoots;

    public ConstantModuleLoader(List<String> relativeCompileSourceRoots, List<String> relativeTestCompileSourceRoots) {
        super(null);
        this.compileSourceRoots = relativeCompileSourceRoots;
        this.testCompileSourceRoots = relativeTestCompileSourceRoots;
    }

    @Override
    public void loadModules(MetricsCalculator metricsCalculator){
        List<String> compileSrc = new LinkedList<>();
        List<String> testSrc = new LinkedList<>();
        for(String src: compileSourceRoots) {
            compileSrc.add(projectPath + "/" + src);
        }

        for(String src: testCompileSourceRoots) {
            testSrc.add(projectPath + "/" + src);
        }

        metricsCalculator.setCompileSourceRoots(compileSrc);
        metricsCalculator.setTestCompileSourceRoots(testSrc);
    }
}
