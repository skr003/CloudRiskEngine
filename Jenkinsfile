pipeline {
    agent any

    environment {
        // Credentials binding for Neo4j Password
        NEO4J_PASSWORD = credentials('neo4j-db-password') 
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Cloud Data Collector') {
            steps {
                script {
                    echo "Running Collector Module..."
                    sh 'bash scripts/collect_iam_data.sh'
                }
            }
        }

        stage('Privilege Analysis (Graph Build)') {
            steps {
                script {
                    echo "Building Neo4j Graph..."
                    sh 'bash scripts/build_graph.sh'
                }
            }
        }

        stage('Threat Intel Mapping') {
            steps {
                script {
                    echo "Mapping MITRE TTPs..."
                    sh 'python3 scripts/map_mitre.py'
                    
                    echo "Importing TTPs to Graph..."
                    sh 'bash scripts/import_mitre.sh'
                }
            }
        }

        stage('Remediation & Reporting') {
            steps {
                script {
                    echo "Generating Remediation Plans..."
                    sh 'python3 scripts/remediation.py'
                }
            }
        }
        
        stage('Deploy Dashboard') {
            steps {
                // In a real env, you might deploy this to a container
                // Here we just print instructions
                echo "Dashboard is ready. Run: streamlit run dashboard/app.py"
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'output/**/*', allowEmptyArchive: true
            cleanWs()
        }
    }
}
