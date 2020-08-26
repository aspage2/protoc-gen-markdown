import com.mintel.jenkins.artifacts.*
@Library("everest-shared@master") _
node("docker&&virtualenv") {
    properties([
        buildDiscarder(
            logRotator(
                artifactDaysToKeepStr: "14",
                artifactNumToKeepStr: "30",
                daysToKeepStr: "14",
                numToKeepStr: "30"
            )
        ),
        [$class: "JobRestrictionProperty"],
        gitLabConnection("Gitlab"),
    ])

    // Set job timeout.
    gitlabCommitStatus("jenkins-pipeline"){
        timeout(time: 2, unit: "HOURS") {
            com.mintel.jenkins.EverestPipeline.builder(this)
                .withFlowdockNotification("bac6aea4efa3cbee8a7e7169a8a800ab")
                .with(PythonPackage)
                .build()
                .execute()
        }
    }
}
