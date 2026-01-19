pipeline {
    agent any

    environment {
        // Credentials binding for Neo4j Password
        NEO4J_PASSWORD = credentials('neo4j-db-password') 
        // Azure Credentials (Service Principal)
        AZURE_CREDENTIALS = credentials('azure-sp-credentials')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt'
                // Ensure jq and azure-cli are installed on the agent
            }
        }

        stage('Cloud Data Collector') {
            steps {
                script {
                    echo "Logging into Azure..."
                    // Assuming credential binding provides vars or use 'az login' manually
                    sh 'az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID'
                    
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
