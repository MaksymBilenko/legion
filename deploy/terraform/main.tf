terraform {
  backend "s3" {
    bucket = "legion-ci-configuration"
    key    = "terraform/state"
    region = "eu-central-1"
  }
}

variable "AWS_INSTANCE_TYPE" {}
variable "INSTANCE_NAME" {}
variable "ENV_NAME" {}
variable "AWS_REGION" {}
variable "AWS_SECURITY_GROUPS" {}
variable "AWS_IMAGE" {}
variable "AWS_KEY_NAME" {}
variable "AWS_SUBNET_ID" {}
variable "AWS_VOLUME_SIZE" {}
variable "WORKER_ASG_MAX_SIZE" {}
variable "WORKER_ASG_MIN_SIZE" {}
variable "WORKER_ASG_DESIRED_CAPACITY" {}
variable "WORKER_ASG_HC_GRACE_PERIOD" {}
variable "WORKER_ASG_HC_TYPE" {}

provider "aws" {
    region = "${var.AWS_REGION}"
}

# k8s master node
resource "aws_instance" "legion-k8s-master" {

    root_block_device {
        volume_type = "standard"
        volume_size = "${var.AWS_VOLUME_SIZE}"
    }

    volume_tags {
        Name = "${var.INSTANCE_NAME}-volume"
    }

    ami = "${var.AWS_IMAGE}"
    instance_type = "${var.AWS_INSTANCE_TYPE}"

    tags {
        Name = "${var.INSTANCE_NAME}"
    }

    subnet_id = "${var.AWS_SUBNET_ID}"
    vpc_security_group_ids = ["${split(",", var.AWS_SECURITY_GROUPS)}"]
    associate_public_ip_address = true

    key_name = "${var.AWS_KEY_NAME}"
}


resource "aws_eip" "legion-k8s-master-ip" {
    vpc = true
    instance = "${aws_instance.legion-k8s-master.id}"
}


# k8s worker node ASG

resource "aws_launch_configuration" "legion-k8s-workers-lc" {
  name            = "${var.ENV_NAME}-k8s-workers-lc"
  image_id        = "${var.AWS_IMAGE}"
  instance_type   = "${var.AWS_INSTANCE_TYPE}"
  security_groups = ["${split(",", var.AWS_SECURITY_GROUPS)}"]
  key_name        = "${var.AWS_KEY_NAME}"
  user_data       = "${data.template_file.user_data_shell.rendered}"
}

data "template_file" "user_data_shell" {
  template = <<-EOF
              #!/bin/bash
              echo "${var.ENV_NAME}" > /opt/k8s/env_name
              EOF
}

resource "aws_autoscaling_group" "legion-k8s-workers-asg" {
  name                      = "${var.ENV_NAME}-k8s-workers-asg"
  max_size                  = "${var.WORKER_ASG_MAX_SIZE}"
  min_size                  = "${var.WORKER_ASG_MIN_SIZE}"
  health_check_grace_period = "${var.WORKER_ASG_HC_GRACE_PERIOD}"
  health_check_type         = "${var.WORKER_ASG_HC_TYPE}"
  desired_capacity          = "${var.WORKER_ASG_DESIRED_CAPACITY}"
  launch_configuration      = "${aws_launch_configuration.legion-k8s-workers-lc.name}"
  tags {
    Name          = "${var.ENV_NAME}-k8s-worker"
    EnvName       = "${var.ENV_NAME}"
  }
}

output "public_ip" {
  value = "${aws_eip.legion-k8s-master-ip.public_ip}"
}

output "private_ip" {
  value = "${aws_instance.legion-k8s-master.private_ip}"
}

