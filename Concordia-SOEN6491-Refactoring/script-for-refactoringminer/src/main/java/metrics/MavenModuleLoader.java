package metrics;

import com.beust.jcommander.Strings;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import utils.Util;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

public class MavenModuleLoader extends ModuleLoader{
    private final Logger logger;

    public MavenModuleLoader(String projectPath, Logger logger) {
        super(projectPath);
        this.logger = logger;
    }

    public List<String> extractModulesFromPom(String pomPath) {
        List<String> modules = new ArrayList<>();

        try {
            File pomFile = new File(pomPath);
            DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
            DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
            Document doc = dBuilder.parse(pomFile);

            doc.getDocumentElement().normalize();

            NodeList moduleList = doc.getElementsByTagName("module");

            for (int i = 0; i < moduleList.getLength(); i++) {
                Node moduleNode = moduleList.item(i);
                if (moduleNode.getNodeType() == Node.ELEMENT_NODE) {
                    String moduleName = moduleNode.getTextContent().trim();
                    modules.add(moduleName);
                }
            }

        } catch (Exception e) {
            logger.log(Level.SEVERE, e.getMessage(), e);
        }

        return modules;
    }


    @Override
    public void loadModules(MetricsCalculator metricsCalculator) {
        List<String> modules = extractModulesFromPom(projectPath + "/pom.xml");
        logger.info("Modules: " + Strings.join(", ", modules));

        List<String> compileSourceRoots = new ArrayList<>();
        List<String> testCompileSourceRoots = new ArrayList<>();

        if (modules.isEmpty()) {
            Util.fillSourceRoots(this.projectPath, compileSourceRoots, testCompileSourceRoots);
        } else {
            for (String module : modules) {
                Util.fillSourceRoots(this.projectPath + "/" + module, compileSourceRoots, testCompileSourceRoots);
            }
        }

        metricsCalculator.setCompileSourceRoots(compileSourceRoots);
        metricsCalculator.setTestCompileSourceRoots(testCompileSourceRoots);
    }

}
