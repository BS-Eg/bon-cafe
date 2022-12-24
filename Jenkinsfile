def win32BuildBadge = addEmbeddableBadgeConfiguration(id: "win32build", subject: "Windows Build")

def RunBuild() {
    echo 'Sleeping instead of running the build'
    sleep 10
}
pipeline {
    agent any 
    stages {
        stage('Push') {
            steps {
                echo 'connect to remote host'
                echo 'pull down the latest version'
                sh 'sudo ssh -i ~/ssh-keys/SSH/global-new.pem root@demo15.globalsolutions.dev sudo ./pull-git.sh'
            }
        }
        stage('Check website is up') {
            steps {
                echo 'Check website is up'
                sh 'curl -Is demo15.globalsolutions.dev | head -n 1'
            }
        }
        stage('Building') {
            steps {
                script {
                    win32BuildBadge.setStatus('running')
                    try {
                        RunBuild()
                        win32BuildBadge.setStatus('passing')
                    } catch (Exception err) {
                        win32BuildBadge.setStatus('failing')

                        /* Note: If you do not set the color
                                 the configuration uses the best status-matching color.
                                 passing -> brightgreen
                                 failing -> red
                                 ...
                        */
                        win32BuildBadge.setColor('pink')
                        error 'Build failed'
                    }
                }
            }
        }
    }
}
