// Sets the container locations for applications that Jenkins relies on
// See http://javadoc.jenkins-ci.org/ for more details.
// Some more examples at https://groups.google.com/forum/#!topic/jenkinsci-users/U9HLBVB5_CM
import jenkins.*
import jenkins.model.*
import hudson.*
import hudson.model.*

// Add in maven configuration
mvn=Jenkins.instance.getExtensionList(hudson.tasks.Maven.DescriptorImpl.class)[0];
mvnList=(mvn.installations as List);
if ( mvnList.size() == 0 ) {
  mvnList.add(new hudson.tasks.Maven.MavenInstallation("mvn", "/usr/share/maven", []));
  mvn.installations=mvnList
  mvn.save()
  println("Added Maven Installation to configuration")
}

// Set the java home
jdk=Jenkins.instance.getExtensionList(hudson.model.JDK.DescriptorImpl.class)[0];
jdkList=(jdk.getInstallations() as List);
if ( jdkList.size() == 0 ) {
  jdkList.add(new hudson.model.JDK("jdk8", "/usr/lib/jvm/java-8-openjdk-amd64", []));
  jdk.installations=jdkList
  jdk.save()
  println("Added JDK Installation to configuration")
}
