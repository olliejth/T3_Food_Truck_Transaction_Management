# Describes all the variables sensitive and otherwaise that our terraform needs

# Variabke block
variable "AWS_REGION" {
    type = string
    default = "eu-west-2"
}

variable AWS_ACCESS_KEY {
    type = string
}

variable AWS_PRIVATE_ACCESS_KEY {
    type = string
}

variable IAM_ROLE {
    type = string
}

variable BUCKET_NAME {
    type = string
}

variable DB_HOST {
    type = string
}

variable DB_PORT {
    type = string
}

variable DB_NAME {
    type = string
}

variable DB_USER {
    type = string
}

variable DB_PASSWORD {
    type = string
}

variable DB_SCHEMA {
    type = string
}

variable DATA_FILEPATH {
    type = string
}

variable MERGED_FILE {
    type = string
}

variable CLEAN_FILE {
    type = string
}

variable INVALID_TOTALS {
    type = string
}
