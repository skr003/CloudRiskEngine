pipeline {
    agent any

    environment {
        OUTPUT_DIR = "output"
    }

    stages {
        stage('Initialize') {
            steps {
                sh '''
                mkdir -p $OUTPUT_DIR
                echo "[*] Workspace initialized."
                '''
            }
        }

        stage('Query Azure Infra State') {
            steps {
                script {
                withCredentials([
                    string(credentialsId: 'AZURE_CLIENT_ID', variable: 'AZURE_CLIENT_ID'),
                    string(credentialsId: 'AZURE_CLIENT_SECRET', variable: 'AZURE_CLIENT_SECRET'),
                    string(credentialsId: 'AZURE_TENANT_ID', variable: 'AZURE_TENANT_ID'),
                    string(credentialsId: 'AZURE_SUBSCRIPTION_ID', variable: 'AZURE_SUBSCRIPTION_ID')
                ]) {
                    sh 'az login --service-principal --username "$AZURE_CLIENT_ID" --password "$AZURE_CLIENT_SECRET" --tenant "$AZURE_TENANT_ID"'
                    sh 'az account set --subscription "$AZURE_SUBSCRIPTION_ID"'
                }       
                    sh './scripts/collect_iam_data.sh'
                }
                }
            }
        
        stage('Build Privilege Graph') {
            steps {
                sh '''
                bash scripts/build_graph.sh
                '''
            }
        }

        stage('Risk Analysis & Scoring') {
            steps {
                sh '''
                bash scripts/risk_analysis.sh
                '''
            }
        }

        stage('Threat Intelligence Mapping') {
            steps {
                sh '''
                bash scripts/map_mitre.sh
                '''
            }
        }

        stage('Export Dashboard Data') {
            steps {
                sh '''
                bash scripts/export_dashboard.sh
                '''
            }
        }

        stage('Generate Remediation Script') {
            steps {
                sh '''
                bash scripts/remediate.sh
                '''
            }
        }

        stage('Post-Check: Auto-Remediation Approval') {
            steps {
                script {
                    def risky = sh(script: "grep -c 'Owner\\|Contributor' output/risk_scores.csv || true", returnStdout: true).trim()
                    if (risky != "0") {
                        echo "⚠️ Risky assignments found. Approving auto-remediation..."
                        sh "bash output/remediation.sh"
                    } else {
                        echo "✅ No risky assignments found. Skipping remediation."
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'output/**/*', fingerprint: true
        }
    }
}
