pipeline {
  agent any
  environment {
    STORAGE_ACCOUNT_KEY = credentials('STORAGE_ACCOUNT_KEY') // ID of Jenkins credential
  }
  stages {
    stage('Collect Azure Data') {
      steps { sh 'python3 scripts/collector.py' }
    }
    stage('Analyze Drift') {
      steps { sh 'python3 scripts/analyze_drift.py' }
    }
    stage('Generate Remediation') {
      steps { sh 'python3 scripts/generate_remediation.py' }
    }
    stage('Build Graph') {
      steps { sh 'python3 scripts/build_graph.py' }
    }
    stage('Upload Reports') {
      steps { sh '''
      bash scripts/upload_to_blob.sh "$STORAGE_ACCOUNT_KEY"
      az ad user list
      }
    }
  }
}
