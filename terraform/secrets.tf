# AWS Secrets Manager - Database Credentials
resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "${var.project_name}-db-credentials"
  description = "PostgreSQL database credentials"

  tags = {
    Name = "${var.project_name}-db-credentials"
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username     = var.db_username
    password     = var.db_password
    host         = aws_db_instance.postgresql.address
    port         = aws_db_instance.postgresql.port
    database     = var.db_name
    DATABASE_URL = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgresql.address}:${aws_db_instance.postgresql.port}/${var.db_name}"
  })
}

# AWS Secrets Manager - Google API Key
resource "aws_secretsmanager_secret" "google_api_key" {
  name        = "${var.project_name}-google-api-key"
  description = "Google Gemini API key for AI message generation"

  tags = {
    Name = "${var.project_name}-google-api-key"
  }
}

resource "aws_secretsmanager_secret_version" "google_api_key" {
  secret_id     = aws_secretsmanager_secret.google_api_key.id
  secret_string = var.google_api_key
}

# AWS Secrets Manager - Firebase Service Account Key
resource "aws_secretsmanager_secret" "firebase_key" {
  name        = "${var.project_name}-firebase-key"
  description = "Firebase service account key for push notifications"

  tags = {
    Name = "${var.project_name}-firebase-key"
  }
}

resource "aws_secretsmanager_secret_version" "firebase_key" {
  secret_id     = aws_secretsmanager_secret.firebase_key.id
  secret_string = var.firebase_service_account_key
}
